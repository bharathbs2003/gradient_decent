"""
Multilingual AI Video Dubbing Platform - Main FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from app.core.config import get_settings
from app.core.database import init_db
from app.api.v1 import api_router
from app.core.exceptions import DubbingException


logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Multilingual AI Video Dubbing Platform")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down application")


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

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

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
    logger.error("Dubbing error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.error_code}
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