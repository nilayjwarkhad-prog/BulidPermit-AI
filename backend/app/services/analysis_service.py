import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.config import settings
from app.core.logging import log_info, log_error
from app.models.project import Project
from app.models.document import Document
from app.models.extraction import DocumentExtraction
from app.models.analysis import AnalysisJob
from app.models.finding import Finding
from app.models.checklist import Checklist, ChecklistItem
from app.document_processing.pdf_loader import extract_document_content, render_page_preview
from app.document_processing.document_classifier import classify_document
from app.document_processing.field_extractor import extract_fields_from_document
from app.document_processing.docling_processor import docling_processor
from app.document_processing.ocr_processor import ocr_processor
from app.compliance.cross_document_checks import run_cross_document_checks
from app.compliance.rule_engine import evaluate_jurisdiction_rules
from app.compliance.checklist_engine import evaluate_checklist
from app.ai.llm_client import llm_client

PIPELINE_STEPS = [
    (1, "Validating Uploaded Files", 10.0),
    (2, "Extracting PDF Text & Page Geometry", 25.0),
    (3, "Rendering Page Previews & Layout Analysis", 40.0),
    (4, "Classifying Document Categories", 55.0),
    (5, "Extracting Structured Fields & Measurements", 70.0),
    (6, "Evaluating Pre-Submission Checklist", 80.0),
    (7, "Executing Cross-Document Consistency Checks", 90.0),
    (8, "Evaluating Jurisdiction Rules", 95.0),
    (9, "Pre-Check Compilation Ready", 100.0)
]

def append_job_log(job: AnalysisJob, step_num: int, message: str, level: str = "info"):
    now_iso = datetime.now(timezone.utc).isoformat()
    step_info = PIPELINE_STEPS[min(step_num - 1, len(PIPELINE_STEPS) - 1)]
    job.current_step_number = step_num
    job.current_step = step_info[1]
    job.progress_percentage = step_info[2]
    
    logs = list(job.logs or [])
    logs.append({
        "timestamp": now_iso,
        "step": step_info[1],
        "message": message,
        "level": level
    })
    job.logs = logs

async def execute_project_analysis(job_id: str, db: Session):
    """
    Executes the comprehensive 9-step permit pre-check pipeline.
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        log_error(f"Analysis job {job_id} not found")
        return

    try:
        job.status = "processing"
        db.commit()

        project = db.query(Project).filter(Project.id == job.project_id).first()
        if not project:
            raise ValueError("Target project does not exist")

        docs = db.query(Document).filter(Document.project_id == project.id, Document.is_active == True).all()

        # Step 1: Validate Files
        append_job_log(job, 1, f"Validating {len(docs)} uploaded project documents...")
        db.commit()
        for doc in docs:
            if not os.path.exists(doc.file_path):
                raise FileNotFoundError(f"File missing on disk: {doc.filename}")

        # Step 2: Text Extraction & Layout Analysis
        append_job_log(job, 2, "Extracting text content, tables, and page geometry...")
        db.commit()
        
        extracted_docs_data: List[Dict[str, Any]] = []

        for doc in docs:
            content = extract_document_content(doc.file_path, doc.mime_type)
            doc.page_count = content.get("page_count", 1)
            doc.status = "extracted"
            
            layout_meta = {
                "engine": content.get("engine", "pypdf"),
                "is_scanned": content.get("is_scanned", False),
                "ocr_applied": False
            }

            # Docling integration when available for deep layout/table parsing
            if docling_processor.is_available() and doc.mime_type == "application/pdf":
                docling_data = docling_processor.process_document(doc.file_path)
                if docling_data:
                    layout_meta["docling"] = docling_data
                    if not content.get("full_text") and docling_data.get("markdown"):
                        content["full_text"] = docling_data["markdown"]
            
            # OCR fallback for scanned plans or images with low text density
            if content.get("is_scanned") and not content.get("full_text"):
                append_job_log(job, 2, f"Scanned/blueprint image detected for {doc.filename}. Applying OCR fallback...", level="info")
                if doc.mime_type.startswith("image/"):
                    ocr_res = ocr_processor.process_scanned_image(doc.file_path)
                    layout_meta["ocr_result"] = ocr_res
                    layout_meta["ocr_applied"] = ocr_res.get("ocr_success", False)
                    if ocr_res.get("text"):
                        content["full_text"] = ocr_res["text"]
                        if content.get("pages"):
                            content["pages"][0]["text"] = ocr_res["text"]
                            content["pages"][0]["word_count"] = ocr_res.get("word_count", 0)

            # Check or create DocumentExtraction record
            ext = db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()
            if not ext:
                ext = DocumentExtraction(
                    document_id=doc.id,
                    raw_text=content.get("full_text", ""),
                    page_extractions=content.get("pages", []),
                    layout_metadata=layout_meta
                )
                db.add(ext)
            else:
                ext.raw_text = content.get("full_text", "")
                ext.page_extractions = content.get("pages", [])
                ext.layout_metadata = layout_meta
            
            db.commit()

        # Step 3: Render Previews
        append_job_log(job, 3, "Rendering high-resolution page previews for web viewer...")
        db.commit()
        for doc in docs:
            ext = db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()
            preview_filenames = []
            for p_num in range(1, min(doc.page_count + 1, 15)):  # render up to first 15 pages
                prev_fn = f"prev_{doc.id}_p{p_num}.png"
                out_path = os.path.join(settings.PREVIEWS_DIR, prev_fn)
                if not os.path.exists(out_path):
                    render_page_preview(doc.file_path, p_num, out_path, doc.mime_type)
                preview_filenames.append(prev_fn)
            if ext:
                ext.preview_images = preview_filenames
                db.commit()

        # Step 4: Classification
        append_job_log(job, 4, "Classifying document categories with keyword & AI heuristics...")
        db.commit()
        for doc in docs:
            ext = db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()
            raw_text = ext.raw_text if ext else ""
            
            rule_cls = classify_document(raw_text, doc.filename)
            
            # If user hasn't manually overridden, check LLM enhancement or apply rule classification
            if not doc.manual_category_override:
                assigned_category = rule_cls["category"]
                confidence = rule_cls["confidence"]
                
                # If rule confidence is moderate, check AI if enabled
                if rule_cls["requires_confirmation"] and settings.AI_ENABLED:
                    ai_cls = await llm_client.classify_document_text(raw_text[:1200], doc.filename)
                    if ai_cls and ai_cls.confidence > confidence:
                        assigned_category = ai_cls.category
                        confidence = ai_cls.confidence
                
                doc.category = assigned_category
                doc.suggested_category = assigned_category
                doc.category_confidence = confidence
                db.commit()

        # Step 5: Field Extraction
        append_job_log(job, 5, "Extracting structured building permit fields, dimensions, and setbacks...")
        db.commit()
        for doc in docs:
            ext = db.query(DocumentExtraction).filter(DocumentExtraction.document_id == doc.id).first()
            raw_text = ext.raw_text if ext else ""
            pages_data = ext.page_extractions if ext else []
            
            fields = extract_fields_from_document(doc.category, raw_text, pages_data)
            if ext:
                ext.extracted_fields = fields
                db.commit()

            extracted_docs_data.append({
                "id": doc.id,
                "filename": doc.filename,
                "category": doc.category,
                "page_count": doc.page_count,
                "mime_type": doc.mime_type,
                "extracted_fields": fields,
                "pages_data": pages_data,
                "category_confidence": doc.category_confidence
            })

        # Step 6: Checklist Verification
        append_job_log(job, 6, "Verifying submittal package against jurisdiction checklist...")
        db.commit()

        # Clear previous checklist items for project
        chk = db.query(Checklist).filter(Checklist.project_id == project.id).first()
        if not chk:
            chk = Checklist(
                project_id=project.id,
                jurisdiction_id=project.jurisdiction_id,
                ruleset_version="1.0.0"
            )
            db.add(chk)
            db.commit()
            db.refresh(chk)

        db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).delete()
        db.commit()

        # Step 7: Cross Document Consistency Checks
        append_job_log(job, 7, "Executing deterministic cross-document checks...")
        db.commit()

        project_dict = {
            "id": project.id,
            "name": project.name,
            "address": project.address,
            "city": project.city,
            "state_region": project.state_region,
            "project_type": project.project_type,
            "num_floors": project.num_floors,
            "area": project.area
        }

        cross_findings = run_cross_document_checks(project_dict, extracted_docs_data)

        # Step 8: Jurisdiction Rules
        append_job_log(job, 8, "Evaluating applicable zoning and building setback rules...")
        db.commit()

        rule_findings = evaluate_jurisdiction_rules(project_dict, extracted_docs_data, project.jurisdiction_id)

        all_findings_raw = cross_findings + rule_findings

        # Clear previous open findings (preserve resolved/dismissed)
        db.query(Finding).filter(Finding.project_id == project.id, Finding.status.in_(["open", "in_review"])).delete()
        db.commit()

        for f_data in all_findings_raw:
            f = Finding(
                project_id=project.id,
                document_id=f_data.get("document_id"),
                rule_code=f_data.get("rule_code"),
                title=f_data.get("title"),
                category=f_data.get("category"),
                severity=f_data.get("severity", "warning"),
                status="open",
                explanation=f_data.get("explanation"),
                page_number=f_data.get("page_number"),
                evidence_text=f_data.get("evidence_text"),
                rule_reference=f_data.get("rule_reference"),
                recommended_action=f_data.get("recommended_action"),
                confidence=f_data.get("confidence", 0.9),
                human_review_required=f_data.get("human_review_required", False)
            )
            db.add(f)
        db.commit()

        # Populate checklist
        evaluated_checklist_items = evaluate_checklist(project_dict, extracted_docs_data, all_findings_raw)
        for ci in evaluated_checklist_items:
            item = ChecklistItem(
                checklist_id=chk.id,
                category=ci["category"],
                requirement_code=ci["requirement_code"],
                title=ci["title"],
                description=ci["description"],
                status=ci["status"],
                notes=ci["notes"],
                evidence_document_id=ci.get("evidence_document_id"),
                evidence_page_number=ci.get("evidence_page_number"),
                rule_reference=ci.get("rule_reference")
            )
            db.add(item)
        db.commit()

        # Step 9: Finalize
        append_job_log(job, 9, f"Pre-check analysis complete. Identified {len(all_findings_raw)} findings across {len(docs)} documents.")
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        log_error(f"Analysis job {job_id} encountered fatal error: {e}")
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
