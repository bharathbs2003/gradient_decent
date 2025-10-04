"""
Base service class for AI microservices
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

import torch
import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import AIServiceConfig


logger = structlog.get_logger()


class ServiceHealth(BaseModel):
    """Service health status"""
    status: str
    service: str
    version: str
    uptime: float
    gpu_available: bool
    memory_usage: Dict[str, float]


class BaseAIService(ABC):
    """Base class for AI microservices"""
    
    def __init__(self, config: AIServiceConfig):
        self.config = config
        self.start_time = time.time()
        self.model = None
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO if not config.debug else logging.DEBUG)
        self.logger = structlog.get_logger(service=config.service_name)
        
        self.logger.info(
            "Initializing AI service",
            service=config.service_name,
            device=str(self.device),
            debug=config.debug
        )
    
    @abstractmethod
    async def load_model(self):
        """Load the AI model"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data with the AI model"""
        pass
    
    async def health_check(self) -> ServiceHealth:
        """Get service health status"""
        uptime = time.time() - self.start_time
        
        # Get memory usage
        memory_usage = {}
        if torch.cuda.is_available():
            memory_usage["gpu_allocated"] = torch.cuda.memory_allocated() / 1024**3  # GB
            memory_usage["gpu_reserved"] = torch.cuda.memory_reserved() / 1024**3  # GB
        
        import psutil
        process = psutil.Process()
        memory_usage["cpu_memory"] = process.memory_info().rss / 1024**3  # GB
        
        return ServiceHealth(
            status="healthy" if self.model is not None else "loading",
            service=self.config.service_name,
            version="1.0.0",
            uptime=uptime,
            gpu_available=torch.cuda.is_available(),
            memory_usage=memory_usage
        )
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("Starting AI service", service=self.config.service_name)
            await self.load_model()
            self.logger.info("AI service ready", service=self.config.service_name)
            yield
            # Shutdown
            self.logger.info("Shutting down AI service", service=self.config.service_name)
        
        app = FastAPI(
            title=f"{self.config.service_name.upper()} AI Service",
            description=f"AI microservice for {self.config.service_name}",
            version="1.0.0",
            lifespan=lifespan
        )
        
        @app.get("/health", response_model=ServiceHealth)
        async def health():
            """Health check endpoint"""
            return await self.health_check()
        
        @app.post("/process")
        async def process_endpoint(input_data: Dict[str, Any]):
            """Main processing endpoint"""
            try:
                start_time = time.time()
                result = await self.process(input_data)
                processing_time = time.time() - start_time
                
                self.logger.info(
                    "Processing completed",
                    service=self.config.service_name,
                    processing_time=processing_time
                )
                
                return {
                    "result": result,
                    "processing_time": processing_time,
                    "service": self.config.service_name
                }
                
            except Exception as e:
                self.logger.error(
                    "Processing failed",
                    service=self.config.service_name,
                    error=str(e)
                )
                raise HTTPException(status_code=500, detail=str(e))
        
        return app
    
    def run(self):
        """Run the service"""
        import uvicorn
        
        app = self.create_app()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=self.config.service_port,
            workers=1,  # Single worker for GPU services
            log_level="info" if not self.config.debug else "debug"
        )