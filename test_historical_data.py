#!/usr/bin/env python3
"""
Test Historical Data Fetching
Demonstrates fetching maximum historical data for all timeframes
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time

async def test_historical_data_api():
    """Test the historical data API endpoints"""
    
    base_url = "http://localhost:8000/api/historical"
    
    async with aiohttp.ClientSession() as session:
        
        print("🔍 Testing Historical Data API")
        print("=" * 50)
        
        # 1. Get supported timeframes
        print("\n1️⃣ Getting supported timeframes...")
        try:
            async with session.get(f"{base_url}/timeframes") as response:
                if response.status == 200:
                    timeframes = await response.json()
                    print(f"✅ Found {len(timeframes)} supported timeframes:")
                    for tf, config in timeframes.items():
                        print(f"   📊 {tf}: {config['description']} (max {config['max_historical_days']} days)")
                else:
                    print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 2. Test single timeframe fetch
        print("\n2️⃣ Testing single timeframe fetch (BTCUSDT 1h)...")
        try:
            start_time = time.time()
            async with session.get(f"{base_url}/fetch/BTCUSDT/1h") as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - start_time
                    print(f"✅ Fetched {data['total_candles']} candles in {duration:.2f}s")
                    print(f"   📅 Date range: {data['earliest_date']} to {data['latest_date']}")
                    if data['data']:
                        print(f"   💰 Latest price: ${data['data'][-1]['close']}")
                else:
                    print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Test bulk fetch for multiple timeframes
        print("\n3️⃣ Testing bulk fetch (BTCUSDT - selected timeframes)...")
        try:
            start_time = time.time()
            timeframes_to_fetch = "1m,5m,15m,1h,4h,1d"
            async with session.get(f"{base_url}/fetch/BTCUSDT?timeframes={timeframes_to_fetch}") as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - start_time
                    print(f"✅ Bulk fetch completed in {data['fetch_duration_seconds']:.2f}s")
                    print(f"   📊 Total datasets: {data['total_datasets']}")
                    
                    for tf, tf_data in data['timeframes'].items():
                        if tf_data['total_candles'] > 0:
                            print(f"   📈 {tf}: {tf_data['total_candles']} candles ({tf_data['earliest_date']} to {tf_data['latest_date']})")
                        else:
                            print(f"   ❌ {tf}: No data")
                else:
                    print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 4. Test data summary
        print("\n4️⃣ Getting data summary...")
        try:
            async with session.get(f"{base_url}/summary") as response:
                if response.status == 200:
                    summary = await response.json()
                    print(f"✅ Data summary: {summary['total_datasets']} datasets cached")
                    
                    if summary['datasets']:
                        print("   📋 Cached datasets:")
                        for dataset in summary['datasets'][:10]:  # Show first 10
                            print(f"      {dataset['symbol']} {dataset['timeframe']}: {dataset['total_candles']} candles")
                        
                        if len(summary['datasets']) > 10:
                            print(f"      ... and {len(summary['datasets']) - 10} more")
                else:
                    print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 5. Test health check
        print("\n5️⃣ Health check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"✅ Service healthy: {health['total_datasets']} datasets, {health['supported_timeframes']} timeframes")
                else:
                    print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_multiple_symbols():
    """Test fetching data for multiple symbols"""
    
    print("\n" + "=" * 50)
    print("🚀 Testing Multiple Symbols")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/historical"
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    async with aiohttp.ClientSession() as session:
        
        for symbol in symbols:
            print(f"\n📊 Fetching {symbol} data...")
            try:
                start_time = time.time()
                timeframes = "1h,4h,1d"  # Fetch key timeframes
                
                async with session.get(f"{base_url}/fetch/{symbol}?timeframes={timeframes}") as response:
                    if response.status == 200:
                        data = await response.json()
                        duration = time.time() - start_time
                        
                        print(f"✅ {symbol}: {data['total_datasets']} datasets in {duration:.2f}s")
                        
                        for tf, tf_data in data['timeframes'].items():
                            if tf_data['total_candles'] > 0:
                                latest_price = tf_data['data'][-1]['close'] if tf_data['data'] else 0
                                print(f"   {tf}: {tf_data['total_candles']} candles, latest: ${latest_price}")
                    else:
                        print(f"❌ {symbol}: Error {response.status}")
                        
            except Exception as e:
                print(f"❌ {symbol}: Error {e}")

def main():
    """Main test function"""
    print("🔥 Historical Data API Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        # Run the tests
        asyncio.run(test_historical_data_api())
        asyncio.run(test_multiple_symbols())
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("📚 Check the API docs at: http://localhost:8000/docs")
        print("🔍 Look for the 'historical-data' section")
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main()