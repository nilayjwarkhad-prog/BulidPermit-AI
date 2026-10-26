from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AIClassificationOutput(BaseModel):
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = []
    requires_human_confirmation: bool = False
    reasoning: Optional[str] = None

class AIExtractionExplanation(BaseModel):
    summary: str
    key_findings: List[str] = []
    potential_issues: List[str] = []
    suggested_corrections: List[str] = []

class AIFindingRecommendation(BaseModel):
    explanation: str
    recommended_action: str
    severity: str  # critical, warning, info
    confidence: float = 0.85
