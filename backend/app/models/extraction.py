import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    raw_text = Column(Text, nullable=True)
    page_extractions = Column(JSON, nullable=True)  # List of {page: int, text: str, word_count: int, dimensions: dict}
    extracted_fields = Column(JSON, nullable=True)  # Dict of fields found (address, dimensions, setbacks, stamps, etc.)
    layout_metadata = Column(JSON, nullable=True)   # Tables, blocks, headings
    preview_images = Column(JSON, nullable=True)    # Rendered preview image paths per page
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    document = relationship("Document", back_populates="extraction")
