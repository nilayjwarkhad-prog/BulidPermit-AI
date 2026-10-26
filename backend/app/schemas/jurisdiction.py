from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class JurisdictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: str
    state_region: str
    city: str
    authority_name: str
    is_supported: bool
    is_sample_ruleset: bool
    notes: Optional[str] = None

class RuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    jurisdiction_id: str
    rule_code: str
    category: str
    title: str
    description: str
    source_url: Optional[str] = None
    effective_date: Optional[str] = None
    severity: str
    human_review_required: bool
    is_sample: bool
