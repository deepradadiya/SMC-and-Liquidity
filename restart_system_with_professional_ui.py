#!/usr/bin/env python3
"""
Restart System with Professional MTF UI Improvements
"""

import subprocess
import time
import requests
import os
from datetime import datetime

def restart_system_with_improvements():
    """Restart the system to apply professional UI improvements"""
    
    print("🚀 RESTARTING SYSTEM WITH PROFESSIONAL MTF UI")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n1. 🔧 IMPROVEMENTS IMPLEMENTED:")
    print("   ✅ Professional confidence-based messaging")
    print("   ✅ No more endless 'SCANNING MARKET...' loading")
    print("   ✅ Clear confidence scores (0-100)")
    print("   ✅ Dynamic retry intervals (2-15 minutes)")
    print("   ✅ 'ANALYZING MARKET CONDITIONS' status")
    print("   ✅ 'Next analysis in X minutes' timing")
    print("   ✅ MTF Bias shows 'ANALYZING...' not 'LOADING'")
    
    print("\n2. 🔄 RESTART INSTRUCTIONS:")
    print("   To see the improvements, you need to restart:")
    print("   📱 Frontend: Stop (Ctrl+C) and run 'npm start' in frontend/")
    print("   🖥️  Backend: Stop (Ctrl+C) and run 'python main.py' in backend/")
    print("   🧹 Browser: Hard refresh (Ctrl+Shift+R) to clear cache")
    
    print("\n3. 🧪 TESTING THE IMPROVEMENTS:")
    print("   After restart, you should see:")
    print("   • No more continuous loading spinners")
    print("   • Professional 'ANALYZING MARKET CONDITIONS' message")
    print("   • Clear confidence scores like '45/100'")
    print("   • Specific timing like 'Next analysis in 5 minutes'")
    print("   • MTF timeframes show 'ANALYZING...' instead of 'LOADING'")
    
    print("\n4. 📋 QUICK START COMMANDS:")
    print("   Backend:")
    print("   cd backend && python main.py")
    print("")
    print("   Frontend (in new terminal):")
    print("   cd frontend && npm start")
    
    print("\n5. 🎯 EXPECTED BEHAVIOR:")
    print("   Low Confidence (< 60):")
    print("   📊 'ANALYZING MARKET CONDITIONS'")
    print("   💬 'Confidence score: 45/100'")
    print("   ⏰ 'Next analysis in 5 minutes'")
    print("")
    print("   High Confidence (≥ 60):")
    print("   🎯 Shows active signal with trade levels")
    print("   ✅ Action buttons enabled")
    print("   📈 Confluence factors displayed")

def create_startup_scripts():
    """Create convenient startup scripts"""
    
    print("\n6. 📝 CREATING STARTUP SCRIPTS:")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🚀 Starting Backend with Professional MTF UI..."
cd backend
python main.py
"""
    
    with open("start_backend.sh", "w") as f:
        f.write(backend_script)
    
    # Frontend startup script  
    frontend_script = """#!/bin/bash
echo "🚀 Starting Frontend with Professional MTF UI..."
cd frontend
npm start
"""
    
    with open("start_frontend.sh", "w") as f:
        f.write(frontend_script)
    
    # Make scripts executable
    try:
        os.chmod("start_backend.sh", 0o755)
        os.chmod("start_frontend.sh", 0o755)
        print("   ✅ Created start_backend.sh")
        print("   ✅ Created start_frontend.sh")
        print("   💡 Run with: ./start_backend.sh and ./start_frontend.sh")
    except Exception as e:
        print(f"   ⚠️  Could not make scripts executable: {e}")

def test_after_restart():
    """Instructions for testing after restart"""
    
    print("\n7. 🧪 TESTING AFTER RESTART:")
    print("   1. Wait for both backend and frontend to start")
    print("   2. Open browser to http://localhost:3000")
    print("   3. Look at the right panel (MTF Signal Panel)")
    print("   4. You should see professional messaging instead of loading")
    print("   5. Check MTF Bias section - should show 'ANALYZING...' not 'LOADING'")
    
    print("\n8. 🔍 TROUBLESHOOTING:")
    print("   If you still see old loading states:")
    print("   • Hard refresh browser (Ctrl+Shift+R)")
    print("   • Check browser console for errors (F12)")
    print("   • Verify both servers are running")
    print("   • Wait a few seconds for API response")

if __name__ == "__main__":
    restart_system_with_improvements()
    create_startup_scripts()
    test_after_restart()
    
    print(f"\n🎉 PROFESSIONAL MTF UI READY!")
    print("Restart the system to see the improvements!")
    print("No more endless loading - professional confidence-based messaging!")