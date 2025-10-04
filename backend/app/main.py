"""
Multilingual AI Video Dubbing Platform - Main FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os

# Try to import dependencies with fallbacks
try:
    from app.core.config import get_settings
    settings = get_settings()
except Exception as e:
    print(f"Warning: Could not load settings: {e}")
    # Create minimal settings
    class MockSettings:
        ALLOWED_HOSTS = ["*"]
        CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
        DEBUG = True
    settings = MockSettings()

try:
    from app.core.database import init_db
except Exception as e:
    print(f"Warning: Could not import database: {e}")
    async def init_db():
        print("Database initialization skipped")

try:
    from app.api.v1 import api_router
except Exception as e:
    print(f"Warning: Could not import API router: {e}")
    from fastapi import APIRouter
    api_router = APIRouter()
    
    @api_router.get("/health")
    async def health():
        return {"status": "ok", "message": "Minimal health check"}

try:
    from app.core.exceptions import DubbingException
except Exception as e:
    print(f"Warning: Could not import exceptions: {e}")
    class DubbingException(Exception):
        def __init__(self, message: str, status_code: int = 500):
            self.message = message
            self.status_code = status_code
            super().__init__(message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Multilingual AI Video Dubbing Platform")
    try:
        await init_db()
        print("Database initialization completed")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    yield
    # Shutdown
    print("Shutting down application")


app = FastAPI(
    title="Multilingual AI Video Dubbing Platform",
    description="""
    A comprehensive AI-powered platform for creating high-fidelity multilingual dubbed videos 
    with synchronized, realistic facial animations.
    
    ## Features
    
    * **Automated Dubbing Pipeline**: Reduce manual dubbing effort by ≥80%
    * **50+ Language Support**: Cover top spoken languages by internet users  
    * **High-Quality Lip Sync**: Achieve LSE-C ≥ 0.85 accuracy
    * **Real-time Preview**: <5 sec latency for short clips
    * **Ethical AI**: Embedded provenance and consent management
    """,
    version="1.0.0",
    contact={
        "name": "AI Dubbing Platform Team",
        "email": "support@aidubbing.ai",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# Security middleware (optional)
try:
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )
except Exception as e:
    print(f"Warning: Could not add TrustedHostMiddleware: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(DubbingException)
async def dubbing_exception_handler(request: Request, exc: DubbingException):
    """Handle custom dubbing exceptions"""
    print(f"Dubbing error: {exc.message} at {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": getattr(exc, 'error_code', 'DUBBING_ERROR')}
    )


@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "message": "Multilingual AI Video Dubbing Platform",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Automated dubbing pipeline",
            "50+ language support", 
            "High-quality lip sync",
            "Real-time preview",
            "Ethical AI safeguards"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )