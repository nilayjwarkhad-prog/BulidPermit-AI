from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    report_number: str
    file_path: str
    file_size: int
    summary_data: Optional[Dict[str, Any]] = None
    created_at: datetime
