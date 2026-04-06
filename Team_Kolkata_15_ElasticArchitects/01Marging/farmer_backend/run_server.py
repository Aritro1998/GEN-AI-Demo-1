#!/usr/bin/env python
"""
Startup script for Farmer Backend API
Runs the FastAPI server with uvicorn
"""
import subprocess
import sys
import time
import requests

def start_server():
    """Start the FastAPI server"""
    print("="*60)
    print("Starting Farmer Backend API Server...")
    print("="*60)
    print("\nServer will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Interactive API: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
            cwd="."
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)

if __name__ == "__main__":
    start_server()
