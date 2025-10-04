#!/usr/bin/env python3
"""
Startup script for the Multilingual AI Video Dubbing Platform
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: ./install_dependencies.sh")
        return False

def start_minimal_server(port=8000, host="0.0.0.0"):
    """Start the minimal server"""
    print(f"🚀 Starting minimal server on {host}:{port}")
    
    os.chdir("backend")
    
    try:
        # Try to use the full main app first
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", 
               "--host", host, "--port", str(port), "--reload"]
        
        print("Attempting to start full application...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit to see if it starts successfully
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Full application started successfully!")
            return process
        else:
            stdout, stderr = process.communicate()
            print("⚠️  Full application failed, trying minimal version...")
            print(f"Error: {stderr.decode()}")
            
    except Exception as e:
        print(f"⚠️  Could not start full app: {e}")
    
    # Fallback to minimal app
    try:
        cmd = [sys.executable, "-m", "uvicorn", "app.minimal_main:app", 
               "--host", host, "--port", str(port), "--reload"]
        
        print("Starting minimal application...")
        process = subprocess.Popen(cmd)
        
        time.sleep(2)
        print("✅ Minimal application started!")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start minimal app: {e}")
        return None

def start_frontend(port=3000):
    """Start the frontend development server"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found")
        return None
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return None
        except FileNotFoundError:
            print("⚠️  Node.js not found. Please install Node.js to run the frontend.")
            return None
    
    try:
        print(f"🎨 Starting frontend on port {port}")
        cmd = ["npm", "run", "dev"]
        process = subprocess.Popen(cmd, cwd=frontend_dir)
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Start the Multilingual AI Video Dubbing Platform")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=3000, help="Frontend port (default: 3000)")
    parser.add_argument("--host", default="0.0.0.0", help="Backend host (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    print("🎬 Multilingual AI Video Dubbing Platform")
    print("=" * 50)
    
    if not check_dependencies():
        return 1
    
    processes = []
    
    try:
        # Start backend
        if not args.frontend_only:
            backend_process = start_minimal_server(args.port, args.host)
            if backend_process:
                processes.append(("Backend", backend_process))
                print(f"🌐 Backend available at: http://localhost:{args.port}")
                print(f"📖 API docs at: http://localhost:{args.port}/docs")
        
        # Start frontend
        if not args.backend_only:
            frontend_process = start_frontend(args.frontend_port)
            if frontend_process:
                processes.append(("Frontend", frontend_process))
                print(f"🎨 Frontend available at: http://localhost:{args.frontend_port}")
        
        if not processes:
            print("❌ No services started successfully")
            return 1
        
        print("\n✅ Platform started successfully!")
        print("\n🔧 Controls:")
        print("   • Press Ctrl+C to stop all services")
        print("   • Check logs above for any errors")
        
        # Wait for processes
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} process has stopped")
        
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    finally:
        # Clean up processes
        for name, process in processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"Error stopping {name}: {e}")
    
    print("👋 All services stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())