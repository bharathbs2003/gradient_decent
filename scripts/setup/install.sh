#!/bin/bash

# Multilingual AI Video Dubbing Platform - Installation Script
# This script sets up the complete platform with all dependencies

set -e

echo "🚀 Installing Multilingual AI Video Dubbing Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for NVIDIA Docker (for GPU support)
if command -v nvidia-docker &> /dev/null || docker info | grep -q nvidia; then
    echo "✅ NVIDIA Docker detected - GPU acceleration will be available"
    GPU_SUPPORT=true
else
    echo "⚠️  NVIDIA Docker not detected - running in CPU-only mode"
    echo "For GPU acceleration, install NVIDIA Docker: https://github.com/NVIDIA/nvidia-docker"
    GPU_SUPPORT=false
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads models logs deployment/nginx/ssl

# Set permissions
chmod 755 uploads models logs

# Generate environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://dubbing_user:dubbing_password@postgres:5432/dubbing_platform
POSTGRES_DB=dubbing_platform
POSTGRES_USER=dubbing_user
POSTGRES_PASSWORD=dubbing_password

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Security
SECRET_KEY=$(openssl rand -hex 32)

# AI Services
AI_SERVICES_BASE_URL=http://ai-gateway:8001

# Application
DEBUG=false
CORS_ORIGINS=["http://localhost:3000", "http://localhost"]
ALLOWED_HOSTS=["*"]

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=524288000  # 500MB

# Quality Targets (from PRD)
TARGET_LSE_C=0.85
TARGET_FID=15.0
TARGET_AU_CORRELATION=0.75
TARGET_BLEU=35.0

# Ethics
ENABLE_WATERMARKING=true
ENABLE_CONSENT_TRACKING=true
ENABLE_PROVENANCE=true
WATERMARK_STRENGTH=0.1

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
    echo "✅ Environment file created (.env)"
    echo "🔧 Please review and update the .env file with your specific settings"
fi

# Create Docker Compose override for CPU-only mode if needed
if [ "$GPU_SUPPORT" = false ]; then
    echo "📝 Creating CPU-only Docker Compose override..."
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  asr-service:
    deploy:
      resources: {}
    environment:
      - CUDA_VISIBLE_DEVICES=""
      - DEVICE=cpu

  translation-service:
    deploy:
      resources: {}
    environment:
      - CUDA_VISIBLE_DEVICES=""
      - DEVICE=cpu

  tts-service:
    deploy:
      resources: {}
    environment:
      - CUDA_VISIBLE_DEVICES=""
      - DEVICE=cpu

  face-animation-service:
    deploy:
      resources: {}
    environment:
      - CUDA_VISIBLE_DEVICES=""
      - DEVICE=cpu
EOF
fi

# Pull base images
echo "📦 Pulling base Docker images..."
docker-compose pull postgres redis nginx prometheus grafana

# Build services
echo "🔨 Building application services..."
docker-compose build --parallel

# Initialize database
echo "🗃️  Initializing database..."
docker-compose up -d postgres redis
sleep 10

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose run --rm backend python -c "
from app.core.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Download AI models (this would be a separate script in production)
echo "🤖 Preparing AI models..."
echo "ℹ️  AI models will be downloaded on first use"
echo "ℹ️  This may take some time depending on your internet connection"

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
echo "🏥 Running health checks..."

check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start"
    return 1
}

# Check core services
check_service "Backend API" "http://localhost:8000/health"
check_service "Frontend" "http://localhost:3000"

# Check AI services (may take longer to load models)
echo "🤖 Checking AI services (this may take a while for model loading)..."
check_service "ASR Service" "http://localhost:8001/health" || echo "⚠️  ASR service not ready (models may still be loading)"
check_service "Translation Service" "http://localhost:8002/health" || echo "⚠️  Translation service not ready"
check_service "TTS Service" "http://localhost:8003/health" || echo "⚠️  TTS service not ready"
check_service "Face Animation Service" "http://localhost:8004/health" || echo "⚠️  Face Animation service not ready"

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📊 Access your services:"
echo "   • Frontend:              http://localhost:3000"
echo "   • Backend API:           http://localhost:8000"
echo "   • API Documentation:     http://localhost:8000/docs"
echo "   • Celery Flower:         http://localhost:5555"
echo "   • Prometheus:            http://localhost:9090"
echo "   • Grafana:               http://localhost:3001 (admin/admin)"
echo ""
echo "📝 Next steps:"
echo "   1. Visit http://localhost:3000 to access the platform"
echo "   2. Create an account and start dubbing!"
echo "   3. Monitor services at http://localhost:3001 (Grafana)"
echo ""
echo "🔧 To stop all services: docker-compose down"
echo "🔧 To view logs: docker-compose logs -f [service-name]"
echo "🔧 To restart: docker-compose restart [service-name]"
echo ""
echo "📚 For more information, see the README.md file"