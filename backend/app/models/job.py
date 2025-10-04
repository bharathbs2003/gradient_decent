"""
Job model for tracking processing tasks
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class JobStatus(str, Enum):
    """Job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobType(str, Enum):
    """Job type"""
    ASR = "asr"
    TRANSLATION = "translation"
    TTS = "tts"
    VOICE_CLONING = "voice_cloning"
    FACE_EXTRACTION = "face_extraction"
    FACE_ANIMATION = "face_animation"
    RENDERING = "rendering"
    QUALITY_CHECK = "quality_check"
    WATERMARKING = "watermarking"
    FULL_DUBBING = "full_dubbing"


class Job(Base):
    """Job model for processing tasks"""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job details
    type = Column(ENUM(JobType), nullable=False)
    status = Column(ENUM(JobStatus), default=JobStatus.PENDING, nullable=False)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    
    # References
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Input/Output
    input_data = Column(JSON)  # Input parameters and file references
    output_data = Column(JSON)  # Output results and file references
    
    # Progress and metrics
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Quality metrics (if applicable)
    quality_metrics = Column(JSON)
    
    # Processing details
    worker_id = Column(String(255))  # Celery worker ID
    task_id = Column(String(255))  # Celery task ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Estimated and actual duration
    estimated_duration = Column(Integer)  # seconds
    actual_duration = Column(Integer)  # seconds
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    project = relationship("Project", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if job is active"""
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.RETRYING]
    
    @property
    def is_completed(self) -> bool:
        """Check if job is completed"""
        return self.status == JobStatus.COMPLETED
    
    @property
    def has_failed(self) -> bool:
        """Check if job has failed"""
        return self.status == JobStatus.FAILED
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.retry_count < self.max_retries and self.status == JobStatus.FAILED
    
    def start(self, worker_id: str = None, task_id: str = None):
        """Mark job as started"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if worker_id:
            self.worker_id = worker_id
        if task_id:
            self.task_id = task_id
    
    def complete(self, output_data: dict = None, quality_metrics: dict = None):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        if output_data:
            self.output_data = output_data
        if quality_metrics:
            self.quality_metrics = quality_metrics
            
        # Calculate actual duration
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.actual_duration = int(duration)
    
    def fail(self, error_message: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
        
        # Calculate actual duration if started
        if self.started_at:
            duration = (datetime.utcnow() - self.started_at).total_seconds()
            self.actual_duration = int(duration)
    
    def retry(self):
        """Retry failed job"""
        if not self.can_retry:
            raise ValueError("Job cannot be retried")
        
        self.status = JobStatus.RETRYING
        self.retry_count += 1
        self.error_message = None
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel job"""
        if self.is_completed:
            raise ValueError("Cannot cancel completed job")
        
        self.status = JobStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, progress: float):
        """Update job progress"""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.utcnow()