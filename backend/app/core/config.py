"""
Configuration management for the Multilingual AI Video Dubbing Platform
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Multilingual AI Video Dubbing Platform"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production-this-is-for-development-only", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./dubbing_platform.db", description="Database URL")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads")
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024)  # 500MB
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "mov", "avi", "mkv"]
    ALLOWED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "aac", "flac"]
    
    # AI Services
    AI_SERVICES_BASE_URL: str = Field(default="http://localhost:8001")
    
    # ASR Settings
    WHISPER_MODEL: str = Field(default="whisper-large-v3")
    ASR_TIMEOUT: int = Field(default=300)  # 5 minutes
    
    # Translation Settings
    TRANSLATION_MODEL: str = Field(default="seamlessM4T")
    SUPPORTED_LANGUAGES: List[str] = Field(default=[
        "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko",
        "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no",
        "fi", "el", "he", "cs", "hu", "ro", "bg", "hr", "sk", "sl",
        "et", "lv", "lt", "mt", "ga", "cy", "eu", "ca", "gl", "is",
        "mk", "sq", "sr", "bs", "me", "az", "kk", "ky", "uz", "tg"
    ])
    
    # TTS Settings
    TTS_MODEL: str = Field(default="VITS")
    VOICE_CLONING_MIN_DURATION: int = Field(default=30)  # seconds
    
    # Face Animation Settings
    FACE_MODEL: str = Field(default="FLAME")
    EXPRESSION_MODEL: str = Field(default="LSTM")
    RENDERER_MODEL: str = Field(default="DAE-Talker")
    
    # Quality Metrics
    TARGET_LSE_C: float = Field(default=0.85)
    TARGET_FID: float = Field(default=15.0)
    TARGET_AU_CORRELATION: float = Field(default=0.75)
    TARGET_BLEU: float = Field(default=35.0)
    
    # Processing
    MAX_CONCURRENT_JOBS: int = Field(default=5)
    JOB_TIMEOUT: int = Field(default=3600)  # 1 hour
    CLEANUP_INTERVAL: int = Field(default=86400)  # 24 hours
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PORT: int = Field(default=9090)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    # Ethical AI
    ENABLE_WATERMARKING: bool = Field(default=True)
    ENABLE_CONSENT_TRACKING: bool = Field(default=True)
    ENABLE_PROVENANCE: bool = Field(default=True)
    WATERMARK_STRENGTH: float = Field(default=0.1)
    
    @validator("SUPPORTED_LANGUAGES")
    def validate_languages(cls, v):
        """Ensure we have at least 50 languages as per PRD"""
        if len(v) < 50:
            raise ValueError("Must support at least 50 languages")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure secret key is strong enough"""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()