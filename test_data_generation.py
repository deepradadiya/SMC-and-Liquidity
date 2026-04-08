#!/usr/bin/env python3
"""
Test data generation for MTF confluence engine
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.market_data_service import MarketDataService


async def test_data_generation():
    """Test market data generation"""
    print("🔍 Testing Market Data Generation")
    print("=" * 40)
    
    service = MarketDataService()
    
    # Test different limits
    test_cases = [
        ("BTCUSDT", "4h", 500),
        ("BTCUSDT", "1h", 500),
        ("BTCUSDT", "5m", 500)
    ]
    
    for symbol, timeframe, limit in test_cases:
        print(f"\nTesting {symbol} {timeframe} with limit {limit}")
        
        try:
            market_data = await service.fetch_ohlcv(symbol, timeframe, limit)
            df = service.to_dataframe(market_data)
            
            print(f"✅ Generated {len(df)} candles")
            print(f"   DataFrame shape: {df.shape}")
            print(f"   Price range: {df['low'].min():.2f} - {df['high'].max():.2f}")
            print(f"   Time range: {df.index[0]} to {df.index[-1]}")
            
            if len(df) >= 50:
                print(f"   ✅ Sufficient data for SMC analysis")
            else:
                print(f"   ❌ Insufficient data for SMC analysis (need 50+)")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_data_generation())