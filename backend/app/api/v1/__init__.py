"""
API v1 routes
"""

from fastapi import APIRouter

# Create a simple router that works without all dependencies
api_router = APIRouter()

# Import endpoints with error handling
try:
    from .endpoints import (
        auth, users, projects, jobs, media, 
        translation, voice, dubbing, ethics, health
    )
    
    # Include all endpoint routers
    api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
    api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    api_router.include_router(media.router, prefix="/media", tags=["media"])
    api_router.include_router(translation.router, prefix="/translation", tags=["translation"])
    api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
    api_router.include_router(dubbing.router, prefix="/dubbing", tags=["dubbing"])
    api_router.include_router(ethics.router, prefix="/ethics", tags=["ethics"])
    api_router.include_router(health.router, prefix="/health", tags=["health"])
    
except ImportError as e:
    print(f"Warning: Could not import all endpoints: {e}")
    # Create minimal health endpoint
    @api_router.get("/health")
    async def basic_health():
        return {"status": "ok", "message": "Basic health check"}