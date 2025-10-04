"""
Main dubbing endpoints - the core functionality of the platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.exceptions import *
from app.models import User, Project, Job, MediaFile
from app.schemas.dubbing import *
from app.services.dubbing import DubbingService
from app.api.deps import get_current_user

logger = structlog.get_logger()
router = APIRouter()


@router.post("/process", response_model=DubbingJobResponse)
async def create_dubbing_job(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    target_languages: str = Form(...),  # JSON string of language codes
    source_language: Optional[str] = Form(None),
    enable_voice_cloning: bool = Form(True),
    enable_emotion_preservation: bool = Form(True),
    quality_mode: str = Form("structural"),  # structural or end_to_end
    require_human_review: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new dubbing job for multilingual video processing.
    
    This is the main endpoint that orchestrates the entire dubbing pipeline:
    1. Input processing and validation
    2. ASR (Automatic Speech Recognition)
    3. Translation to target languages
    4. Voice synthesis/cloning
    5. Facial re-animation
    6. Final video rendering
    7. Quality checks and ethical safeguards
    """
    try:
        # Parse target languages
        import json
        target_langs = json.loads(target_languages)
        
        # Validate input
        if not target_langs:
            raise ValidationError("At least one target language is required")
        
        # Create dubbing request
        request = DubbingRequest(
            target_languages=target_langs,
            source_language=source_language,
            enable_voice_cloning=enable_voice_cloning,
            enable_emotion_preservation=enable_emotion_preservation,
            quality_mode=quality_mode,
            require_human_review=require_human_review
        )
        
        # Initialize dubbing service
        dubbing_service = DubbingService(db)
        
        # Create and start dubbing job
        job = await dubbing_service.create_dubbing_job(
            user=current_user,
            video_file=video_file,
            request=request
        )
        
        # Start processing in background
        background_tasks.add_task(
            dubbing_service.process_dubbing_job,
            job.id
        )
        
        logger.info(
            "Dubbing job created",
            job_id=str(job.id),
            user_id=str(current_user.id),
            target_languages=target_langs
        )
        
        return DubbingJobResponse.from_orm(job)
        
    except json.JSONDecodeError:
        raise ValidationError("Invalid target_languages format")
    except Exception as e:
        logger.error("Failed to create dubbing job", error=str(e))
        raise DubbingException(f"Failed to create dubbing job: {str(e)}")


@router.get("/jobs/{job_id}", response_model=DubbingJobResponse)
async def get_dubbing_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dubbing job status and results"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    return DubbingJobResponse.from_orm(job)


@router.get("/jobs/{job_id}/progress", response_model=DubbingProgressResponse)
async def get_dubbing_progress(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed progress information for a dubbing job"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    dubbing_service = DubbingService(db)
    progress = await dubbing_service.get_job_progress(job_id)
    
    return progress


@router.post("/jobs/{job_id}/cancel")
async def cancel_dubbing_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a running dubbing job"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    if not job.is_active:
        raise ValidationError("Job is not active and cannot be cancelled")
    
    dubbing_service = DubbingService(db)
    await dubbing_service.cancel_job(job_id)
    
    logger.info("Dubbing job cancelled", job_id=job_id, user_id=str(current_user.id))
    
    return {"message": "Job cancelled successfully"}


@router.post("/jobs/{job_id}/retry")
async def retry_dubbing_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry a failed dubbing job"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    if not job.can_retry:
        raise ValidationError("Job cannot be retried")
    
    dubbing_service = DubbingService(db)
    
    # Retry the job
    job.retry()
    db.commit()
    
    # Start processing in background
    background_tasks.add_task(
        dubbing_service.process_dubbing_job,
        job.id
    )
    
    logger.info("Dubbing job retried", job_id=job_id, user_id=str(current_user.id))
    
    return {"message": "Job retry initiated"}


@router.get("/jobs", response_model=List[DubbingJobResponse])
async def list_dubbing_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's dubbing jobs"""
    query = db.query(Job).filter(Job.user_id == current_user.id)
    
    if status:
        query = query.filter(Job.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    
    return [DubbingJobResponse.from_orm(job) for job in jobs]


@router.get("/preview/{job_id}")
async def get_dubbing_preview(
    job_id: str,
    language: str,
    segment_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time preview of dubbed content.
    
    Supports previewing specific segments or the full video
    in a target language with <5 second latency for short clips.
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    dubbing_service = DubbingService(db)
    preview_url = await dubbing_service.generate_preview(
        job_id=job_id,
        language=language,
        segment_id=segment_id
    )
    
    return {"preview_url": preview_url, "expires_in": 3600}


@router.post("/quality-check/{job_id}", response_model=QualityCheckResponse)
async def run_quality_check(
    job_id: str,
    check_request: QualityCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run quality checks on dubbed content.
    
    Evaluates:
    - Lip-sync accuracy (LSE-C ≥ 0.85)
    - Visual fidelity (FID ≤ 15)
    - Emotion preservation (AU correlation ≥ 0.75)
    - Translation quality (BLEU ≥ 35)
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise NotFoundError("Dubbing job")
    
    if not job.is_completed:
        raise ValidationError("Job must be completed before quality check")
    
    dubbing_service = DubbingService(db)
    quality_results = await dubbing_service.run_quality_check(job_id, check_request)
    
    return quality_results


@router.get("/supported-languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Get list of supported languages with capabilities"""
    from app.core.config import get_settings
    settings = get_settings()
    
    # This would typically come from a service or database
    languages = []
    for lang_code in settings.SUPPORTED_LANGUAGES:
        # Mock language info - in reality this would be fetched from a service
        lang_info = LanguageInfo(
            code=lang_code,
            name=f"Language {lang_code.upper()}",
            native_name=f"Native {lang_code.upper()}",
            supports_asr=True,
            supports_tts=True,
            supports_translation=True,
            voice_count=10  # Mock voice count
        )
        languages.append(lang_info)
    
    return languages


@router.get("/models/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about AI models used in the pipeline"""
    from app.core.config import get_settings
    settings = get_settings()
    
    return ModelInfoResponse(
        asr_model=settings.WHISPER_MODEL,
        translation_model=settings.TRANSLATION_MODEL,
        tts_model=settings.TTS_MODEL,
        face_model=settings.FACE_MODEL,
        expression_model=settings.EXPRESSION_MODEL,
        renderer_model=settings.RENDERER_MODEL,
        model_versions={
            "whisper": "large-v3",
            "seamlessM4T": "v1.0",
            "VITS": "v2.0",
            "FLAME": "v1.0",
            "DAE-Talker": "v1.0"
        }
    )