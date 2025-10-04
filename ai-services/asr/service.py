"""
Automatic Speech Recognition (ASR) Service using Whisper
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, List, Optional

import torch
import whisper
import librosa
import numpy as np
from pydantic import BaseModel

from ..common.base_service import BaseAIService
from ..common.config import ASRConfig


class ASRRequest(BaseModel):
    """ASR processing request"""
    audio_path: str
    language: Optional[str] = None
    task: str = "transcribe"  # transcribe or translate
    return_segments: bool = True
    return_language_detection: bool = True


class ASRSegment(BaseModel):
    """ASR segment result"""
    start: float
    end: float
    text: str
    confidence: float


class ASRResult(BaseModel):
    """ASR processing result"""
    text: str
    language: str
    language_confidence: float
    segments: List[ASRSegment]
    processing_time: float


class ASRService(BaseAIService):
    """ASR service using Whisper large-v3"""
    
    def __init__(self):
        config = ASRConfig()
        super().__init__(config)
        self.model = None
    
    async def load_model(self):
        """Load Whisper model"""
        self.logger.info("Loading Whisper model", model=self.config.whisper_model)
        
        # Load model on specified device
        self.model = whisper.load_model(
            self.config.whisper_model.replace("whisper-", ""),
            device=self.device
        )
        
        self.logger.info(
            "Whisper model loaded successfully",
            model=self.config.whisper_model,
            device=str(self.device)
        )
    
    async def process(self, input_data: Dict[str, Any]) -> ASRResult:
        """Process audio file for speech recognition"""
        request = ASRRequest(**input_data)
        
        if not os.path.exists(request.audio_path):
            raise FileNotFoundError(f"Audio file not found: {request.audio_path}")
        
        self.logger.info(
            "Processing ASR request",
            audio_path=request.audio_path,
            language=request.language,
            task=request.task
        )
        
        # Load and preprocess audio
        audio = await self._load_audio(request.audio_path)
        
        # Run Whisper inference
        result = await self._transcribe_audio(
            audio, 
            language=request.language,
            task=request.task
        )
        
        # Process results
        segments = []
        if request.return_segments and "segments" in result:
            for segment in result["segments"]:
                segments.append(ASRSegment(
                    start=segment["start"],
                    end=segment["end"],
                    text=segment["text"].strip(),
                    confidence=segment.get("avg_logprob", 0.0)
                ))
        
        # Language detection
        detected_language = result.get("language", "unknown")
        language_confidence = 1.0  # Whisper doesn't provide language confidence
        
        return ASRResult(
            text=result["text"].strip(),
            language=detected_language,
            language_confidence=language_confidence,
            segments=segments,
            processing_time=0.0  # Will be set by base service
        )
    
    async def _load_audio(self, audio_path: str) -> np.ndarray:
        """Load and preprocess audio file"""
        try:
            # Load audio with librosa
            audio, sr = librosa.load(
                audio_path, 
                sr=self.config.sample_rate,
                mono=True
            )
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            return audio
            
        except Exception as e:
            self.logger.error("Failed to load audio", error=str(e), audio_path=audio_path)
            raise
    
    async def _transcribe_audio(
        self, 
        audio: np.ndarray, 
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        try:
            # Prepare options
            options = {
                "task": task,
                "language": language,
                "verbose": False,
                "word_timestamps": True,
            }
            
            # Remove None values
            options = {k: v for k, v in options.items() if v is not None}
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(audio, **options)
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Transcription failed", error=str(e))
            raise
    
    async def detect_language(self, audio_path: str) -> Dict[str, Any]:
        """Detect language of audio file"""
        audio = await self._load_audio(audio_path)
        
        # Use Whisper's language detection
        # Load a small portion for language detection
        audio_segment = audio[:self.config.sample_rate * 30]  # First 30 seconds
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: whisper.detect_language(self.model, audio_segment)
        )
        
        return {
            "language": result[0],
            "confidence": result[1]
        }
    
    def create_app(self):
        """Create FastAPI app with additional ASR endpoints"""
        app = super().create_app()
        
        @app.post("/transcribe", response_model=ASRResult)
        async def transcribe(request: ASRRequest):
            """Transcribe audio file"""
            return await self.process(request.dict())
        
        @app.post("/detect-language")
        async def detect_language_endpoint(audio_path: str):
            """Detect language of audio file"""
            return await self.detect_language(audio_path)
        
        @app.get("/supported-languages")
        async def get_supported_languages():
            """Get list of supported languages"""
            # Whisper supports 99 languages
            languages = [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Spanish"},
                {"code": "fr", "name": "French"},
                {"code": "de", "name": "German"},
                {"code": "it", "name": "Italian"},
                {"code": "pt", "name": "Portuguese"},
                {"code": "ru", "name": "Russian"},
                {"code": "zh", "name": "Chinese"},
                {"code": "ja", "name": "Japanese"},
                {"code": "ko", "name": "Korean"},
                # Add more languages as needed
            ]
            return {"languages": languages}
        
        return app


def main():
    """Run ASR service"""
    service = ASRService()
    service.run()


if __name__ == "__main__":
    main()