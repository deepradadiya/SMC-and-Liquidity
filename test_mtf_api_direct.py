#!/usr/bin/env python3
"""
Direct test of MTF API to verify it's working
"""

import requests
import json

def test_mtf_api():
    """Test the MTF API directly"""
    print("🔍 Testing MTF API directly...")
    
    try:
        # Test MTF analysis endpoint
        response = requests.post(
            'http://localhost:8000/api/mtf/mtf-analyze',
            headers={'Content-Type': 'application/json'},
            json={
                'symbol': 'BTCUSDT',
                'entry_tf': '5m',
                'htf': '4h',
                'mtf': '1h'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ MTF API is working!")
            print(f"📊 BTC Entry Price: ${data.get('entry', 'N/A')}")
            print(f"📈 Confluence Score: {data.get('confluence_score', 'N/A')}/100")
            print(f"🎯 Bias: {data.get('bias', 'N/A')}")
            print(f"✅ Signal Valid: {data.get('signal_valid', False)}")
            
            if data.get('entry'):
                print(f"\n💰 Trade Levels:")
                print(f"   Entry: ${data.get('entry'):.2f}")
                print(f"   Stop Loss: ${data.get('sl', 0):.2f}")
                print(f"   Take Profit: ${data.get('tp', 0):.2f}")
            
            print(f"\n🔍 Confluence Reasons:")
            for reason in data.get('reasons', []):
                print(f"   • {reason}")
                
            return True
        else:
            print(f"❌ MTF API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MTF API test failed: {e}")
        return False

def test_backend_health():
    """Test backend health"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing SMC Backend MTF API")
    print("=" * 50)
    
    if test_backend_health():
        test_mtf_api()
    else:
        print("❌ Backend is not running. Please start it first:")
        print("   cd backend && python run.py")