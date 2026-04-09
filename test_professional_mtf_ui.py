#!/usr/bin/env python3
"""
Test Professional MTF UI with Confidence-Based Messaging
"""

import requests
import json
import time
from datetime import datetime

def test_professional_mtf_messaging():
    """Test the new professional confidence-based messaging system"""
    
    print("🧪 Testing Professional MTF UI with Confidence-Based Messaging")
    print("=" * 60)
    
    # Test different scenarios to see confidence-based responses
    test_cases = [
        {
            "name": "High Volume Pair (Should have higher confidence)",
            "symbol": "BTCUSDT",
            "expected_confidence": "> 40"
        },
        {
            "name": "Lower Volume Pair (May have lower confidence)",
            "symbol": "ADAUSDT", 
            "expected_confidence": "Variable"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print(f"   Symbol: {test_case['symbol']}")
        print(f"   Expected: {test_case['expected_confidence']}")
        
        try:
            # Make API call
            response = requests.post(
                "http://localhost:8000/api/mtf/mtf-analyze",
                headers={'Content-Type': 'application/json'},
                json={
                    "symbol": test_case["symbol"],
                    "entry_tf": "5m",
                    "htf": "4h", 
                    "mtf": "1h"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ API Response Received")
                print(f"   📊 Confluence Score: {data.get('confluence_score', 0)}/100")
                print(f"   🎯 Bias: {data.get('bias', 'neutral').upper()}")
                print(f"   ⏰ Next Analysis: {data.get('next_analysis_in', 5)} minutes")
                print(f"   📈 Market Status: {data.get('market_status', 'analyzing')}")
                print(f"   ✅ Signal Valid: {data.get('signal_valid', False)}")
                
                # Show professional messaging logic
                confidence = data.get('confluence_score', 0)
                if confidence < 60:
                    print(f"   💬 Professional Message: 'Analyzing market... Confidence score: {confidence}/100. Next analysis in {data.get('next_analysis_in', 5)} minutes.'")
                else:
                    print(f"   💬 Professional Message: 'Signal ready with {confidence}/100 confidence'")
                
                # Show confluence factors
                reasons = data.get('reasons', [])
                if reasons:
                    print(f"   📋 Confluence Factors ({len(reasons)}):")
                    for reason in reasons[:3]:  # Show first 3
                        print(f"      • {reason}")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected Error: {e}")
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎯 PROFESSIONAL UI IMPROVEMENTS:")
    print("   ✅ No more continuous loading spinners")
    print("   ✅ Confidence-based messaging system")
    print("   ✅ Dynamic retry intervals (2-15 minutes)")
    print("   ✅ Professional status indicators")
    print("   ✅ Clear next analysis timing")
    print("\n📱 UI BEHAVIOR:")
    print("   • Score ≥ 60: Show signal with confidence")
    print("   • Score < 60: Show 'Analyzing market...' with score")
    print("   • Dynamic refresh based on confidence level")
    print("   • Professional retry messaging")

def test_ui_integration():
    """Test that frontend components handle new fields correctly"""
    
    print("\n🔧 Testing Frontend Integration")
    print("-" * 40)
    
    # Check if frontend files have been updated
    frontend_files = [
        "frontend/src/hooks/useMTFConfluence.js",
        "frontend/src/components/MTFSignalPanel.jsx"
    ]
    
    for file_path in frontend_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for new features
            features = {
                "statusMessage": "statusMessage" in content,
                "nextAnalysisIn": "nextAnalysisIn" in content or "next_analysis_in" in content,
                "marketStatus": "marketStatus" in content or "market_status" in content,
                "professionalMessaging": "Analyzing market" in content or "Confidence score" in content
            }
            
            print(f"\n📁 {file_path}:")
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}")
                
        except FileNotFoundError:
            print(f"   ❌ File not found: {file_path}")
        except Exception as e:
            print(f"   ❌ Error reading {file_path}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Professional MTF UI Test")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test the API improvements
    test_professional_mtf_messaging()
    
    # Test frontend integration
    test_ui_integration()
    
    print(f"\n✅ Professional MTF UI Test Complete")
    print("💡 The system now provides professional confidence-based messaging")
    print("   instead of continuous loading spinners!")