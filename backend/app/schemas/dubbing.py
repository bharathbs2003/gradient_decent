"""
Pydantic schemas for dubbing operations
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class QualityMode(str, Enum):
    """Quality processing mode"""
    STRUCTURAL = "structural"  # High quality, slower
    END_TO_END = "end_to_end"  # Faster, lower quality


class DubbingRequest(BaseModel):
    """Request for dubbing job creation"""
    target_languages: List[str] = Field(..., min_items=1, max_items=10)
    source_language: Optional[str] = None
    enable_voice_cloning: bool = True
    enable_emotion_preservation: bool = True
    quality_mode: QualityMode = QualityMode.STRUCTURAL
    require_human_review: bool = False
    custom_settings: Optional[Dict[str, Any]] = None
    
    @validator('target_languages')
    def validate_languages(cls, v):
        """Validate language codes"""
        valid_codes = [
            "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko",
            "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no"
        ]  # Subset for validation
        
        for lang in v:
            if lang not in valid_codes:
                raise ValueError(f"Unsupported language code: {lang}")
        return v


class DubbingJobResponse(BaseModel):
    """Response for dubbing job"""
    id: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None
    target_languages: List[str]
    source_language: Optional[str]
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class DubbingProgressResponse(BaseModel):
    """Detailed progress response"""
    job_id: str
    overall_progress: float
    current_stage: str
    stages: List[Dict[str, Any]]
    estimated_time_remaining: Optional[int] = None  # seconds
    quality_metrics: Optional[Dict[str, float]] = None


class QualityCheckRequest(BaseModel):
    """Request for quality check"""
    check_lip_sync: bool = True
    check_visual_fidelity: bool = True
    check_emotion_preservation: bool = True
    check_translation_quality: bool = True
    target_language: Optional[str] = None  # Check specific language


class QualityMetrics(BaseModel):
    """Quality metrics results"""
    lse_c_score: Optional[float] = None  # Lip-sync accuracy
    fid_score: Optional[float] = None  # Visual fidelity
    au_correlation: Optional[float] = None  # Emotion preservation
    bleu_score: Optional[float] = None  # Translation quality
    overall_score: Optional[float] = None


class QualityCheckResponse(BaseModel):
    """Quality check results"""
    job_id: str
    language: str
    metrics: QualityMetrics
    passed: bool
    issues: List[str] = []
    recommendations: List[str] = []


class LanguageInfo(BaseModel):
    """Language information and capabilities"""
    code: str
    name: str
    native_name: str
    supports_asr: bool
    supports_tts: bool
    supports_translation: bool
    voice_count: int


class ModelInfoResponse(BaseModel):
    """AI model information"""
    asr_model: str
    translation_model: str
    tts_model: str
    face_model: str
    expression_model: str
    renderer_model: str
    model_versions: Dict[str, str]


class PreviewRequest(BaseModel):
    """Request for preview generation"""
    language: str
    segment_start: Optional[float] = None  # seconds
    segment_end: Optional[float] = None  # seconds
    quality: str = "medium"  # low, medium, high


class PreviewResponse(BaseModel):
    """Preview generation response"""
    preview_url: str
    expires_in: int  # seconds
    duration: float  # seconds
    resolution: str


class DubbingStats(BaseModel):
    """Dubbing statistics"""
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    average_processing_time: float  # minutes
    languages_processed: int
    total_duration_processed: float  # hours