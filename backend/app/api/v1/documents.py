import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.document import Document, DocumentVersion
from app.models.extraction import DocumentExtraction
from app.schemas.document import DocumentResponse, DocumentCategoryUpdate
from app.core.dependencies import get_current_user, get_user_project
from app.document_processing.file_validation import validate_uploaded_file
from app.document_processing.pdf_loader import extract_document_content, render_page_preview, EncryptedPDFError, CorruptPDFError
from app.document_processing.document_classifier import classify_document
from app.document_processing.field_extractor import extract_fields_from_document

router = APIRouter(tags=["Documents"])

def enrich_document_response(doc: Document, db: Session) -> DocumentResponse:
    ext = db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()
    fields = ext.extracted_fields if ext else None
    previews = ext.preview_images if ext else []
    
    resp = DocumentResponse.model_validate(doc)
    resp.extracted_fields = fields
    resp.preview_pages = previews
    return resp

@router.post("/projects/{project_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    category: str = Form(default="Other Supporting Document"),
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    # Read bytes safely
    file_bytes = await file.read()
    filename = file.filename or "uploaded_document.pdf"
    
    # Security & content validation
    is_valid, detected_mime, err_msg = validate_uploaded_file(
        file_bytes, filename, max_size_bytes=settings.MAX_UPLOAD_SIZE_BYTES
    )
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    doc_id = str(uuid.uuid4())
    _, ext = os.path.splitext(filename)
    safe_filename = f"{doc_id}{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Initial extraction to count pages and classify
    try:
        content = extract_document_content(save_path, detected_mime)
        page_count = content.get("page_count", 1)
        if page_count > settings.MAX_PAGES_PER_DOCUMENT:
            os.remove(save_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document exceeds maximum page limit ({settings.MAX_PAGES_PER_DOCUMENT} pages)"
            )
        
        full_text = content.get("full_text", "")
        pages_data = content.get("pages", [])
        
        # Classification
        classification = classify_document(full_text, filename)
        suggested_cat = classification["category"]
        confidence = classification["confidence"]

        # Use category if explicitly provided, else suggested
        assigned_cat = category if category != "Other Supporting Document" else suggested_cat

        # Field extraction
        extracted_fields = extract_fields_from_document(assigned_cat, full_text, pages_data)

        # Pre-render page 1 preview
        prev_fn = f"prev_{doc_id}_p1.png"
        prev_path = os.path.join(settings.PREVIEWS_DIR, prev_fn)
        render_page_preview(save_path, 1, prev_path, detected_mime)

    except EncryptedPDFError as epfe:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(epfe))
    except CorruptPDFError as cpfe:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(cpfe))
    except HTTPException:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        raise
    except Exception as e:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to process document: {str(e)}")

    doc = Document(
        id=doc_id,
        project_id=project.id,
        filename=filename,
        original_filename=filename,
        file_path=save_path,
        file_size=len(file_bytes),
        mime_type=detected_mime,
        page_count=page_count,
        category=assigned_cat,
        suggested_category=suggested_cat,
        category_confidence=confidence,
        manual_category_override=(category != "Other Supporting Document"),
        status="uploaded",
        version=1,
        is_active=True
    )
    db.add(doc)
    db.commit()

    # Create extraction entry
    extraction = DocumentExtraction(
        document_id=doc.id,
        raw_text=full_text,
        page_extractions=pages_data,
        extracted_fields=extracted_fields,
        preview_images=[prev_fn],
        layout_metadata={"engine": content.get("engine", "pypdf"), "is_scanned": content.get("is_scanned", False)}
    )
    db.add(extraction)

    # Create first version record
    v1 = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        file_path=save_path,
        file_size=len(file_bytes),
        change_summary="Initial upload"
    )
    db.add(v1)
    db.commit()
    db.refresh(doc)

    return enrich_document_response(doc, db)

@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
def list_project_documents(project: Project = Depends(get_user_project), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(
        Document.project_id == project.id,
        Document.is_active == True
    ).order_by(desc(Document.created_at)).all()
    return [enrich_document_response(d, db) for d in docs]

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    return enrich_document_response(doc, db)

@router.patch("/documents/{document_id}/category", response_model=DocumentResponse)
def update_document_category(
    document_id: str,
    update_data: DocumentCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    doc.category = update_data.category
    doc.manual_category_override = True
    db.commit()
    db.refresh(doc)
    return enrich_document_response(doc, db)

@router.get("/documents/{document_id}/preview/{page_number}")
def get_document_page_preview(
    document_id: str,
    page_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    preview_path = os.path.join(settings.PREVIEWS_DIR, f"prev_{doc.id}_p{page_number}.png")
    if not os.path.exists(preview_path):
        # Render on demand
        success = render_page_preview(doc.file_path, page_number, preview_path, doc.mime_type)
        if not success or not os.path.exists(preview_path):
            raise HTTPException(status_code=404, detail="Preview not available for this page")

    return FileResponse(preview_path, media_type="image/png")

@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.is_active == True).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File content missing on storage")

    return FileResponse(
        doc.file_path,
        media_type=doc.mime_type,
        filename=doc.original_filename
    )

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    doc.is_active = False
    db.commit()
    return None

@router.post("/projects/{project_id}/seed_sample_documents", response_model=List[DocumentResponse])
def seed_sample_documents_to_project(
    include_inconsistency: bool = True,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Seeds realistic sample PDF documents (Permit App, Site Plan, Floor Plan, and optional Inconsistent Doc)
    into the project for instant testing of the pre-check pipeline.
    """
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "sample_documents"))
    if not os.path.exists(sample_dir):
        raise HTTPException(status_code=404, detail="Sample documents directory not found")

    files_to_seed = [
        ("Sample_Permit_Application.pdf", "Permit Application"),
        ("Sample_Site_Plan.pdf", "Site Plan"),
        ("Sample_Floor_Plan.pdf", "Floor Plan")
    ]
    if include_inconsistency:
        files_to_seed.append(("Sample_Inconsistent_Document.pdf", "Structural Plans"))

    created_docs = []
    for fn, assigned_cat in files_to_seed:
        src_path = os.path.join(sample_dir, fn)
        if not os.path.exists(src_path):
            continue

        doc_id = str(uuid.uuid4())
        dest_filename = f"{doc_id}.pdf"
        dest_path = os.path.join(settings.UPLOAD_DIR, dest_filename)
        shutil.copyfile(src_path, dest_path)
        file_size = os.path.getsize(dest_path)

        content = extract_document_content(dest_path, "application/pdf")
        full_text = content.get("full_text", "")
        pages_data = content.get("pages", [])
        page_count = content.get("page_count", 1)

        extracted_fields = extract_fields_from_document(assigned_cat, full_text, pages_data)

        # Render preview
        prev_fn = f"prev_{doc_id}_p1.png"
        prev_path = os.path.join(settings.PREVIEWS_DIR, prev_fn)
        render_page_preview(dest_path, 1, prev_path, "application/pdf")

        doc = Document(
            id=doc_id,
            project_id=project.id,
            filename=fn,
            original_filename=fn,
            file_path=dest_path,
            file_size=file_size,
            mime_type="application/pdf",
            page_count=page_count,
            category=assigned_cat,
            suggested_category=assigned_cat,
            category_confidence=0.96,
            manual_category_override=True,
            status="uploaded",
            version=1,
            is_active=True
        )
        db.add(doc)
        db.commit()

        ext = DocumentExtraction(
            document_id=doc.id,
            raw_text=full_text,
            page_extractions=pages_data,
            extracted_fields=extracted_fields,
            preview_images=[prev_fn],
            layout_metadata={"engine": "pypdf", "is_scanned": False}
        )
        db.add(ext)

        v1 = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            file_path=dest_path,
            file_size=file_size,
            change_summary="Sample document loaded"
        )
        db.add(v1)
        db.commit()
        db.refresh(doc)
        created_docs.append(enrich_document_response(doc, db))

    return created_docs
