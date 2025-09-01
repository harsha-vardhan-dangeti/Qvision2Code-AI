#!/usr/bin/env python3
"""
Startup script for Vision2Code AI with Figma Integration
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'requests',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are available")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not available, using system environment")
        
        # Check Figma access token
        access_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if access_token and access_token != "your_figma_access_token_here":
            print("✅ FIGMA_ACCESS_TOKEN is configured")
        else:
            print("⚠️  FIGMA_ACCESS_TOKEN not properly configured")
            print("   Please set a valid Figma access token in your .env file")
            return False
    else:
        print("⚠️  .env file not found")
        print("   Copy env_template.txt to .env and configure your settings")
        return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Vision2Code AI server with Figma integration...")
    
    # Check if virtual environment exists
    venv_path = os.path.join(os.getcwd(), 'myenv')
    if os.path.exists(venv_path):
        print("✅ Virtual environment found, activating...")
        # Activate virtual environment
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
            cmd = ['cmd', '/c', f'"{activate_script}" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload']
        else:  # Unix/Linux/macOS
            activate_script = os.path.join(venv_path, 'bin', 'activate')
            cmd = ['bash', '-c', f'source "{activate_script}" && cd app && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload']
    else:
        print("⚠️  Virtual environment not found, using system Python")
        cmd = [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
        os.chdir('app')
    
    print(f"Running: {' '.join(cmd)}")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Figma endpoints: http://localhost:8000/figma/*")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🎯 Vision2Code AI - Figma Integration Service")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return 1
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please configure your .env file.")
        return 1
    
    print("\n✅ All checks passed!")
    
    # Start server
    start_server()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
