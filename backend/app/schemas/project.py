from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    country: str = "United States"
    state_region: str
    city: str
    address: str
    project_type: str = "Residential Addition"
    building_type: str = "Single Family Residence"
    num_floors: int = Field(default=1, ge=1, le=10)
    area: Optional[float] = Field(default=None, ge=0)
    area_unit: str = "sq_ft"  # sq_ft, sq_m
    stage: str = "Pre-Submission Preparation"
    jurisdiction_id: str = "US-CA-GENERIC"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    project_type: Optional[str] = None
    building_type: Optional[str] = None
    num_floors: Optional[int] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    stage: Optional[str] = None
    jurisdiction_id: Optional[str] = None

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    country: str
    state_region: str
    city: str
    address: str
    project_type: str
    building_type: str
    num_floors: int
    area: Optional[float] = None
    area_unit: str
    stage: str
    jurisdiction_id: str
    jurisdiction_supported: str
    created_at: datetime
    updated_at: datetime
    
    # Computed metrics
    document_count: Optional[int] = 0
    open_findings_count: Optional[int] = 0
    checklist_completion_percent: Optional[float] = 0.0
    latest_job_status: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    total_projects: int
    documents_awaiting_review: int
    issues_requiring_attention: int
    completed_reviews: int
    recent_projects: List[ProjectResponse]
    recent_jobs: List[dict]
