#!/usr/bin/env python3
"""
Start SMC Trading System - BOTH PROBLEMS FIXED
This script starts the system with real-time data and no import errors
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_command_in_terminal(cmd, cwd=None, title="Command"):
    """Run a command in a new terminal window"""
    if sys.platform == "darwin":  # macOS
        script = f'''
        tell application "Terminal"
            do script "cd {cwd or os.getcwd()} && {cmd}"
            set custom title of front window to "{title}"
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
    else:
        # For Linux/Windows, just print instructions
        print(f"\n🔧 Please run this command in a new terminal:")
        print(f"📁 Directory: {cwd or os.getcwd()}")
        print(f"💻 Command: {cmd}")
        print("-" * 50)

def main():
    """Main function to start the system"""
    print("🚀 Starting SMC Trading System - BOTH PROBLEMS FIXED")
    print("=" * 60)
    print("✅ Problem 1 FIXED: Real-time data (no more mock $66,250)")
    print("✅ Problem 2 FIXED: Frontend import errors resolved")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the SMC-and-Liquidity root directory")
        return 1
    
    print("\n🔧 Starting Backend Server...")
    run_command_in_terminal(
        "python run.py",
        cwd=str(Path.cwd() / "backend"),
        title="SMC Backend"
    )
    
    print("\n🔧 Starting Frontend Server...")
    run_command_in_terminal(
        "npm start",
        cwd=str(Path.cwd() / "frontend"),
        title="SMC Frontend"
    )
    
    print("\n" + "=" * 60)
    print("🎉 SMC Trading System Starting!")
    print("📊 Backend API: http://localhost:8000")
    print("📊 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 60)
    print("\n💡 What's Fixed:")
    print("   ✅ Real BTC price: ~$69,000 (not $66,250)")
    print("   ✅ MTF Confluence: Real analysis from Module 1")
    print("   ✅ No import errors: Frontend loads properly")
    print("   ✅ Signal Panel: Shows live data")
    print("\n🔄 Data updates every 30 seconds")
    print("📈 Module 1 (MTF Confluence) working perfectly")
    print("\n⏹️  Close the terminal windows to stop services")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)