#!/usr/bin/env python3
"""
Vision2Code AI - Complete Application Startup Script
This script automatically starts both the FastAPI backend and Streamlit frontend.
"""

import os
import sys
import time
import subprocess
import signal
import threading
import requests
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Vision2CodeStarter:
    """Main application starter class"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8501"
        self.backend_port = 8000
        self.frontend_port = 8501
        
    def print_header(self):
        """Print application header"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("=" * 70)
        print("🚀 VISION2CODE AI - COMPLETE APPLICATION STARTER")
        print("=" * 70)
        print(f"{Colors.ENDC}")
        print(f"{Colors.OKCYAN}This script will automatically start:{Colors.ENDC}")
        print(f"  🔧 FastAPI Backend (Port {self.backend_port})")
        print(f"  🌐 Streamlit Frontend (Port {self.frontend_port})")
        print(f"  📊 Figma Integration Service")
        print(f"  🖼️  Image Analysis Pipeline")
        print()
        
    def check_dependencies(self):
        """Check if required packages are installed"""
        print(f"{Colors.OKBLUE}🔍 Checking dependencies...{Colors.ENDC}")
        
        required_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'requests', 
            'pillow', 'matplotlib', 'numpy'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")
        
        if missing_packages:
            print(f"\n{Colors.FAIL}❌ Missing packages: {', '.join(missing_packages)}{Colors.ENDC}")
            print(f"{Colors.WARNING}💡 Install missing packages with: pip install {' '.join(missing_packages)}{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKGREEN}✅ All dependencies are available{Colors.ENDC}\n")
        return True
    
    def check_ports(self):
        """Check if required ports are available"""
        print(f"{Colors.OKBLUE}🔍 Checking port availability...{Colors.ENDC}")
        
        import socket
        
        ports_to_check = [self.backend_port, self.frontend_port]
        available_ports = []
        
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('localhost', port))
                available_ports.append(port)
                print(f"  ✅ Port {port} is available")
                sock.close()
            except OSError:
                print(f"  ❌ Port {port} is already in use")
            finally:
                sock.close()
        
        if len(available_ports) != len(ports_to_check):
            print(f"\n{Colors.WARNING}⚠️  Some ports are already in use{Colors.ENDC}")
            print(f"{Colors.WARNING}💡 You may need to stop other services using these ports{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKGREEN}✅ All required ports are available{Colors.ENDC}\n")
        return True
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print(f"{Colors.OKBLUE}🚀 Starting FastAPI Backend...{Colors.ENDC}")
        
        try:
            # Start backend server
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", str(self.backend_port),
                "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"  📡 Backend process started (PID: {self.backend_process.pid})")
            
            # Wait for backend to be ready
            print(f"  ⏳ Waiting for backend to be ready...")
            for attempt in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"  ✅ Backend is ready at {self.backend_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                if attempt % 5 == 0:
                    print(f"    Still waiting... ({attempt + 1}/30)")
            
            print(f"  ❌ Backend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print(f"{Colors.OKBLUE}🌐 Starting Streamlit Frontend...{Colors.ENDC}")
        
        try:
            # Start frontend server
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                "web/ui_inspector.py",
                "--server.port", str(self.frontend_port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"  📱 Frontend process started (PID: {self.frontend_process.pid})")
            
            # Wait for frontend to be ready
            print(f"  ⏳ Waiting for frontend to be ready...")
            for attempt in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.frontend_url}", timeout=2)
                    if response.status_code == 200:
                        print(f"  ✅ Frontend is ready at {self.frontend_url}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                if attempt % 5 == 0:
                    print(f"    Still waiting... ({attempt + 1}/30)")
            
            print(f"  ❌ Frontend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
            return False
    
    def monitor_services(self):
        """Monitor running services and show status"""
        print(f"\n{Colors.OKGREEN}🎉 APPLICATION STARTED SUCCESSFULLY!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}📊 Service Status:{Colors.ENDC}")
        print(f"  🔧 Backend:  {Colors.OKGREEN}RUNNING{Colors.ENDC} at {self.backend_url}")
        print(f"  🌐 Frontend: {Colors.OKGREEN}RUNNING{Colors.ENDC} at {self.frontend_url}")
        
        print(f"\n{Colors.BOLD}🌐 Access Your Application:{Colors.ENDC}")
        print(f"  📱 Main UI:     {Colors.OKCYAN}{self.frontend_url}{Colors.ENDC}")
        print(f"  📚 API Docs:    {Colors.OKCYAN}{self.backend_url}/docs{Colors.ENDC}")
        print(f"  🔍 Health Check: {Colors.OKCYAN}{self.backend_url}/health{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}💡 Features Available:{Colors.ENDC}")
        print(f"  🖼️  Image Analysis: Upload UI screenshots for component detection")
        print(f"  🎨 Figma Integration: Connect to Figma and analyze design files")
        print(f"  📊 Component Extraction: Get structured JSON of UI layouts")
        print(f"  🌳 Tree Visualization: View hierarchical component structures")
        
        print(f"\n{Colors.BOLD}⚠️  Important Notes:{Colors.ENDC}")
        print(f"  • Keep this terminal open to monitor services")
        print(f"  • Press Ctrl+C to stop all services")
        print(f"  • Backend auto-reloads on code changes")
        print(f"  • Frontend updates automatically")
        
        print(f"\n{Colors.OKGREEN}🚀 Happy coding with Vision2Code AI!{Colors.ENDC}")
        print("=" * 70)
    
    def cleanup(self):
        """Clean up running processes"""
        print(f"\n{Colors.WARNING}🛑 Stopping services...{Colors.ENDC}")
        
        if self.backend_process:
            print(f"  🔧 Stopping backend (PID: {self.backend_process.pid})")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print(f"  🌐 Stopping frontend (PID: {self.frontend_process.pid})")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print(f"{Colors.OKGREEN}✅ All services stopped{Colors.ENDC}")
    
    def run(self):
        """Main execution method"""
        try:
            # Print header
            self.print_header()
            
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Check ports
            if not self.check_ports():
                return False
            
            # Start backend
            if not self.start_backend():
                return False
            
            # Start frontend
            if not self.start_frontend():
                return False
            
            # Monitor services
            self.monitor_services()
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        print(f"{Colors.FAIL}❌ Backend process stopped unexpectedly{Colors.ENDC}")
                        break
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print(f"{Colors.FAIL}❌ Frontend process stopped unexpectedly{Colors.ENDC}")
                        break
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}🛑 Received interrupt signal{Colors.ENDC}")
            
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    starter = Vision2CodeStarter()
    success = starter.run()
    
    if success:
        print(f"\n{Colors.OKGREEN}✅ Application shutdown completed successfully{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}❌ Application startup failed{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
