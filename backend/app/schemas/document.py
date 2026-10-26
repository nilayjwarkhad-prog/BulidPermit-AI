from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    page_count: int
    category: str
    suggested_category: Optional[str] = None
    category_confidence: Optional[float] = None
    manual_category_override: bool
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    extracted_fields: Optional[Dict[str, Any]] = None
    preview_pages: Optional[List[str]] = None

class DocumentCategoryUpdate(BaseModel):
    category: str

class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    file_size: int
    change_summary: Optional[str] = None
    created_at: datetime
