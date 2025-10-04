"""
Main dubbing service that orchestrates the entire pipeline
"""

import asyncio
import os
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import structlog

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.core.config import get_settings
from app.models import User, Project, Job, MediaFile, JobType, JobStatus
from app.schemas.dubbing import DubbingRequest, DubbingProgressResponse
from app.services.ethics import EthicsService

logger = structlog.get_logger()
settings = get_settings()


class DubbingService:
    """Main service for orchestrating the dubbing pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ethics_service = EthicsService(db)
        self.ai_services_base_url = settings.AI_SERVICES_BASE_URL
    
    async def create_dubbing_job(
        self,
        user: User,
        video_file: UploadFile,
        request: DubbingRequest
    ) -> Job:
        """Create a new dubbing job"""
        logger.info(
            "Creating dubbing job",
            user_id=str(user.id),
            target_languages=request.target_languages
        )
        
        # Create project
        project = Project(
            name=f"Dubbing - {video_file.filename}",
            owner_id=user.id,
            source_language=request.source_language or "auto",
            target_languages=request.target_languages,
            settings={
                "enable_voice_cloning": request.enable_voice_cloning,
                "enable_emotion_preservation": request.enable_emotion_preservation,
                "quality_mode": request.quality_mode,
                "require_human_review": request.require_human_review
            }
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Save uploaded video
        video_path = await self._save_uploaded_file(video_file, project.id)
        
        # Create media file record
        media_file = MediaFile(
            filename=f"{project.id}_{video_file.filename}",
            original_filename=video_file.filename,
            file_path=video_path,
            file_size=video_file.size or 0,
            mime_type=video_file.content_type or "video/mp4",
            media_type="video",
            project_id=project.id
        )
        self.db.add(media_file)
        
        # Create main dubbing job
        job = Job(
            type=JobType.FULL_DUBBING,
            user_id=user.id,
            project_id=project.id,
            input_data={
                "video_path": video_path,
                "target_languages": request.target_languages,
                "source_language": request.source_language,
                "settings": request.dict()
            }
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(
            "Dubbing job created",
            job_id=str(job.id),
            project_id=str(project.id)
        )
        
        return job
    
    async def process_dubbing_job(self, job_id: str):
        """Process a dubbing job through the entire pipeline"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error("Job not found", job_id=job_id)
            return
        
        try:
            job.start()
            self.db.commit()
            
            logger.info("Starting dubbing pipeline", job_id=job_id)
            
            # Step 1: Ethics checks
            await self._run_ethics_checks(job)
            
            # Step 2: ASR (Automatic Speech Recognition)
            transcript = await self._run_asr(job)
            job.update_progress(0.2)
            self.db.commit()
            
            # Step 3: Translation
            translations = await self._run_translation(job, transcript)
            job.update_progress(0.4)
            self.db.commit()
            
            # Step 4: Voice synthesis
            audio_files = await self._run_voice_synthesis(job, translations)
            job.update_progress(0.6)
            self.db.commit()
            
            # Step 5: Face animation
            animated_videos = await self._run_face_animation(job, audio_files)
            job.update_progress(0.8)
            self.db.commit()
            
            # Step 6: Quality checks
            quality_results = await self._run_quality_checks(job, animated_videos)
            
            # Step 7: Apply ethical safeguards
            final_videos = await self._apply_ethical_safeguards(job, animated_videos)
            job.update_progress(1.0)
            
            # Complete job
            job.complete(
                output_data={
                    "videos": final_videos,
                    "quality_metrics": quality_results
                },
                quality_metrics=quality_results
            )
            self.db.commit()
            
            logger.info("Dubbing pipeline completed", job_id=job_id)
            
        except Exception as e:
            logger.error("Dubbing pipeline failed", job_id=job_id, error=str(e))
            job.fail(str(e))
            self.db.commit()
    
    async def _save_uploaded_file(self, file: UploadFile, project_id: str) -> str:
        """Save uploaded file to storage"""
        upload_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return file_path
    
    async def _run_ethics_checks(self, job: Job):
        """Run initial ethics checks"""
        logger.info("Running ethics checks", job_id=str(job.id))
        
        project = job.project
        
        # Check consent requirements
        if project.require_consent:
            consent_status = await self.ethics_service.check_consent_status(project.id)
            if not consent_status["has_consent"]:
                raise ValueError("Consent required but not provided")
        
        # Create provenance record
        await self.ethics_service.create_provenance_record(
            project_id=project.id,
            content_path=job.input_data["video_path"],
            processing_chain=[{
                "step": "ethics_check",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "passed"
            }]
        )
    
    async def _run_asr(self, job: Job) -> Dict[str, Any]:
        """Run Automatic Speech Recognition"""
        logger.info("Running ASR", job_id=str(job.id))
        
        video_path = job.input_data["video_path"]
        source_language = job.input_data.get("source_language")
        
        # Call ASR service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ai_services_base_url}:8001/transcribe",
                json={
                    "audio_path": video_path,
                    "language": source_language,
                    "return_segments": True
                },
                timeout=300
            )
            response.raise_for_status()
            return response.json()
    
    async def _run_translation(self, job: Job, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """Run translation for all target languages"""
        logger.info("Running translation", job_id=str(job.id))
        
        source_language = transcript.get("language", "en")
        target_languages = job.input_data["target_languages"]
        source_text = transcript["text"]
        
        translations = {}
        
        for target_lang in target_languages:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_services_base_url}:8002/translate",
                    json={
                        "text": source_text,
                        "source_language": source_language,
                        "target_language": target_lang
                    },
                    timeout=120
                )
                response.raise_for_status()
                translations[target_lang] = response.json()
        
        return translations
    
    async def _run_voice_synthesis(self, job: Job, translations: Dict[str, Any]) -> Dict[str, Any]:
        """Run voice synthesis for all translations"""
        logger.info("Running voice synthesis", job_id=str(job.id))
        
        settings_data = job.input_data["settings"]
        enable_voice_cloning = settings_data.get("enable_voice_cloning", True)
        
        audio_files = {}
        
        for lang, translation in translations.items():
            request_data = {
                "text": translation["translated_text"],
                "language": lang,
                "emotion": "neutral"
            }
            
            if enable_voice_cloning:
                # Use original video audio as reference
                request_data["speaker_wav"] = job.input_data["video_path"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_services_base_url}:8003/synthesize",
                    json=request_data,
                    timeout=180
                )
                response.raise_for_status()
                audio_files[lang] = response.json()
        
        return audio_files
    
    async def _run_face_animation(self, job: Job, audio_files: Dict[str, Any]) -> Dict[str, Any]:
        """Run face animation for all languages"""
        logger.info("Running face animation", job_id=str(job.id))
        
        video_path = job.input_data["video_path"]
        settings_data = job.input_data["settings"]
        quality_mode = settings_data.get("quality_mode", "structural")
        
        animated_videos = {}
        
        for lang, audio_data in audio_files.items():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_services_base_url}:8004/animate",
                    json={
                        "video_path": video_path,
                        "audio_path": audio_data["audio_path"],
                        "mode": quality_mode,
                        "preserve_pose": True,
                        "preserve_expression": settings_data.get("enable_emotion_preservation", True)
                    },
                    timeout=600
                )
                response.raise_for_status()
                animated_videos[lang] = response.json()
        
        return animated_videos
    
    async def _run_quality_checks(self, job: Job, videos: Dict[str, Any]) -> Dict[str, Any]:
        """Run quality checks on generated videos"""
        logger.info("Running quality checks", job_id=str(job.id))
        
        quality_results = {}
        
        for lang, video_data in videos.items():
            # This would call quality assessment services
            # For now, use mock results
            quality_results[lang] = {
                "lse_c": 0.87,  # Lip-sync accuracy
                "fid": 12.3,    # Visual fidelity
                "au_correlation": 0.78,  # Emotion preservation
                "bleu": 38.5,   # Translation quality
                "overall_score": 0.85
            }
        
        return quality_results
    
    async def _apply_ethical_safeguards(self, job: Job, videos: Dict[str, Any]) -> Dict[str, Any]:
        """Apply watermarking and other ethical safeguards"""
        logger.info("Applying ethical safeguards", job_id=str(job.id))
        
        project = job.project
        final_videos = {}
        
        for lang, video_data in videos.items():
            video_path = video_data["output_video_path"]
            
            # Apply watermarking if enabled
            if project.enable_watermarking:
                watermarked_path = await self.ethics_service.apply_watermark(
                    project_id=project.id,
                    content_path=video_path,
                    watermark_type="invisible"
                )
                video_data["output_video_path"] = watermarked_path
            
            # Update provenance record
            await self.ethics_service.update_provenance_record(
                project_id=project.id,
                processing_step={
                    "step": "face_animation",
                    "language": lang,
                    "model": "DAE-Talker",
                    "timestamp": datetime.utcnow().isoformat(),
                    "quality_metrics": video_data.get("quality_metrics", {})
                }
            )
            
            final_videos[lang] = video_data
        
        return final_videos
    
    async def get_job_progress(self, job_id: str) -> DubbingProgressResponse:
        """Get detailed progress for a dubbing job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Define pipeline stages
        stages = [
            {"name": "Ethics Check", "progress": 1.0 if job.progress > 0.1 else 0.0},
            {"name": "Speech Recognition", "progress": 1.0 if job.progress > 0.2 else 0.0},
            {"name": "Translation", "progress": 1.0 if job.progress > 0.4 else 0.0},
            {"name": "Voice Synthesis", "progress": 1.0 if job.progress > 0.6 else 0.0},
            {"name": "Face Animation", "progress": 1.0 if job.progress > 0.8 else 0.0},
            {"name": "Quality Check", "progress": 1.0 if job.progress >= 1.0 else 0.0},
        ]
        
        # Determine current stage
        current_stage = "Initializing"
        for stage in stages:
            if stage["progress"] < 1.0:
                current_stage = stage["name"]
                break
        if job.progress >= 1.0:
            current_stage = "Completed"
        
        # Estimate remaining time
        estimated_time_remaining = None
        if job.started_at and job.progress > 0:
            elapsed = (datetime.utcnow() - job.started_at).total_seconds()
            if job.progress < 1.0:
                estimated_total = elapsed / job.progress
                estimated_time_remaining = int(estimated_total - elapsed)
        
        return DubbingProgressResponse(
            job_id=str(job.id),
            overall_progress=job.progress,
            current_stage=current_stage,
            stages=stages,
            estimated_time_remaining=estimated_time_remaining,
            quality_metrics=job.quality_metrics
        )
    
    async def cancel_job(self, job_id: str):
        """Cancel a running job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        job.cancel()
        self.db.commit()
        
        logger.info("Job cancelled", job_id=job_id)
    
    async def generate_preview(
        self,
        job_id: str,
        language: str,
        segment_id: Optional[str] = None
    ) -> str:
        """Generate preview for a specific language/segment"""
        # This would generate a quick preview of the dubbed content
        # For now, return a mock URL
        return f"https://preview.example.com/{job_id}/{language}"