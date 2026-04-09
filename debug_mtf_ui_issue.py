#!/usr/bin/env python3
"""
Debug MTF UI Issue - Check why professional messaging isn't showing
"""

import requests
import json
import time
from datetime import datetime

def debug_mtf_ui_issue():
    """Debug why the UI still shows old loading states"""
    
    print("🔍 DEBUGGING MTF UI ISSUE")
    print("=" * 40)
    
    print("1. Checking Backend API Response...")
    try:
        response = requests.post(
            "http://localhost:8000/api/mtf/mtf-analyze",
            headers={'Content-Type': 'application/json'},
            json={
                "symbol": "BTCUSDT",
                "entry_tf": "5m",
                "htf": "4h",
                "mtf": "1h"
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend Response: {response.status_code}")
            print(f"   📊 Confidence Score: {data.get('confluence_score', 'Missing')}")
            print(f"   ⏰ Next Analysis: {data.get('next_analysis_in', 'Missing')}")
            print(f"   📈 Market Status: {data.get('market_status', 'Missing')}")
            print(f"   🎯 Signal Valid: {data.get('signal_valid', 'Missing')}")
            
            # Check if new fields are present
            new_fields = ['next_analysis_in', 'market_status']
            missing_fields = [field for field in new_fields if field not in data]
            
            if missing_fields:
                print(f"   ⚠️  Missing new fields: {missing_fields}")
                print("   💡 Backend may need restart to pick up changes")
            else:
                print("   ✅ All new fields present in API response")
                
        else:
            print(f"   ❌ Backend Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend not running")
        print("   💡 Start backend: python backend/main.py")
    except requests.exceptions.Timeout:
        print("   ⏰ Backend timeout - may be processing")
        print("   💡 This is normal for first request")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_frontend_files():
    """Check if frontend files have the correct updates"""
    
    print("\n2. Checking Frontend Files...")
    
    files_to_check = [
        {
            "path": "frontend/src/components/MTFSignalPanel.jsx",
            "should_contain": [
                "ANALYZING MARKET CONDITIONS",
                "Confidence score:",
                "Next analysis in",
                "statusMessage",
                "next_analysis_in"
            ]
        },
        {
            "path": "frontend/src/hooks/useMTFConfluence.js", 
            "should_contain": [
                "statusMessage",
                "nextAnalysisIn",
                "marketStatus",
                "next_analysis_in"
            ]
        }
    ]
    
    for file_info in files_to_check:
        try:
            with open(file_info["path"], 'r') as f:
                content = f.read()
            
            print(f"\n   📁 {file_info['path']}:")
            
            for item in file_info["should_contain"]:
                if item in content:
                    print(f"      ✅ Contains: {item}")
                else:
                    print(f"      ❌ Missing: {item}")
                    
        except FileNotFoundError:
            print(f"   ❌ File not found: {file_info['path']}")
        except Exception as e:
            print(f"   ❌ Error reading {file_info['path']}: {e}")

def suggest_solutions():
    """Suggest solutions based on findings"""
    
    print("\n3. Possible Solutions:")
    print("-" * 20)
    
    solutions = [
        "🔄 Restart the backend server (python backend/main.py)",
        "🔄 Restart the frontend development server (npm start)",
        "🧹 Clear browser cache and hard refresh (Ctrl+Shift+R)",
        "📱 Check browser developer console for JavaScript errors",
        "🔍 Verify the correct component is being used (MTFSignalPanel vs SignalPanel)",
        "⏰ Wait for API response - first request may take time",
        "🔧 Check if WebSocket connections are working properly"
    ]
    
    for solution in solutions:
        print(f"   {solution}")

def show_expected_behavior():
    """Show what the UI should display"""
    
    print("\n4. Expected UI Behavior:")
    print("-" * 25)
    
    print("When confidence < 60:")
    print("   📊 Should show: 'ANALYZING MARKET CONDITIONS'")
    print("   💬 Should show: 'Confidence score: XX/100'")
    print("   ⏰ Should show: 'Next analysis in X minutes'")
    print("   🔄 MTF Bias should show: 'ANALYZING...' not 'LOADING'")
    
    print("\nWhen confidence >= 60:")
    print("   🎯 Should show: Active signal with trade levels")
    print("   ✅ Should show: Action buttons")
    print("   📈 Should show: Confluence factors")

if __name__ == "__main__":
    print("🚀 MTF UI DEBUG SESSION")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Debug the issue
    debug_mtf_ui_issue()
    
    # Check frontend files
    check_frontend_files()
    
    # Suggest solutions
    suggest_solutions()
    
    # Show expected behavior
    show_expected_behavior()
    
    print(f"\n🎯 DEBUG COMPLETE")
    print("If UI still shows old states, try restarting both backend and frontend!")