import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    country = Column(String(100), nullable=False, default="United States")
    state_region = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    
    project_type = Column(String(100), nullable=False, default="Residential Addition")  # New Construction, Addition, Renovation, ADU, Deck/Patio
    building_type = Column(String(100), nullable=False, default="Single Family Residence")
    num_floors = Column(Integer, default=1, nullable=False)
    area = Column(Float, nullable=True)
    area_unit = Column(String(20), default="sq_ft", nullable=False)  # sq_ft, sq_m
    stage = Column(String(100), default="Pre-Submission Preparation", nullable=False)  # Conceptual, Pre-Submission Preparation, Final Review
    
    jurisdiction_id = Column(String(100), nullable=False, default="US-CA-GENERIC")
    jurisdiction_supported = Column(String(50), default="supported", nullable=False)  # supported, partial, unsupported
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")
    checklists = relationship("Checklist", back_populates="project", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
