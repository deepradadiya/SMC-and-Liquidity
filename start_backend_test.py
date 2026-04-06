#!/usr/bin/env python3
"""
Start the backend server for testing
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    print("Starting SMC Trading System Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env.update({
            'APP_ENV': 'development',
            'HOST': '0.0.0.0',
            'PORT': '8000',
            'LOG_LEVEL': 'INFO'
        })
        
        # Start backend process from backend directory
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ], cwd='backend', env=env)
        
        print(f"Backend process ID: {process.pid}")
        print("Starting up...")
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n👋 Stopping backend...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Backend stopped gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("🔪 Backend force killed")
        
    except Exception as e:
        print(f"❌ Server error: {e}")