"""
Ethics and compliance models for consent, watermarking, and provenance
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON
import uuid

from app.core.database import Base


class ConsentRecord(Base):
    """Consent record for ethical AI compliance"""
    
    __tablename__ = "consent_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Consent details
    consent_type = Column(String(50), nullable=False)  # voice, likeness, content
    subject_name = Column(String(255))  # Name of person giving consent
    subject_identifier = Column(String(255))  # Unique identifier
    
    # Consent status
    is_granted = Column(Boolean, default=False, nullable=False)
    consent_document_path = Column(String(500))  # Path to signed consent form
    
    # Usage scope
    permitted_uses = Column(JSON)  # List of permitted uses
    restrictions = Column(JSON)  # List of restrictions
    expiry_date = Column(DateTime)  # When consent expires
    
    # Legal details
    jurisdiction = Column(String(100))  # Legal jurisdiction
    legal_basis = Column(String(100))  # Legal basis for processing
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(255))  # Who verified the consent
    verification_method = Column(String(100))  # How consent was verified
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="consent_records")
    project = relationship("Project", back_populates="consent_records")
    
    def __repr__(self):
        return f"<ConsentRecord(id={self.id}, type={self.consent_type}, granted={self.is_granted})>"
    
    @property
    def is_active(self) -> bool:
        """Check if consent is active"""
        if not self.is_granted or self.revoked_at:
            return False
        if self.expiry_date and datetime.utcnow() > self.expiry_date:
            return False
        return True
    
    @property
    def is_expired(self) -> bool:
        """Check if consent is expired"""
        return self.expiry_date and datetime.utcnow() > self.expiry_date
    
    def grant_consent(self, document_path: str = None):
        """Grant consent"""
        self.is_granted = True
        self.granted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if document_path:
            self.consent_document_path = document_path
    
    def revoke_consent(self):
        """Revoke consent"""
        self.is_granted = False
        self.revoked_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def verify(self, verified_by: str, method: str):
        """Verify consent"""
        self.is_verified = True
        self.verified_by = verified_by
        self.verification_method = method
        self.updated_at = datetime.utcnow()


class WatermarkRecord(Base):
    """Watermark record for tracking AI-generated content"""
    
    __tablename__ = "watermark_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Watermark details
    watermark_type = Column(String(50), nullable=False)  # invisible, visible, audio
    watermark_method = Column(String(100), nullable=False)  # LSB, DCT, spectral
    watermark_strength = Column(Float, default=0.1)
    
    # Content information
    content_type = Column(String(50), nullable=False)  # video, audio, image
    content_path = Column(String(500), nullable=False)
    content_hash = Column(String(64))  # SHA-256 hash of content
    
    # Watermark payload
    payload_data = Column(JSON)  # Watermark payload
    payload_hash = Column(String(64))  # Hash of payload
    
    # Detection information
    detection_key = Column(String(255))  # Key for watermark detection
    is_detectable = Column(Boolean, default=True)
    detection_confidence = Column(Float)  # Detection confidence (0-1)
    
    # Quality metrics
    psnr = Column(Float)  # Peak Signal-to-Noise Ratio
    ssim = Column(Float)  # Structural Similarity Index
    quality_degradation = Column(Float)  # Quality degradation (0-1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="watermark_records")
    
    def __repr__(self):
        return f"<WatermarkRecord(id={self.id}, type={self.watermark_type}, method={self.watermark_method})>"
    
    @property
    def is_high_quality(self) -> bool:
        """Check if watermark maintains high quality"""
        return (self.psnr and self.psnr >= 40 and 
                self.ssim and self.ssim >= 0.95)
    
    @property
    def is_robust(self) -> bool:
        """Check if watermark is robust"""
        return (self.detection_confidence and 
                self.detection_confidence >= 0.9)


class ProvenanceRecord(Base):
    """Provenance record for AI content traceability"""
    
    __tablename__ = "provenance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Content information
    content_type = Column(String(50), nullable=False)  # video, audio, image
    content_path = Column(String(500), nullable=False)
    content_hash = Column(String(64))  # SHA-256 hash
    
    # AI processing chain
    processing_chain = Column(JSON, nullable=False)  # List of processing steps
    models_used = Column(JSON)  # List of AI models used
    
    # Source information
    source_content_hash = Column(String(64))  # Hash of original content
    source_metadata = Column(JSON)  # Original content metadata
    
    # Generation details
    generation_timestamp = Column(DateTime, nullable=False)
    generation_parameters = Column(JSON)  # Parameters used for generation
    
    # Quality and validation
    quality_metrics = Column(JSON)  # Quality assessment results
    validation_results = Column(JSON)  # Validation check results
    
    # C2PA compliance
    c2pa_manifest = Column(JSON)  # C2PA manifest data
    c2pa_signature = Column(Text)  # C2PA digital signature
    
    # Human involvement
    human_review = Column(Boolean, default=False)
    human_reviewer = Column(String(255))
    review_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="provenance_records")
    
    def __repr__(self):
        return f"<ProvenanceRecord(id={self.id}, content_type={self.content_type})>"
    
    @property
    def is_c2pa_compliant(self) -> bool:
        """Check if record is C2PA compliant"""
        return bool(self.c2pa_manifest and self.c2pa_signature)
    
    @property
    def processing_step_count(self) -> int:
        """Get number of processing steps"""
        return len(self.processing_chain) if self.processing_chain else 0
    
    def add_processing_step(self, step_name: str, model_name: str, 
                          parameters: dict, timestamp: datetime = None):
        """Add a processing step to the chain"""
        if not self.processing_chain:
            self.processing_chain = []
        if not self.models_used:
            self.models_used = []
        
        step = {
            "step": step_name,
            "model": model_name,
            "parameters": parameters,
            "timestamp": (timestamp or datetime.utcnow()).isoformat()
        }
        
        self.processing_chain.append(step)
        if model_name not in self.models_used:
            self.models_used.append(model_name)
        
        self.updated_at = datetime.utcnow()
    
    def add_human_review(self, reviewer: str, notes: str = None):
        """Add human review information"""
        self.human_review = True
        self.human_reviewer = reviewer
        if notes:
            self.review_notes = notes
        self.updated_at = datetime.utcnow()