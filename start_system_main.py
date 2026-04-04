#!/usr/bin/env python3
"""
SMC Trading System - Main Branch Startup
Starts the perfect backend from main branch with new UI
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_requirements():
    """Check if required dependencies are installed"""
    print("🔍 Checking requirements...")
    
    # Check if we're in globalvenv
    if 'globalvenv' in sys.executable:
        print("✅ Using globalvenv environment")
    else:
        print("⚠️  Not in globalvenv - activating it is recommended")
    
    # Check Python dependencies
    try:
        import uvicorn
        import fastapi
        import ccxt
        print("✅ Python backend dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Run: pip install -r backend/requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        print("💡 Install Node.js from https://nodejs.org/")
        return False
    
    # Check if frontend dependencies are installed
    if not (Path("frontend/node_modules").exists()):
        print("❌ Frontend dependencies not installed")
        print("💡 Run: cd frontend && npm install --legacy-peer-deps")
        return False
    else:
        print("✅ Frontend dependencies found")
    
    return True

def start_backend():
    """Start the main branch backend server"""
    print("🚀 Starting main branch backend server...")
    
    backend_env = os.environ.copy()
    backend_env.update({
        'APP_ENV': 'development',
        'HOST': '0.0.0.0',
        'PORT': '8000',
        'LOG_LEVEL': 'INFO',
        'ALLOWED_ORIGINS': 'http://localhost:3000,http://localhost:5173'
    })
    
    backend_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ], cwd='backend', env=backend_env)
    
    return backend_process

def start_frontend():
    """Start the new frontend"""
    print("🎨 Starting new modern frontend...")
    
    frontend_env = os.environ.copy()
    frontend_env.update({
        'REACT_APP_BACKEND_URL': 'http://localhost:8000',
        'PORT': '3000'
    })
    
    frontend_process = subprocess.Popen([
        'npm', 'start'
    ], cwd='frontend', env=frontend_env)
    
    return frontend_process

def main():
    """Main startup function"""
    print("🔥 SMC Trading System - Main Branch with New UI")
    print("=" * 55)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing dependencies.")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Wait a moment for backend to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("\n🎉 System started successfully!")
        print("📊 Backend API: http://localhost:8000")
        print("🎨 Frontend UI: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n✨ Features Available:")
        print("  • Modern UI with all 10 modules")
        print("  • MTF Confluence Analysis")
        print("  • Risk Management System")
        print("  • Precise SMC Analysis")
        print("  • Advanced Backtesting")
        print("  • ML Signal Filter")
        print("  • Session Management")
        print("  • Alert System")
        print("  • Data Management")
        print("  • Authentication & Security")
        print("\n💡 Press Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if any process died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"\n❌ Process {i} died with code {process.returncode}")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()