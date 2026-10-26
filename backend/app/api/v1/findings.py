from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.finding import Finding
from app.models.document import Document
from app.schemas.finding import FindingResponse, FindingStatusUpdate
from app.core.dependencies import get_current_user, get_user_project
from app.ai.llm_client import llm_client

router = APIRouter(tags=["Findings"])

def enrich_finding_response(f: Finding, db: Session) -> FindingResponse:
    doc_name = None
    if f.document_id:
        doc = db.query(Document).filter(Document.id == f.document_id).first()
        if doc:
            doc_name = doc.filename
    resp = FindingResponse.model_validate(f)
    resp.document_name = doc_name
    return resp

@router.get("/projects/{project_id}/findings", response_model=List[FindingResponse])
def list_findings(
    project_id: str,
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    query = db.query(Finding).filter(Finding.project_id == project.id)
    
    if severity:
        query = query.filter(Finding.severity == severity.lower())
    if category:
        query = query.filter(Finding.category == category)
    if status:
        query = query.filter(Finding.status == status.lower())
    if document_id:
        query = query.filter(Finding.document_id == document_id)

    findings = query.order_by(desc(Finding.created_at)).all()
    return [enrich_finding_response(f, db) for f in findings]

@router.patch("/findings/{finding_id}", response_model=FindingResponse)
def update_finding_status(
    finding_id: str,
    update_data: FindingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    project = db.query(Project).filter(Project.id == finding.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    new_status = update_data.status.lower()
    if new_status not in ["open", "in_review", "resolved", "dismissed"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    finding.status = new_status
    if update_data.resolution_notes is not None:
        finding.resolution_notes = update_data.resolution_notes
        
    if new_status in ["resolved", "dismissed"]:
        finding.resolved_at = datetime.now(timezone.utc)
    else:
        finding.resolved_at = None

    db.commit()
    db.refresh(finding)
    return enrich_finding_response(finding, db)

@router.post("/findings/{finding_id}/ai_advice", response_model=FindingResponse)
async def generate_ai_advice_for_finding(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    project = db.query(Project).filter(Project.id == finding.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    advice = await llm_client.explain_finding(finding.title, finding.explanation, finding.rule_reference)
    if advice:
        finding.recommended_action = advice.recommended_action
        finding.explanation = f"{finding.explanation}\n\nAI Analysis: {advice.explanation}"
        db.commit()
        db.refresh(finding)
    else:
        # Deterministic advisory guidance if local LLM service is offline
        advisory_note = (
            "\n\nAI Advisory Note: Verify this item with your project drafter, architect, or contractor. "
            "Ensure that title blocks, dimension schedules, and application forms reflect consistent values across all submitted sheets."
        )
        if "AI Advisory Note:" not in finding.explanation and "AI Analysis:" not in finding.explanation:
            finding.explanation = f"{finding.explanation}{advisory_note}"
            db.commit()
            db.refresh(finding)

    return enrich_finding_response(finding, db)
