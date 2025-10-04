"""
Voice profile and cloning models
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class VoiceProfile(Base):
    """Voice profile model for storing voice characteristics"""
    
    __tablename__ = "voice_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Profile details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Voice characteristics
    gender = Column(String(20))  # male, female, neutral
    age_range = Column(String(20))  # young, adult, senior
    accent = Column(String(50))  # american, british, etc.
    language = Column(String(10), nullable=False)  # ISO 639-1 code
    
    # Audio properties
    pitch_range = Column(JSON)  # [min_hz, max_hz]
    speaking_rate = Column(Float)  # words per minute
    voice_quality = Column(String(50))  # clear, raspy, smooth, etc.
    
    # Emotional characteristics
    emotional_range = Column(JSON)  # Supported emotions
    default_emotion = Column(String(50), default="neutral")
    
    # Technical details
    sample_rate = Column(Integer, default=22050)
    model_path = Column(String(500))  # Path to voice model
    model_type = Column(String(50))  # VITS, WaveNet, etc.
    model_version = Column(String(20))
    
    # Quality metrics
    quality_score = Column(Float)  # Overall quality score (0-1)
    naturalness_score = Column(Float)  # Naturalness score (0-1)
    similarity_score = Column(Float)  # Similarity to original (0-1)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    voice_clones = relationship("VoiceClone", back_populates="voice_profile")
    
    def __repr__(self):
        return f"<VoiceProfile(id={self.id}, name={self.name}, language={self.language})>"
    
    @property
    def is_high_quality(self) -> bool:
        """Check if voice profile is high quality"""
        return self.quality_score and self.quality_score >= 0.8
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()


class VoiceClone(Base):
    """Voice clone model for speaker-specific voice synthesis"""
    
    __tablename__ = "voice_clones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Clone details
    name = Column(String(255), nullable=False)
    speaker_id = Column(String(100), nullable=False)  # Original speaker identifier
    
    # Source information
    source_audio_path = Column(String(500), nullable=False)
    source_duration = Column(Float, nullable=False)  # seconds
    source_language = Column(String(10), nullable=False)
    
    # Voice profile reference
    voice_profile_id = Column(UUID(as_uuid=True), ForeignKey("voice_profiles.id"), nullable=False)
    
    # Clone quality
    clone_quality = Column(Float)  # Quality score (0-1)
    similarity_score = Column(Float)  # Similarity to original (0-1)
    training_loss = Column(Float)  # Final training loss
    
    # Training details
    training_steps = Column(Integer)
    training_duration = Column(Float)  # Training time in seconds
    model_size = Column(Integer)  # Model size in bytes
    
    # Supported features
    supports_emotions = Column(Boolean, default=False)
    supports_styles = Column(Boolean, default=False)
    supported_languages = Column(JSON)  # List of language codes
    
    # Usage and status
    is_ready = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trained_at = Column(DateTime)
    
    # Relationships
    voice_profile = relationship("VoiceProfile", back_populates="voice_clones")
    
    def __repr__(self):
        return f"<VoiceClone(id={self.id}, name={self.name}, speaker_id={self.speaker_id})>"
    
    @property
    def is_high_quality(self) -> bool:
        """Check if voice clone is high quality"""
        return (self.clone_quality and self.clone_quality >= 0.8 and
                self.similarity_score and self.similarity_score >= 0.8)
    
    @property
    def training_duration_formatted(self) -> str:
        """Get formatted training duration"""
        if not self.training_duration:
            return "00:00:00"
        
        hours = int(self.training_duration // 3600)
        minutes = int((self.training_duration % 3600) // 60)
        seconds = int(self.training_duration % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def model_size_mb(self) -> float:
        """Get model size in MB"""
        return self.model_size / (1024 * 1024) if self.model_size else 0
    
    def mark_ready(self, quality_score: float, similarity_score: float):
        """Mark voice clone as ready"""
        self.is_ready = True
        self.clone_quality = quality_score
        self.similarity_score = similarity_score
        self.trained_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
    
    def supports_language(self, language_code: str) -> bool:
        """Check if clone supports a specific language"""
        if not self.supported_languages:
            return language_code == self.source_language
        return language_code in self.supported_languages