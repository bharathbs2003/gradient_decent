"""
Translation model for managing multilingual content
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class TranslationStatus(str, Enum):
    """Translation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class Translation(Base):
    """Translation model"""
    
    __tablename__ = "translations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Project reference
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Languages
    source_language = Column(String(10), nullable=False)  # ISO 639-1 code
    target_language = Column(String(10), nullable=False)  # ISO 639-1 code
    
    # Content
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text)
    reviewed_text = Column(Text)  # Human-reviewed version
    
    # Metadata
    speaker_id = Column(String(100))  # Speaker identifier
    segment_start = Column(Float)  # Start time in seconds
    segment_end = Column(Float)  # End time in seconds
    confidence_score = Column(Float)  # Translation confidence (0-1)
    
    # Status and review
    status = Column(ENUM(TranslationStatus), default=TranslationStatus.PENDING, nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_notes = Column(Text)
    
    # Quality metrics
    bleu_score = Column(Float)  # BLEU score vs reference
    quality_metrics = Column(JSON)  # Additional quality metrics
    
    # Processing details
    model_used = Column(String(100))  # Translation model
    processing_time = Column(Float)  # Processing time in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="translations")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<Translation(id={self.id}, {self.source_language}->{self.target_language}, status={self.status})>"
    
    @property
    def is_pending(self) -> bool:
        """Check if translation is pending"""
        return self.status == TranslationStatus.PENDING
    
    @property
    def is_completed(self) -> bool:
        """Check if translation is completed"""
        return self.status == TranslationStatus.COMPLETED
    
    @property
    def needs_review(self) -> bool:
        """Check if translation needs review"""
        return self.status == TranslationStatus.REVIEW
    
    @property
    def is_approved(self) -> bool:
        """Check if translation is approved"""
        return self.status == TranslationStatus.APPROVED
    
    @property
    def has_failed(self) -> bool:
        """Check if translation has failed"""
        return self.status == TranslationStatus.FAILED
    
    @property
    def duration(self) -> float:
        """Get segment duration"""
        if self.segment_start is not None and self.segment_end is not None:
            return self.segment_end - self.segment_start
        return 0.0
    
    @property
    def final_text(self) -> str:
        """Get final text (reviewed if available, otherwise translated)"""
        return self.reviewed_text or self.translated_text or ""
    
    def complete(self, translated_text: str, confidence_score: float = None, 
                bleu_score: float = None, quality_metrics: dict = None):
        """Mark translation as completed"""
        self.status = TranslationStatus.COMPLETED
        self.translated_text = translated_text
        self.updated_at = datetime.utcnow()
        
        if confidence_score is not None:
            self.confidence_score = confidence_score
        if bleu_score is not None:
            self.bleu_score = bleu_score
        if quality_metrics:
            self.quality_metrics = quality_metrics
    
    def submit_for_review(self):
        """Submit translation for human review"""
        if self.status != TranslationStatus.COMPLETED:
            raise ValueError("Translation must be completed before review")
        
        self.status = TranslationStatus.REVIEW
        self.updated_at = datetime.utcnow()
    
    def approve(self, reviewer_id: uuid.UUID, reviewed_text: str = None, notes: str = None):
        """Approve translation"""
        self.status = TranslationStatus.APPROVED
        self.reviewer_id = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if reviewed_text:
            self.reviewed_text = reviewed_text
        if notes:
            self.review_notes = notes
    
    def reject(self, reviewer_id: uuid.UUID, notes: str):
        """Reject translation"""
        self.status = TranslationStatus.REJECTED
        self.reviewer_id = reviewer_id
        self.review_notes = notes
        self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fail(self, error_message: str):
        """Mark translation as failed"""
        self.status = TranslationStatus.FAILED
        self.review_notes = error_message
        self.updated_at = datetime.utcnow()
    
    def calculate_word_count(self, text_type: str = "source") -> int:
        """Calculate word count for specified text"""
        if text_type == "source":
            text = self.source_text
        elif text_type == "translated":
            text = self.translated_text
        elif text_type == "reviewed":
            text = self.reviewed_text
        else:
            text = self.final_text
        
        return len(text.split()) if text else 0