import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    jurisdiction_id = Column(String(100), nullable=False)
    ruleset_version = Column(String(50), nullable=False, default="1.0.0")
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="checklists")
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    checklist_id = Column(String(36), ForeignKey("checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category = Column(String(100), nullable=False)  # Application Completeness, Site Requirements, Architectural Drawings, Structural & Life Safety, Zoning & Setbacks
    requirement_code = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Status: complete, missing, needs_verification, not_applicable, unsupported
    status = Column(String(50), default="missing", nullable=False)
    
    notes = Column(Text, nullable=True)
    evidence_document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    evidence_page_number = Column(Integer, nullable=True)
    rule_reference = Column(String(255), nullable=True)
    document_references = Column(JSON, default=list, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    checklist = relationship("Checklist", back_populates="items")
