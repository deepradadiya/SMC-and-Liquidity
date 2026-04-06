#!/usr/bin/env python3
"""
Test the /predict endpoint to verify it's working
"""

import requests
import json
from datetime import datetime, timedelta

def test_predict_endpoint():
    """Test the predict endpoint with mock data"""
    
    # Create mock candle data
    base_time = datetime.now()
    candles = []
    
    for i in range(20):  # Send 20 candles
        timestamp = (base_time - timedelta(minutes=20-i)).isoformat()
        candles.append({
            "open_time": timestamp,
            "open": 50000.0 + i * 10,
            "high": 50100.0 + i * 10,
            "low": 49900.0 + i * 10,
            "close": 50050.0 + i * 10,
            "volume": 1000.0
        })
    
    # Prepare request
    payload = {
        "candles": candles,
        "atr_sl_multiplier": 1.5
    }
    
    try:
        # Test the endpoint
        print("Testing /predict endpoint...")
        response = requests.post(
            "http://localhost:8000/predict",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Predict endpoint working!")
            print(f"Signal: {result['signal']}")
            print(f"Confidence: {result['confidence']}%")
            print(f"Entry: {result['entry']}")
            print(f"Stop Loss: {result['stop_loss']}")
            print(f"Target: {result['target']}")
            print(f"Risk/Reward: {result['rr_ratio']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the backend server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_predict_endpoint()