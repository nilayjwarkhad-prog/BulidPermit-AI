import os
import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.finding import Finding
from app.models.checklist import Checklist, ChecklistItem
from app.models.report import Report
from app.schemas.report import ReportResponse
from app.core.dependencies import get_current_user, get_user_project
from app.reports.pdf_generator import generate_pdf_report

router = APIRouter(tags=["Reports"])

@router.post("/projects/{project_id}/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_project_report(
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    report_id = str(uuid.uuid4())
    report_num = f"BPAI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{report_id[:8].upper()}"
    out_filename = f"report_{report_num}.pdf"
    out_path = os.path.join(settings.REPORTS_DIR, out_filename)

    # Gather data
    docs = db.query(Document).filter(Document.project_id == project.id, Document.is_active == True).all()
    findings = db.query(Finding).filter(Finding.project_id == project.id).all()
    
    chk = db.query(Checklist).filter(Checklist.project_id == project.id).first()
    chk_items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).all() if chk else []

    proj_dict = {
        "id": project.id,
        "name": project.name,
        "address": project.address,
        "city": project.city,
        "state_region": project.state_region,
        "country": project.country,
        "jurisdiction_id": project.jurisdiction_id,
        "project_type": project.project_type,
        "building_type": project.building_type,
        "num_floors": project.num_floors,
        "area": project.area,
        "area_unit": project.area_unit
    }

    doc_dicts = [{
        "filename": d.filename,
        "category": d.category,
        "page_count": d.page_count,
        "category_confidence": d.category_confidence
    } for d in docs]

    doc_id_name_map = {d.id: d.filename for d in docs}

    finding_dicts = [{
        "title": f.title,
        "explanation": f.explanation,
        "severity": f.severity,
        "status": f.status,
        "category": f.category,
        "document_name": doc_id_name_map.get(f.document_id),
        "page_number": f.page_number,
        "evidence_text": f.evidence_text,
        "rule_reference": f.rule_reference,
        "recommended_action": f.recommended_action
    } for f in findings]

    chk_dicts = [{
        "category": ci.category,
        "title": ci.title,
        "description": ci.description,
        "status": ci.status,
        "notes": ci.notes
    } for ci in chk_items]

    # Generate PDF
    success = generate_pdf_report(out_path, proj_dict, doc_dicts, finding_dicts, chk_dicts, report_num)
    if not success or not os.path.exists(out_path):
        raise HTTPException(status_code=500, detail="Failed to compile PDF report")

    file_size = os.path.getsize(out_path)

    report = Report(
        id=report_id,
        project_id=project.id,
        report_number=report_num,
        file_path=out_path,
        file_size=file_size,
        summary_data={
            "documents_count": len(docs),
            "findings_count": len(findings),
            "checklist_items_count": len(chk_items),
            "critical_count": sum(1 for f in findings if f.severity == "critical" and f.status in ("open", "in_review")),
            "warning_count": sum(1 for f in findings if f.severity == "warning" and f.status in ("open", "in_review"))
        }
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse.model_validate(report)

@router.get("/projects/{project_id}/reports", response_model=List[ReportResponse])
def list_project_reports(
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    reports = db.query(Report).filter(
        Report.project_id == project.id
    ).order_by(desc(Report.created_at)).all()
    return [ReportResponse.model_validate(r) for r in reports]

@router.get("/reports/{report_id}/download")
def download_report_pdf(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    project = db.query(Project).filter(Project.id == report.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report PDF file missing from storage")

    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"{report.report_number}.pdf"
    )
