import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    current_step = Column(String(100), default="Initiating", nullable=False)
    current_step_number = Column(Integer, default=1, nullable=False)
    total_steps = Column(Integer, default=9, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    logs = Column(JSON, default=list, nullable=False)  # List of {timestamp, step, message, level}
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="analysis_jobs")
