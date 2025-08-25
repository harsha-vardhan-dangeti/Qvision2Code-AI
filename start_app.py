#!/usr/bin/env python3
"""
Vision2Code AI Startup Script
Launches both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    try:
        # Change to app directory
        os.chdir("app")
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Backend started successfully")
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🌐 Starting Streamlit frontend...")
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "../web/ui_inspector.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ]
    
    try:
        # Change to web directory
        os.chdir("web")
        frontend_process = subprocess.Popen(
            frontend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Frontend started successfully")
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🔍 Vision2Code AI - Starting Application...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            sys.exit(1)
        
        # Wait a moment for backend to initialize
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            backend_process.terminate()
            sys.exit(1)
        
        # Return to original directory
        os.chdir(original_dir)
        
        print("\n" + "=" * 50)
        print("🎉 Vision2Code AI is now running!")
        print("📱 Frontend: http://localhost:8501")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("\nPress Ctrl+C to stop both services...")
        
        try:
            # Wait for processes
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)
    finally:
        # Ensure we're back in the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()

