#!/usr/bin/env python3
"""
Test WebSocket connection to verify it's working properly
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Test WebSocket connection"""
    
    try:
        print("Connecting to WebSocket...")
        
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Wait for initial messages
            try:
                # Receive initial connection message
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received: {data['type']} - {data['message']}")
                
                # Send a test message
                test_message = {
                    "type": "test",
                    "message": "Hello from test client",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                print("✅ Sent test message")
                
                # Wait for echo response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                echo_data = json.loads(response)
                print(f"✅ Received echo: {echo_data['type']}")
                
                # Wait a bit for any market data updates
                print("Waiting for market data updates...")
                for i in range(3):
                    try:
                        update = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        update_data = json.loads(update)
                        print(f"📊 Market update: {update_data['type']}")
                        if 'data' in update_data:
                            for symbol, data in update_data['data'].items():
                                print(f"  {symbol}: ${data.get('price', 'N/A')}")
                    except asyncio.TimeoutError:
                        print("  No market data received (timeout)")
                        break
                
            except asyncio.TimeoutError:
                print("⚠️  Timeout waiting for messages")
                
    except ConnectionRefusedError:
        print("❌ Connection refused - make sure the backend server is running on port 8000")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())