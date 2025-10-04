"""
Media file model for storing video and audio files
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class MediaType(str, Enum):
    """Media file type"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TRANSCRIPT = "transcript"
    SUBTITLE = "subtitle"


class MediaFile(Base):
    """Media file model"""
    
    __tablename__ = "media_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64))  # SHA-256 hash
    
    # Media type and format
    media_type = Column(ENUM(MediaType), nullable=False)
    format = Column(String(10))  # mp4, wav, jpg, etc.
    
    # Project reference
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Media properties
    duration = Column(Float)  # seconds (for video/audio)
    width = Column(Integer)  # pixels (for video/image)
    height = Column(Integer)  # pixels (for video/image)
    fps = Column(Float)  # frames per second (for video)
    bitrate = Column(Integer)  # bits per second (for video/audio)
    sample_rate = Column(Integer)  # Hz (for audio)
    channels = Column(Integer)  # audio channels
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_metadata = Column(JSON)  # Processing results and metadata
    
    # Language and content
    language = Column(String(10))  # ISO 639-1 code
    content_description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="media_files")
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename={self.filename}, type={self.media_type})>"
    
    @property
    def is_video(self) -> bool:
        """Check if file is video"""
        return self.media_type == MediaType.VIDEO
    
    @property
    def is_audio(self) -> bool:
        """Check if file is audio"""
        return self.media_type == MediaType.AUDIO
    
    @property
    def is_image(self) -> bool:
        """Check if file is image"""
        return self.media_type == MediaType.IMAGE
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024) if self.file_size else 0
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)"""
        if not self.duration:
            return "00:00:00"
        
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def resolution(self) -> str:
        """Get video resolution string"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"
    
    def get_aspect_ratio(self) -> float:
        """Get aspect ratio"""
        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return 0.0
    
    def is_hd(self) -> bool:
        """Check if video is HD (720p or higher)"""
        return self.height and self.height >= 720
    
    def is_4k(self) -> bool:
        """Check if video is 4K"""
        return self.height and self.height >= 2160
    
    def update_processing_status(self, is_processed: bool, metadata: dict = None):
        """Update processing status"""
        self.is_processed = is_processed
        if metadata:
            self.processing_metadata = metadata
        self.updated_at = datetime.utcnow()