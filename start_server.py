#!/usr/bin/env python3
"""
Startup script for Vision2Code AI FastAPI server with proper timeout configurations
"""

import uvicorn
import os
import sys

def main():
    """Start the FastAPI server with optimized settings"""
    
    # Server configuration
    config = {
        "host": "0.0.0.0",  # Allow external connections
        "port": 8000,
        "reload": True,  # Auto-reload on code changes
        "workers": 1,  # Single worker for development
        "timeout_keep_alive": 120,  # Keep-alive timeout
        "timeout_graceful_shutdown": 30,  # Graceful shutdown timeout
        "log_level": "info",
        "access_log": True,
    }
    
    print("🚀 Starting Vision2Code AI FastAPI Server...")
    print(f"📍 Server will be available at: http://localhost:{config['port']}")
    print(f"📚 API Documentation: http://localhost:{config['port']}/docs")
    print(f"🔧 Health Check: http://localhost:{config['port']}/health")
    print("=" * 60)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            **config
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
