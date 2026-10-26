from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class FindingEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: Optional[int] = None
    snippet_text: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None

class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    rule_code: Optional[str] = None
    title: str
    category: str
    severity: str
    status: str
    explanation: str
    page_number: Optional[int] = None
    evidence_text: Optional[str] = None
    rule_reference: Optional[str] = None
    recommended_action: Optional[str] = None
    confidence: float
    human_review_required: bool
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    evidence_items: Optional[List[FindingEvidenceResponse]] = []

class FindingStatusUpdate(BaseModel):
    status: str  # open, in_review, resolved, dismissed
    resolution_notes: Optional[str] = None
