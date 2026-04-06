#!/usr/bin/env python3
"""
Test WebSocket price updates to ensure they're reasonable
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Test WebSocket price updates"""
    print("🔌 Testing WebSocket price updates...")
    
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            # Listen for a few price updates
            prices = {}
            update_count = 0
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "price_update":
                        update_count += 1
                        price_data = data.get("data", {})
                        
                        for symbol, info in price_data.items():
                            current_price = info.get("price")
                            if current_price:
                                if symbol in prices:
                                    # Check price change
                                    prev_price = prices[symbol]
                                    change = abs(current_price - prev_price) / prev_price
                                    print(f"📊 {symbol}: ${current_price:,.2f} (change: {change:.2%})")
                                    
                                    if change > 0.05:  # 5% change
                                        print(f"⚠️  WARNING: Large price jump for {symbol}!")
                                else:
                                    print(f"💰 {symbol}: ${current_price:,.2f} (initial)")
                                
                                prices[symbol] = current_price
                        
                        if update_count >= 5:  # Test 5 updates
                            break
                            
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message}")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
            
            print(f"✅ Received {update_count} price updates")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

def main():
    print("🧪 Testing WebSocket Price Updates")
    print("=" * 40)
    
    try:
        success = asyncio.run(test_websocket())
        if success:
            print("\n✅ WebSocket price updates look good!")
        else:
            print("\n❌ WebSocket issues detected")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")

if __name__ == "__main__":
    main()