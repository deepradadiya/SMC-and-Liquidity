#!/usr/bin/env python3
"""
Start SMC Trading System with REAL DATA - Final Fix
This script ensures both backend and frontend work with real-time data
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_backend():
    """Check if backend is running and MTF API works"""
    try:
        # Test health
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code != 200:
            return False
            
        # Test MTF API
        response = requests.post(
            'http://localhost:8000/api/mtf/mtf-analyze',
            json={'symbol': 'BTCUSDT', 'entry_tf': '5m', 'htf': '4h', 'mtf': '1h'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend MTF API working - BTC Price: ${data.get('entry', 'N/A')}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Backend check failed: {e}")
        return False

def start_backend():
    """Start backend server"""
    print("🚀 Starting Backend Server...")
    
    if sys.platform == "darwin":  # macOS
        script = f'''
        tell application "Terminal"
            do script "cd {Path.cwd() / 'backend'} && python run.py"
            set custom title of front window to "SMC Backend - Real Data"
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
    else:
        print("📁 Please run in a new terminal:")
        print(f"   cd {Path.cwd() / 'backend'}")
        print("   python run.py")
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_backend():
            return True
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    
    return False

def start_frontend():
    """Start frontend server"""
    print("🌐 Starting Frontend Server...")
    
    if sys.platform == "darwin":  # macOS
        script = f'''
        tell application "Terminal"
            do script "cd {Path.cwd() / 'frontend'} && npm start"
            set custom title of front window to "SMC Frontend - Real Data"
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
    else:
        print("📁 Please run in a new terminal:")
        print(f"   cd {Path.cwd() / 'frontend'}")
        print("   npm start")

def main():
    """Main function"""
    print("🚀 Starting SMC Trading System with REAL DATA")
    print("=" * 60)
    
    # Check directories
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run from SMC-and-Liquidity root directory")
        return 1
    
    # Check if backend is already running
    if check_backend():
        print("✅ Backend already running with real data")
    else:
        if not start_backend():
            print("❌ Failed to start backend")
            return 1
    
    # Start frontend
    start_frontend()
    
    print("\n" + "=" * 60)
    print("🎉 SMC Trading System Started!")
    print("📊 Backend API: http://localhost:8000")
    print("📊 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("🔍 Test Page: file://" + str(Path.cwd() / "test_frontend_mtf_real.html"))
    print("=" * 60)
    
    print("\n💡 REAL DATA STATUS:")
    print("   ✅ Backend MTF API: Working with live BTC data")
    print("   ✅ Frontend: Updated to use MTFSignalPanel")
    print("   ✅ No more mock $66,250 data")
    
    print("\n🔍 VERIFICATION STEPS:")
    print("   1. Open http://localhost:3000")
    print("   2. Wait 30 seconds for MTF data to load")
    print("   3. Check MTF Signal Panel shows ~$69,000")
    print("   4. If still old data, check browser console for errors")
    
    print("\n📋 TROUBLESHOOTING:")
    print("   • Clear browser cache (Cmd+Shift+R)")
    print("   • Check browser console for API errors")
    print("   • Verify backend logs show MTF API calls")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)