import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(String(100), primary_key=True)  # e.g., US-CA-LOSANGELES, US-CA-GENERIC, EU-DE-BERLIN
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    state_region = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    authority_name = Column(String(255), nullable=False)
    is_supported = Column(Boolean, default=True, nullable=False)
    is_sample_ruleset = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

class RulesetVersion(Base):
    __tablename__ = "ruleset_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    jurisdiction_id = Column(String(100), nullable=False, index=True)
    version_tag = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    effective_date = Column(String(50), nullable=False)
    is_sample_rule = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

class RegulationRule(Base):
    __tablename__ = "regulation_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    jurisdiction_id = Column(String(100), nullable=False, index=True)
    rule_code = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    effective_date = Column(String(50), nullable=True)
    version = Column(String(50), default="1.0.0", nullable=False)
    
    applicability_conditions = Column(JSON, nullable=True)  # project_types, building_types
    required_fields = Column(JSON, nullable=True)           # list of fields required
    validation_logic = Column(JSON, nullable=True)          # rules e.g. min_setback_front, max_height
    severity = Column(String(50), default="warning", nullable=False)
    human_review_required = Column(Boolean, default=False, nullable=False)
    is_sample = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
