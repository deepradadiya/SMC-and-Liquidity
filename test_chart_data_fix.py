#!/usr/bin/env python3
"""
Test script to verify chart data API is working correctly
"""

import requests
import json
from datetime import datetime, timedelta

def test_auth():
    """Test authentication"""
    print("🔐 Testing authentication...")
    
    auth_data = {
        "username": "admin",
        "password": "smc_admin_2024"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login", json=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Authentication successful")
            return token_data.get("access_token")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_chart_data(token):
    """Test chart data endpoint"""
    print("\n📊 Testing chart data endpoint...")
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=8)  # 8 hours of 15m data = 32 candles
    
    params = {
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "validate": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:8000/api/data/ohlcv", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chart data received")
            print(f"📈 Data points: {len(data.get('data', []))}")
            
            if data.get('data'):
                first_candle = data['data'][0]
                last_candle = data['data'][-1]
                print(f"🕐 Time range: {first_candle.get('timestamp')} to {last_candle.get('timestamp')}")
                print(f"💰 Price range: ${first_candle.get('close')} to ${last_candle.get('close')}")
                
                # Check for reasonable price continuity
                prices = [float(candle['close']) for candle in data['data']]
                max_change = 0
                for i in range(1, len(prices)):
                    change = abs(prices[i] - prices[i-1]) / prices[i-1]
                    max_change = max(max_change, change)
                
                print(f"📊 Max price change between candles: {max_change:.2%}")
                if max_change > 0.05:  # 5% change
                    print("⚠️  WARNING: Large price jumps detected!")
                else:
                    print("✅ Price continuity looks good")
                    
            return True
        else:
            print(f"❌ Chart data failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Chart data error: {e}")
        return False

def main():
    print("🧪 Testing Chart Data Fix")
    print("=" * 40)
    
    # Test authentication
    token = test_auth()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test chart data
    success = test_chart_data(token)
    
    if success:
        print("\n✅ All tests passed! Chart data should work properly now.")
    else:
        print("\n❌ Tests failed. Chart data issues persist.")

if __name__ == "__main__":
    main()