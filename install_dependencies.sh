#!/bin/bash

echo "🔧 Installing Python dependencies for the Multilingual AI Video Dubbing Platform..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install basic dependencies
echo "📦 Installing basic Python packages..."
pip3 install --user fastapi uvicorn pydantic sqlalchemy alembic psycopg2-binary redis python-jose passlib python-multipart structlog

# Install additional dependencies
echo "📦 Installing additional packages..."
pip3 install --user python-dotenv loguru prometheus-client httpx

echo "✅ Basic dependencies installed!"
echo ""
echo "🚀 To start the server:"
echo "   cd backend"
echo "   python3 -m uvicorn app.minimal_main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Then visit: http://localhost:8000"