"""
Database models for the Multilingual AI Video Dubbing Platform
"""

# Import all models to ensure they are registered with SQLAlchemy
try:
    from .user import User, UserRole
    from .project import Project, ProjectStatus
    from .job import Job, JobStatus, JobType
    from .media import MediaFile, MediaType
    from .translation import Translation, TranslationStatus
    from .voice import VoiceProfile, VoiceClone
    from .ethics import ConsentRecord, WatermarkRecord, ProvenanceRecord
except ImportError as e:
    # Handle import errors gracefully during development
    print(f"Warning: Could not import all models: {e}")

__all__ = [
    "User",
    "UserRole", 
    "Project",
    "ProjectStatus",
    "Job",
    "JobStatus",
    "JobType",
    "MediaFile",
    "MediaType",
    "Translation",
    "TranslationStatus",
    "VoiceProfile",
    "VoiceClone",
    "ConsentRecord",
    "WatermarkRecord",
    "ProvenanceRecord",
]