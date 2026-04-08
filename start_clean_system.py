#!/usr/bin/env python3
"""
Clean System Starter - Starts backend and frontend without terminal mess
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

class CleanSystemStarter:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_backend(self):
        """Start backend server quietly"""
        print("🚀 Starting backend server...")
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ Backend directory not found!")
            return False
            
        try:
            # Start backend with minimal output
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(("Backend", process))
            
            # Wait a moment and check if it started
            time.sleep(2)
            if process.poll() is None:
                print("✅ Backend server started on http://localhost:8000")
                return True
            else:
                print("❌ Backend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Backend start error: {e}")
            return False
    
    def start_frontend(self):
        """Start frontend development server"""
        print("🎨 Starting frontend server...")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found!")
            return False
            
        try:
            # Check if node_modules exists
            if not (frontend_dir / "node_modules").exists():
                print("📦 Installing frontend dependencies...")
                install_process = subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True
                )
                
                if install_process.returncode != 0:
                    print("❌ Failed to install dependencies")
                    return False
            
            # Start frontend with minimal output
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes.append(("Frontend", process))
            
            # Wait for frontend to start
            time.sleep(5)
            if process.poll() is None:
                print("✅ Frontend server started on http://localhost:3000")
                return True
            else:
                print("❌ Frontend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Frontend start error: {e}")
            return False
    
    def start_signal_monitor(self):
        """Start silent signal monitor"""
        print("🔍 Starting signal monitor...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "silent_signal_monitor.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            
            self.processes.append(("Signal Monitor", process))
            print("✅ Signal monitor started (will alert when signals found)")
            return True
            
        except Exception as e:
            print(f"❌ Signal monitor start error: {e}")
            return False
    
    def cleanup(self):
        """Clean shutdown of all processes"""
        print("\n🛑 Shutting down system...")
        
        for name, process in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"   Error stopping {name}: {e}")
        
        print("✅ System shutdown complete")
    
    def run(self):
        """Run the complete system"""
        print("🎯 SMC Trading System - Clean Startup")
        print("=" * 50)
        
        # Setup signal handler for clean shutdown
        def signal_handler(signum, frame):
            self.running = False
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start backend
            if not self.start_backend():
                return
            
            # Start frontend
            if not self.start_frontend():
                return
                
            print("\n" + "=" * 50)
            print("🎉 System Ready!")
            print("🌐 Frontend: http://localhost:3000")
            print("🔧 Backend API: http://localhost:8000")
            print("🔍 Signal monitoring active")
            print("\n💡 Tips:")
            print("   • Signals appear automatically in UI when found")
            print("   • Run 'python3 quick_signal_check.py' for status")
            print("   • Press Ctrl+C to stop system")
            print("=" * 50)
            
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} stopped unexpectedly")
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    starter = CleanSystemStarter()
    starter.run()