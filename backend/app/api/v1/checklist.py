from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.checklist import Checklist, ChecklistItem
from app.models.document import Document
from app.schemas.checklist import ChecklistResponse, ChecklistItemResponse, ChecklistItemUpdate
from app.core.dependencies import get_current_user, get_user_project

router = APIRouter(tags=["Checklist"])

def enrich_checklist_item(item: ChecklistItem, db: Session) -> ChecklistItemResponse:
    doc_name = None
    if item.evidence_document_id:
        doc = db.query(Document).filter(Document.id == item.evidence_document_id).first()
        if doc:
            doc_name = doc.filename
    resp = ChecklistItemResponse.model_validate(item)
    resp.evidence_document_name = doc_name
    return resp

@router.get("/projects/{project_id}/checklist", response_model=ChecklistResponse)
def get_project_checklist(project: Project = Depends(get_user_project), db: Session = Depends(get_db)):
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

    items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all()
    enriched_items = [enrich_checklist_item(i, db) for i in items]

    total = len(enriched_items)
    complete = sum(1 for i in enriched_items if i.status == "complete")
    missing = sum(1 for i in enriched_items if i.status == "missing")
    needs_verif = sum(1 for i in enriched_items if i.status == "needs_verification")

    stats = {
        "total": total,
        "complete": complete,
        "missing": missing,
        "needs_verification": needs_verif,
        "percentage": round((complete / total * 100.0), 1) if total > 0 else 0.0
    }

    return ChecklistResponse(
        id=chk.id,
        project_id=chk.project_id,
        jurisdiction_id=chk.jurisdiction_id,
        ruleset_version=chk.ruleset_version,
        items=enriched_items,
        completion_stats=stats,
        created_at=chk.created_at,
        updated_at=chk.updated_at
    )

@router.patch("/checklist/items/{item_id}", response_model=ChecklistItemResponse)
def update_checklist_item(
    item_id: str,
    update_data: ChecklistItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    chk = db.query(Checklist).filter(Checklist.id == item.checklist_id).first()
    project = db.query(Project).filter(Project.id == chk.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    item.status = update_data.status
    if update_data.notes is not None:
        item.notes = update_data.notes

    db.commit()
    db.refresh(item)
    return enrich_checklist_item(item, db)
