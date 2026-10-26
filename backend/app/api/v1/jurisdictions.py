from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.project import Project
from app.schemas.jurisdiction import JurisdictionResponse, RuleResponse
from app.compliance.source_registry import SUPPORTED_JURISDICTIONS, SAMPLE_RULES
from app.core.dependencies import get_user_project

router = APIRouter(tags=["Jurisdictions & Regulations"])

@router.get("/jurisdictions", response_model=List[JurisdictionResponse])
def get_jurisdictions():
    return [JurisdictionResponse(**j) for j in SUPPORTED_JURISDICTIONS]

@router.get("/jurisdictions/{jurisdiction_id}/rules", response_model=List[RuleResponse])
def get_jurisdiction_rules(jurisdiction_id: str):
    matched = [r for r in SAMPLE_RULES if r.get("jurisdiction_id") in (jurisdiction_id, "US-CA-GENERIC")]
    rules_resp = []
    for idx, r in enumerate(matched):
        rules_resp.append(RuleResponse(
            id=f"rule-{idx+1}",
            jurisdiction_id=r.get("jurisdiction_id", "US-CA-GENERIC"),
            rule_code=r["rule_code"],
            category=r["category"],
            title=r["title"],
            description=r["description"],
            source_url=r.get("source_url"),
            effective_date=r.get("effective_date"),
            severity=r.get("severity", "warning"),
            human_review_required=r.get("human_review_required", False),
            is_sample=True
        ))
    return rules_resp
