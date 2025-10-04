"""
Project model for organizing dubbing work
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class ProjectStatus(str, Enum):
    """Project status"""
    DRAFT = "draft"
    PROCESSING = "processing"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(Base):
    """Project model"""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status and progress
    status = Column(ENUM(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Languages
    source_language = Column(String(10), nullable=False)  # ISO 639-1 code
    target_languages = Column(JSON)  # List of target language codes
    
    # Settings
    settings = Column(JSON)  # Project-specific settings
    
    # Quality metrics
    target_lse_c = Column(Float, default=0.85)
    target_fid = Column(Float, default=15.0)
    target_au_correlation = Column(Float, default=0.75)
    target_bleu = Column(Float, default=35.0)
    
    # Ethics settings
    require_consent = Column(Boolean, default=True)
    enable_watermarking = Column(Boolean, default=True)
    enable_provenance = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    media_files = relationship("MediaFile", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="project", cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="project")
    watermark_records = relationship("WatermarkRecord", back_populates="project")
    provenance_records = relationship("ProvenanceRecord", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if project is active"""
        return self.status in [ProjectStatus.DRAFT, ProjectStatus.PROCESSING, ProjectStatus.REVIEW]
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed"""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def has_failed(self) -> bool:
        """Check if project has failed"""
        return self.status == ProjectStatus.FAILED
    
    def get_target_language_count(self) -> int:
        """Get number of target languages"""
        return len(self.target_languages) if self.target_languages else 0
    
    def update_progress(self, progress: float):
        """Update project progress"""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self):
        """Mark project as completed"""
        self.status = ProjectStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self):
        """Mark project as failed"""
        self.status = ProjectStatus.FAILED
        self.updated_at = datetime.utcnow()