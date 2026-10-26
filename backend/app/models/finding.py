import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    rule_code = Column(String(100), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Missing Document, Missing Field, Inconsistency, Rule Violation, Page Quality
    severity = Column(String(50), default="warning", nullable=False)  # critical, warning, info
    status = Column(String(50), default="open", nullable=False)  # open, in_review, resolved, dismissed
    
    explanation = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    evidence_text = Column(Text, nullable=True)
    rule_reference = Column(String(255), nullable=True)
    recommended_action = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)
    human_review_required = Column(Boolean, default=False, nullable=False)
    
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="findings")
    document = relationship("Document", back_populates="findings")
    evidence_items = relationship("FindingEvidence", back_populates="finding", cascade="all, delete-orphan")

class FindingEvidence(Base):
    __tablename__ = "finding_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    page_number = Column(Integer, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # {x0, y0, x1, y1}
    snippet_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    finding = relationship("Finding", back_populates="evidence_items")
