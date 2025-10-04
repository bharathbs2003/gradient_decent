#!/usr/bin/env python3
"""
Simple test script to diagnose server issues
"""

import sys
import os
import traceback

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all imports to identify issues"""
    print("Testing imports...")
    
    try:
        print("✓ Testing FastAPI...")
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")
    except Exception as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        print("✓ Testing Pydantic...")
        from pydantic import BaseModel
        print("✓ Pydantic imported successfully")
    except Exception as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    try:
        print("✓ Testing app.main...")
        from app.main import app
        print("✓ Main app imported successfully")
        return True
    except Exception as e:
        print(f"✗ Main app import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_server():
    """Test basic server functionality"""
    print("\nTesting basic server...")
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Create minimal app
        test_app = FastAPI()
        
        @test_app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        @test_app.get("/health")
        def health():
            return {"status": "ok"}
        
        client = TestClient(test_app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"✓ Root endpoint: {response.status_code} - {response.json()}")
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✓ Health endpoint: {response.status_code} - {response.json()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic server test failed: {e}")
        traceback.print_exc()
        return False

def create_minimal_app():
    """Create a minimal working app"""
    print("\nCreating minimal working app...")
    
    minimal_app_code = '''"""
Minimal working FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Multilingual AI Video Dubbing Platform",
    description="AI-powered multilingual video dubbing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multilingual AI Video Dubbing Platform",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "api_version": "v1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    try:
        with open('backend/app/minimal_main.py', 'w') as f:
            f.write(minimal_app_code)
        print("✓ Created minimal_main.py")
        return True
    except Exception as e:
        print(f"✗ Failed to create minimal app: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Diagnosing server issues...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Creating minimal app...")
        create_minimal_app()
        print("\n💡 Try running: cd backend && python -m app.minimal_main")
        return
    
    # Test basic server
    if not test_basic_server():
        print("\n❌ Basic server test failed")
        return
    
    print("\n✅ All tests passed! The server should work.")
    print("\n🚀 To start the server:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()