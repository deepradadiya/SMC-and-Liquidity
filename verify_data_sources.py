#!/usr/bin/env python3
"""
Verify Data Sources - Check what's working and what's not
"""

import requests
import time
from datetime import datetime

def check_backend_status():
    """Check if backend is running"""
    
    print("🔍 CHECKING BACKEND STATUS")
    print("-" * 25)
    
    try:
        # Try to connect to backend health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is RUNNING")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Backend responding but with error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT RUNNING")
        print("   Connection refused on localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Backend is slow to respond")
        return False
    except Exception as e:
        print(f"❌ Backend check failed: {e}")
        return False

def check_mtf_analysis():
    """Check if MTF analysis is working"""
    
    print("\n🧠 CHECKING MTF ANALYSIS")
    print("-" * 22)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/mtf/mtf-analyze",
            json={
                "symbol": "BTCUSDT",
                "entry_tf": "5m",
                "htf": "4h",
                "mtf": "1h"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ MTF Analysis is WORKING")
            print(f"   Confidence Score: {data.get('confluence_score', 'N/A')}")
            print(f"   Bias: {data.get('bias', 'N/A')}")
            print(f"   Signal Valid: {data.get('signal_valid', 'N/A')}")
            return True
        else:
            print(f"❌ MTF Analysis failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ MTF Analysis NOT AVAILABLE")
        print("   Backend not running")
        return False
    except Exception as e:
        print(f"❌ MTF Analysis error: {e}")
        return False

def check_binance_connection():
    """Check if Binance API is accessible"""
    
    print("\n🌐 CHECKING BINANCE CONNECTION")
    print("-" * 27)
    
    try:
        # Test Binance REST API
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Binance API is ACCESSIBLE")
            print(f"   BTCUSDT Price: ${float(data['price']):,.2f}")
            print("   This is why your frontend gets price updates!")
            return True
        else:
            print(f"⚠️  Binance API issue: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Binance API error: {e}")
        return False

def explain_current_situation():
    """Explain what's currently working"""
    
    print("\n📊 CURRENT SITUATION ANALYSIS")
    print("-" * 30)
    
    backend_running = check_backend_status()
    mtf_working = check_mtf_analysis() if backend_running else False
    binance_working = check_binance_connection()
    
    print(f"\n📋 SUMMARY:")
    print(f"   Backend Running: {'✅ YES' if backend_running else '❌ NO'}")
    print(f"   MTF Analysis: {'✅ WORKING' if mtf_working else '❌ NOT WORKING'}")
    print(f"   Binance Data: {'✅ ACCESSIBLE' if binance_working else '❌ NOT ACCESSIBLE'}")
    
    print(f"\n🎯 WHAT THIS MEANS:")
    if not backend_running:
        print("   📱 Frontend: Shows prices but 'SCANNING MARKET...' for analysis")
        print("   📈 Chart: Works (gets data from Binance directly)")
        print("   💹 Watchlist: Works (gets prices from Binance directly)")
        print("   🧠 Analysis: Not working (needs your backend)")
        print("   🎯 Signals: Not generated (needs your backend)")
    else:
        print("   📱 Frontend: Fully functional with analysis")
        print("   📈 Chart: Works with live data")
        print("   💹 Watchlist: Works with live prices")
        print("   🧠 Analysis: Working with confidence scores")
        print("   🎯 Signals: Being generated")

def show_websocket_info():
    """Show WebSocket connection info"""
    
    print(f"\n🔌 WEBSOCKET CONNECTIONS")
    print("-" * 22)
    
    print("Frontend connects to these WebSockets:")
    print("1. 📈 Binance Price Stream:")
    print("   URL: wss://stream.binance.com:9443/stream")
    print("   Purpose: Real-time price tickers")
    print("   Status: ✅ Always works (independent of your backend)")
    
    print("\n2. 📊 Binance Kline Stream:")
    print("   URL: wss://stream.binance.com:9443/ws/btcusdt@kline_15m")
    print("   Purpose: Real-time candle data for charts")
    print("   Status: ✅ Always works (independent of your backend)")
    
    print("\n3. 🖥️  Your Backend WebSocket:")
    print("   URL: ws://localhost:8000/ws")
    print("   Purpose: Analysis updates, signals, notifications")
    print("   Status: ❌ Only works when your backend is running")

if __name__ == "__main__":
    print("🚀 DATA SOURCES VERIFICATION")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    explain_current_situation()
    show_websocket_info()
    
    print(f"\n💡 CONCLUSION:")
    print("Your frontend is SMART! It gets price data directly from Binance,")
    print("so prices always work. Analysis features need your backend.")
    print("\nTo get full functionality: cd backend && python main.py")