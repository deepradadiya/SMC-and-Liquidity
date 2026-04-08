#!/usr/bin/env python3
"""
Test real-time data integration
"""

import asyncio
import sys
import os
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.market_data_service import MarketDataService
from app.strategies.mtf_confluence import ConfluenceEngine


async def test_realtime_data():
    """Test if we're getting real-time data"""
    print("🔍 TESTING REAL-TIME DATA")
    print("=" * 40)
    
    # Test 1: Market Data Service
    print("\n📊 Step 1: Testing Market Data Service")
    print("-" * 30)
    
    service = MarketDataService()
    
    try:
        # Fetch current data
        market_data = await service.fetch_ohlcv("BTCUSDT", "1h", 100)
        df = service.to_dataframe(market_data)
        
        current_price = df['close'].iloc[-1]
        print(f"✅ Current BTC Price: ${current_price:,.2f}")
        
        # Check if price is realistic (should be around $69,000)
        if 60000 <= current_price <= 80000:
            print(f"✅ Price looks realistic (within $60k-$80k range)")
        else:
            print(f"⚠️  Price seems off - might be using mock data")
            
        # Check data freshness
        latest_time = df.index[-1]
        print(f"✅ Latest data time: {latest_time}")
        
    except Exception as e:
        print(f"❌ Market data error: {str(e)}")
        return False
    
    # Test 2: MTF Analysis with current data
    print(f"\n🎯 Step 2: Testing MTF Analysis")
    print("-" * 30)
    
    engine = ConfluenceEngine()
    
    try:
        result = await engine.analyze_mtf_confluence(
            symbol="BTCUSDT",
            entry_tf="5m",
            htf="4h", 
            mtf="1h"
        )
        
        print(f"✅ MTF Analysis completed")
        print(f"   Confluence Score: {result.confluence_score}/100")
        print(f"   Bias: {result.bias}")
        print(f"   Entry: ${result.entry or 0:,.2f}")
        
        # Check if entry price is realistic
        if result.entry and 60000 <= result.entry <= 80000:
            print(f"✅ Entry price looks current")
        elif result.entry:
            print(f"⚠️  Entry price seems outdated: ${result.entry:,.2f}")
        else:
            print(f"ℹ️  No entry signal (confluence score: {result.confluence_score})")
            
    except Exception as e:
        print(f"❌ MTF analysis error: {str(e)}")
        return False
    
    # Test 3: API Endpoint
    print(f"\n🌐 Step 3: Testing API Endpoint")
    print("-" * 30)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/mtf/mtf-analyze",
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
            print(f"✅ API working")
            print(f"   Confluence Score: {data.get('confluence_score', 'N/A')}")
            print(f"   Entry: ${data.get('entry', 0) or 0:,.2f}")
            print(f"   Signal Valid: {data.get('signal_valid', False)}")
        else:
            print(f"❌ API returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API error: {str(e)}")
    
    return True


if __name__ == "__main__":
    print("Real-Time Data Test")
    print("=" * 40)
    
    success = asyncio.run(test_realtime_data())
    
    if success:
        print(f"\n✅ Real-time data test completed!")
        print(f"\nNext steps:")
        print(f"1. Restart your backend server")
        print(f"2. Refresh your frontend")
        print(f"3. Check if prices are now current")
    else:
        print(f"\n❌ Real-time data test failed")