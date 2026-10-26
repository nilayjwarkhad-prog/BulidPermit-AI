from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class AnalysisLogEntry(BaseModel):
    timestamp: str
    step: str
    message: str
    level: str = "info"

class AnalysisJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    status: str
    current_step: str
    current_step_number: int
    total_steps: int
    progress_percentage: float
    logs: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
