"""
Common configuration for AI services
"""

import os
from typing import Dict, Any
from pydantic import BaseSettings, Field


class AIServiceConfig(BaseSettings):
    """Base configuration for AI services"""
    
    # Service settings
    service_name: str = Field(..., description="Name of the AI service")
    service_port: int = Field(default=8001, description="Port to run the service on")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Model settings
    model_cache_dir: str = Field(default="./models", description="Directory to cache models")
    device: str = Field(default="cuda", description="Device to run models on (cuda/cpu)")
    max_batch_size: int = Field(default=4, description="Maximum batch size for inference")
    
    # Performance settings
    num_workers: int = Field(default=1, description="Number of worker processes")
    max_memory_gb: float = Field(default=8.0, description="Maximum memory usage in GB")
    
    # Quality thresholds (from PRD)
    target_lse_c: float = Field(default=0.85, description="Target LSE-C score")
    target_fid: float = Field(default=15.0, description="Target FID score")
    target_au_correlation: float = Field(default=0.75, description="Target AU correlation")
    target_bleu: float = Field(default=35.0, description="Target BLEU score")
    
    class Config:
        env_file = ".env"


class ASRConfig(AIServiceConfig):
    """ASR service configuration"""
    
    service_name: str = "asr"
    
    # Whisper settings
    whisper_model: str = Field(default="whisper-large-v3", description="Whisper model to use")
    whisper_device: str = Field(default="cuda", description="Device for Whisper")
    
    # Audio processing
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    chunk_duration: float = Field(default=30.0, description="Audio chunk duration in seconds")
    
    # Language detection
    enable_language_detection: bool = Field(default=True, description="Enable automatic language detection")
    confidence_threshold: float = Field(default=0.8, description="Confidence threshold for language detection")


class TranslationConfig(AIServiceConfig):
    """Translation service configuration"""
    
    service_name: str = "translation"
    
    # Model settings
    translation_model: str = Field(default="seamlessM4T", description="Translation model to use")
    max_length: int = Field(default=512, description="Maximum sequence length")
    
    # Supported languages (from PRD - 50+ languages)
    supported_languages: list = Field(default=[
        "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko",
        "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no",
        "fi", "el", "he", "cs", "hu", "ro", "bg", "hr", "sk", "sl",
        "et", "lv", "lt", "mt", "ga", "cy", "eu", "ca", "gl", "is",
        "mk", "sq", "sr", "bs", "me", "az", "kk", "ky", "uz", "tg"
    ])


class TTSConfig(AIServiceConfig):
    """TTS service configuration"""
    
    service_name: str = "tts"
    
    # Model settings
    tts_model: str = Field(default="VITS", description="TTS model to use")
    voice_cloning_model: str = Field(default="YourTTS", description="Voice cloning model")
    
    # Voice cloning
    min_voice_sample_duration: int = Field(default=30, description="Minimum voice sample duration in seconds")
    voice_similarity_threshold: float = Field(default=0.8, description="Voice similarity threshold")
    
    # Audio generation
    sample_rate: int = Field(default=22050, description="Output audio sample rate")
    audio_format: str = Field(default="wav", description="Output audio format")


class FaceAnimationConfig(AIServiceConfig):
    """Face animation service configuration"""
    
    service_name: str = "face-animation"
    
    # Model settings
    face_model: str = Field(default="FLAME", description="3D face model")
    expression_model: str = Field(default="LSTM", description="Expression prediction model")
    renderer_model: str = Field(default="DAE-Talker", description="Neural renderer model")
    
    # Processing settings
    video_fps: int = Field(default=25, description="Video frame rate")
    face_detection_confidence: float = Field(default=0.5, description="Face detection confidence threshold")
    
    # Quality settings
    output_resolution: tuple = Field(default=(1080, 1920), description="Output video resolution (height, width)")
    enable_super_resolution: bool = Field(default=False, description="Enable super resolution")


# Global configuration instances
asr_config = ASRConfig()
translation_config = TranslationConfig()
tts_config = TTSConfig()
face_animation_config = FaceAnimationConfig()


def get_config(service_name: str) -> AIServiceConfig:
    """Get configuration for a specific service"""
    configs = {
        "asr": asr_config,
        "translation": translation_config,
        "tts": tts_config,
        "face-animation": face_animation_config,
    }
    
    return configs.get(service_name, AIServiceConfig(service_name=service_name))