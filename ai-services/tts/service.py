"""
Text-to-Speech (TTS) Service with Voice Cloning
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, Optional

import torch
import torchaudio
import numpy as np
from TTS.api import TTS
from pydantic import BaseModel

from ..common.base_service import BaseAIService
from ..common.config import TTSConfig


class TTSRequest(BaseModel):
    """TTS processing request"""
    text: str
    language: str
    speaker_wav: Optional[str] = None  # Path to speaker reference audio
    emotion: str = "neutral"
    speed: float = 1.0
    output_path: Optional[str] = None


class VoiceCloningRequest(BaseModel):
    """Voice cloning request"""
    reference_audio: str
    speaker_name: str
    language: str


class TTSResult(BaseModel):
    """TTS processing result"""
    audio_path: str
    duration: float
    sample_rate: int
    speaker_similarity: Optional[float] = None
    processing_time: float


class TTSService(BaseAIService):
    """TTS service with voice cloning capabilities"""
    
    def __init__(self):
        config = TTSConfig()
        super().__init__(config)
        self.tts_model = None
        self.voice_cloning_model = None
    
    async def load_model(self):
        """Load TTS models"""
        self.logger.info("Loading TTS models", model=self.config.tts_model)
        
        try:
            # Load main TTS model (VITS or similar)
            if self.config.tts_model == "VITS":
                # Load multilingual VITS model
                self.tts_model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/your_tts",
                    progress_bar=False
                ).to(self.device)
            
            # Load voice cloning model
            if self.config.voice_cloning_model == "YourTTS":
                self.voice_cloning_model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/your_tts",
                    progress_bar=False
                ).to(self.device)
            
            self.logger.info(
                "TTS models loaded successfully",
                device=str(self.device)
            )
            
        except Exception as e:
            self.logger.error("Failed to load TTS models", error=str(e))
            raise
    
    async def process(self, input_data: Dict[str, Any]) -> TTSResult:
        """Process TTS request"""
        request = TTSRequest(**input_data)
        
        self.logger.info(
            "Processing TTS request",
            language=request.language,
            text_length=len(request.text),
            has_speaker_wav=bool(request.speaker_wav)
        )
        
        # Generate output path if not provided
        if not request.output_path:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f".{self.config.audio_format}",
                delete=False
            )
            output_path = temp_file.name
            temp_file.close()
        else:
            output_path = request.output_path
        
        # Generate speech
        duration, similarity = await self._generate_speech(
            text=request.text,
            language=request.language,
            speaker_wav=request.speaker_wav,
            emotion=request.emotion,
            speed=request.speed,
            output_path=output_path
        )
        
        return TTSResult(
            audio_path=output_path,
            duration=duration,
            sample_rate=self.config.sample_rate,
            speaker_similarity=similarity,
            processing_time=0.0  # Will be set by base service
        )
    
    async def _generate_speech(
        self,
        text: str,
        language: str,
        speaker_wav: Optional[str] = None,
        emotion: str = "neutral",
        speed: float = 1.0,
        output_path: str = None
    ) -> tuple[float, Optional[float]]:
        """Generate speech from text"""
        try:
            loop = asyncio.get_event_loop()
            
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode
                await loop.run_in_executor(
                    None,
                    lambda: self.voice_cloning_model.tts_to_file(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language,
                        file_path=output_path,
                        speed=speed
                    )
                )
                
                # Calculate speaker similarity (mock implementation)
                similarity = await self._calculate_speaker_similarity(
                    speaker_wav, output_path
                )
                
            else:
                # Standard TTS mode
                await loop.run_in_executor(
                    None,
                    lambda: self.tts_model.tts_to_file(
                        text=text,
                        language=language,
                        file_path=output_path,
                        speed=speed
                    )
                )
                similarity = None
            
            # Get audio duration
            duration = await self._get_audio_duration(output_path)
            
            return duration, similarity
            
        except Exception as e:
            self.logger.error("Speech generation failed", error=str(e))
            raise
    
    async def _calculate_speaker_similarity(
        self,
        reference_path: str,
        generated_path: str
    ) -> float:
        """Calculate similarity between reference and generated speech"""
        try:
            # This is a simplified implementation
            # In practice, you'd use speaker verification models
            
            # Load both audio files
            ref_audio, ref_sr = torchaudio.load(reference_path)
            gen_audio, gen_sr = torchaudio.load(generated_path)
            
            # Resample if needed
            if ref_sr != self.config.sample_rate:
                ref_audio = torchaudio.functional.resample(
                    ref_audio, ref_sr, self.config.sample_rate
                )
            
            if gen_sr != self.config.sample_rate:
                gen_audio = torchaudio.functional.resample(
                    gen_audio, gen_sr, self.config.sample_rate
                )
            
            # Simple spectral similarity (placeholder)
            # In practice, use speaker embeddings
            ref_spec = torch.stft(ref_audio[0], n_fft=1024, return_complex=True)
            gen_spec = torch.stft(gen_audio[0], n_fft=1024, return_complex=True)
            
            # Calculate cosine similarity
            ref_mag = torch.abs(ref_spec).flatten()
            gen_mag = torch.abs(gen_spec).flatten()
            
            # Ensure same length
            min_len = min(len(ref_mag), len(gen_mag))
            ref_mag = ref_mag[:min_len]
            gen_mag = gen_mag[:min_len]
            
            similarity = torch.cosine_similarity(
                ref_mag.unsqueeze(0),
                gen_mag.unsqueeze(0)
            ).item()
            
            return max(0.0, similarity)
            
        except Exception as e:
            self.logger.warning("Speaker similarity calculation failed", error=str(e))
            return 0.5  # Default similarity
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file"""
        try:
            audio, sr = torchaudio.load(audio_path)
            duration = audio.shape[1] / sr
            return duration
        except Exception as e:
            self.logger.warning("Failed to get audio duration", error=str(e))
            return 0.0
    
    async def clone_voice(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create voice clone from reference audio"""
        request = VoiceCloningRequest(**input_data)
        
        self.logger.info(
            "Creating voice clone",
            speaker_name=request.speaker_name,
            language=request.language
        )
        
        # Validate reference audio
        if not os.path.exists(request.reference_audio):
            raise FileNotFoundError(f"Reference audio not found: {request.reference_audio}")
        
        # Check audio duration
        duration = await self._get_audio_duration(request.reference_audio)
        if duration < self.config.min_voice_sample_duration:
            raise ValueError(
                f"Reference audio too short. Minimum {self.config.min_voice_sample_duration}s required, got {duration:.1f}s"
            )
        
        # Create voice profile (simplified)
        voice_profile = {
            "speaker_name": request.speaker_name,
            "language": request.language,
            "reference_audio": request.reference_audio,
            "duration": duration,
            "created_at": asyncio.get_event_loop().time()
        }
        
        return {
            "voice_profile": voice_profile,
            "status": "created",
            "message": f"Voice clone created for {request.speaker_name}"
        }
    
    def create_app(self):
        """Create FastAPI app with additional TTS endpoints"""
        app = super().create_app()
        
        @app.post("/synthesize", response_model=TTSResult)
        async def synthesize(request: TTSRequest):
            """Synthesize speech from text"""
            return await self.process(request.dict())
        
        @app.post("/clone-voice")
        async def clone_voice_endpoint(request: VoiceCloningRequest):
            """Create voice clone from reference audio"""
            return await self.clone_voice(request.dict())
        
        @app.get("/supported-languages")
        async def get_supported_languages():
            """Get list of supported languages for TTS"""
            # This would be model-specific
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
            ]
            return {"languages": languages}
        
        @app.get("/voices")
        async def list_voices():
            """List available voice profiles"""
            # This would query a voice database
            return {"voices": []}
        
        return app


def main():
    """Run TTS service"""
    service = TTSService()
    service.run()


if __name__ == "__main__":
    main()