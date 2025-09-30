#!/usr/bin/env python3
"""
Vision2Code AI - Simple Startup Script
One-click startup for both backend and frontend
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "app/main.py",
        "web/ui_inspector.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file not found: {file}")
            return False
    
    return True

def check_virtual_env():
    """Check if virtual environment exists"""
    venv_path = Path("myenv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run:")
        print("   python3 -m venv myenv")
        print("   source myenv/bin/activate")
        print("   pip install -r requirements.txt")
        return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    
    # Activate virtual environment and start backend
    if os.name == 'nt':  # Windows
        cmd = ["myenv\\Scripts\\python.exe", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    else:  # Unix/Linux/Mac
        cmd = ["myenv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    
    # Activate virtual environment and start frontend
    if os.name == 'nt':  # Windows
        cmd = ["myenv\\Scripts\\streamlit", "run", "web/ui_inspector.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    else:  # Unix/Linux/Mac
        cmd = ["myenv/bin/streamlit", "run", "web/ui_inspector.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def wait_for_service(port, service_name, timeout=30):
    """Wait for a service to be ready"""
    import socket
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"✅ {service_name} is ready on port {port}")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ {service_name} failed to start within {timeout} seconds")
    return False

def cleanup_processes(processes):
    """Clean up running processes"""
    print("\n🛑 Shutting down services...")
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    """Main startup function"""
    print("🎯 Vision2Code AI - Starting Application")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    if not check_virtual_env():
        sys.exit(1)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Wait for backend to be ready
        if not wait_for_service(8000, "Backend"):
            cleanup_processes(processes)
            sys.exit(1)
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        # Wait for frontend to be ready
        if not wait_for_service(8501, "Frontend"):
            cleanup_processes(processes)
            sys.exit(1)
        
        print("\n🎉 Vision2Code AI is running!")
        print("=" * 50)
        print("📍 Frontend (UI): http://localhost:8501")
        print("📍 Backend (API): http://localhost:8000")
        print("📍 API Docs: http://localhost:8000/docs")
        print("📍 Health Check: http://localhost:8000/health")
        print("=" * 50)
        print("Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            # Check if processes are still running
            for process in processes:
                if process.poll() is not None:
                    print(f"❌ A service has stopped unexpectedly")
                    cleanup_processes(processes)
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
        cleanup_processes(processes)
        print("✅ All services stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_processes(processes)
        sys.exit(1)

if __name__ == "__main__":
    main()
