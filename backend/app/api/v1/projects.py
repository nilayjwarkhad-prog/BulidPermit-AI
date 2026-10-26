from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.finding import Finding
from app.models.checklist import Checklist, ChecklistItem
from app.models.analysis import AnalysisJob
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, DashboardStatsResponse
from app.core.dependencies import get_current_user, get_user_project
from app.compliance.source_registry import SUPPORTED_JURISDICTIONS

router = APIRouter(tags=["Projects"])

def enrich_project_response(project: Project, db: Session) -> ProjectResponse:
    doc_count = db.query(Document).filter(Document.project_id == project.id, Document.is_active == True).count()
    open_findings = db.query(Finding).filter(Finding.project_id == project.id, Finding.status.in_(["open", "in_review"])).count()
    
    chk = db.query(Checklist).filter(Checklist.project_id == project.id).first()
    chk_pct = 0.0
    if chk:
        total = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id).count()
        completed = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == chk.id, ChecklistItem.status == "complete").count()
        if total > 0:
            chk_pct = round((completed / total) * 100.0, 1)

    latest_job = db.query(AnalysisJob).filter(AnalysisJob.project_id == project.id).order_by(desc(AnalysisJob.started_at)).first()
    latest_status = latest_job.status if latest_job else None

    resp = ProjectResponse.model_validate(project)
    resp.document_count = doc_count
    resp.open_findings_count = open_findings
    resp.checklist_completion_percent = chk_pct
    resp.latest_job_status = latest_status
    return resp

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(desc(Project.updated_at)).all()
    project_ids = [p.id for p in user_projects]

    total_projects = len(user_projects)
    docs_count = db.query(Document).filter(Document.project_id.in_(project_ids), Document.is_active == True).count() if project_ids else 0
    issues_count = db.query(Finding).filter(Finding.project_id.in_(project_ids), Finding.status.in_(["open", "in_review"])).count() if project_ids else 0
    
    recent_jobs = db.query(AnalysisJob).filter(AnalysisJob.project_id.in_(project_ids)).order_by(desc(AnalysisJob.started_at)).limit(5).all() if project_ids else []
    completed_reviews = db.query(AnalysisJob).filter(AnalysisJob.project_id.in_(project_ids), AnalysisJob.status == "completed").count() if project_ids else 0

    enriched_projects = [enrich_project_response(p, db) for p in user_projects[:5]]
    recent_job_dicts = [{
        "id": j.id,
        "project_id": j.project_id,
        "status": j.status,
        "current_step": j.current_step,
        "progress_percentage": j.progress_percentage,
        "started_at": j.started_at.isoformat() if j.started_at else None,
        "completed_at": j.completed_at.isoformat() if j.completed_at else None
    } for j in recent_jobs]

    return DashboardStatsResponse(
        total_projects=total_projects,
        documents_awaiting_review=docs_count,
        issues_requiring_attention=issues_count,
        completed_reviews=completed_reviews,
        recent_projects=enriched_projects,
        recent_jobs=recent_job_dicts
    )

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if jurisdiction is supported
    jurisdiction_info = next((j for j in SUPPORTED_JURISDICTIONS if j["id"] == project_in.jurisdiction_id), None)
    is_supported = "supported" if jurisdiction_info and jurisdiction_info.get("is_supported") else "unsupported"

    project = Project(
        user_id=current_user.id,
        name=project_in.name,
        description=project_in.description,
        country=project_in.country,
        state_region=project_in.state_region,
        city=project_in.city,
        address=project_in.address,
        project_type=project_in.project_type,
        building_type=project_in.building_type,
        num_floors=project_in.num_floors,
        area=project_in.area,
        area_unit=project_in.area_unit,
        stage=project_in.stage,
        jurisdiction_id=project_in.jurisdiction_id,
        jurisdiction_supported=is_supported
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Initialize empty checklist for project
    chk = Checklist(
        project_id=project.id,
        jurisdiction_id=project.jurisdiction_id,
        ruleset_version="1.0.0"
    )
    db.add(chk)
    db.commit()

    return enrich_project_response(project, db)

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(desc(Project.updated_at)).all()
    return [enrich_project_response(p, db) for p in projects]

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project: Project = Depends(get_user_project), db: Session = Depends(get_db)):
    return enrich_project_response(project, db)

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_update: ProjectUpdate, project: Project = Depends(get_user_project), db: Session = Depends(get_db)):
    update_data = project_update.model_dump(exclude_unset=True)
    if "jurisdiction_id" in update_data:
        j_info = next((j for j in SUPPORTED_JURISDICTIONS if j["id"] == update_data["jurisdiction_id"]), None)
        project.jurisdiction_supported = "supported" if j_info and j_info.get("is_supported") else "unsupported"
        
    for field, val in update_data.items():
        setattr(project, field, val)
        
    db.commit()
    db.refresh(project)
    return enrich_project_response(project, db)

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: Project = Depends(get_user_project), db: Session = Depends(get_db)):
    db.delete(project)
    db.commit()
    return None
