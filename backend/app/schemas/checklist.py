from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    checklist_id: str
    category: str
    requirement_code: str
    title: str
    description: str
    status: str  # complete, missing, needs_verification, not_applicable, unsupported
    notes: Optional[str] = None
    evidence_document_id: Optional[str] = None
    evidence_document_name: Optional[str] = None
    evidence_page_number: Optional[int] = None
    rule_reference: Optional[str] = None
    document_references: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

class ChecklistItemUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    jurisdiction_id: str
    ruleset_version: str
    items: List[ChecklistItemResponse]
    completion_stats: dict
    created_at: datetime
    updated_at: datetime
