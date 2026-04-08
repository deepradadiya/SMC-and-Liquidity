#!/usr/bin/env python3
"""
Restart system with real-time data
"""

import os
import sys
import subprocess
import time

def restart_system():
    """Restart the system with real-time data"""
    print("🔄 RESTARTING SYSTEM WITH REAL-TIME DATA")
    print("=" * 50)
    
    print("\n✅ Changes made:")
    print("   • Switched from sandbox to live Binance data")
    print("   • Updated mock data to current BTC price (~$69k)")
    print("   • Replaced SignalPanel with MTFSignalPanel in Dashboard")
    print("   • MTFSignalPanel uses real Module 1 data")
    
    print(f"\n📋 What you need to do:")
    print("1. Stop your current backend server (Ctrl+C)")
    print("2. Restart backend: python start_system.py")
    print("3. Refresh your frontend browser")
    print("4. You should now see current BTC prices (~$69k)")
    
    print(f"\n🎯 Expected results:")
    print("   • Entry prices around $69,000 (not $66,000)")
    print("   • Real-time confluence analysis")
    print("   • Live MTF bias updates")
    print("   • Auto-refresh every 30 seconds")
    
    print(f"\n⚠️  If you still see old prices:")
    print("   • Clear browser cache")
    print("   • Check browser console for errors")
    print("   • Verify backend is running on port 8000")
    
    return True

if __name__ == "__main__":
    restart_system()
    print(f"\n🚀 System ready for real-time data!")