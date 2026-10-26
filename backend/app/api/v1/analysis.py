import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.analysis import AnalysisJob
from app.schemas.analysis import AnalysisJobResponse
from app.core.dependencies import get_current_user, get_user_project
from app.services.analysis_service import execute_project_analysis

router = APIRouter(tags=["Analysis"])

def run_analysis_task(job_id: str):
    db = SessionLocal()
    try:
        asyncio.run(execute_project_analysis(job_id, db))
    finally:
        db.close()

@router.post("/projects/{project_id}/analysis", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_project_analysis(
    background_tasks: BackgroundTasks,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    # Create AnalysisJob record
    job = AnalysisJob(
        project_id=project.id,
        status="pending",
        current_step="Initializing Pipeline",
        current_step_number=1,
        total_steps=9,
        progress_percentage=5.0,
        logs=[{
            "timestamp": "now",
            "step": "Initializing Pipeline",
            "message": "Analysis job queued for processing.",
            "level": "info"
        }]
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Trigger execution in background task
    background_tasks.add_task(run_analysis_task, job.id)

    return AnalysisJobResponse.model_validate(job)

@router.get("/analysis/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    project = db.query(Project).filter(Project.id == job.project_id).first()
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    return AnalysisJobResponse.model_validate(job)

@router.get("/projects/{project_id}/analysis/history", response_model=List[AnalysisJobResponse])
def get_project_analysis_history(
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    jobs = db.query(AnalysisJob).filter(
        AnalysisJob.project_id == project.id
    ).order_by(desc(AnalysisJob.started_at)).limit(10).all()
    return [AnalysisJobResponse.model_validate(j) for j in jobs]
