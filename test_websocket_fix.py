#!/usr/bin/env python3
"""
Test WebSocket Fix
Quick test to verify WebSocket connections work properly
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for initial messages
            try:
                for i in range(3):  # Wait for up to 3 messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    print(f"📨 Message {i+1}: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'connection':
                        print(f"   Connection message: {data.get('message', '')}")
                    elif data.get('type') == 'price_update':
                        print(f"   Price update: {list(data.get('data', {}).keys())}")
                        
            except asyncio.TimeoutError:
                print("⏰ No more messages received (timeout)")
            
            # Send a test message
            test_message = {"type": "test", "message": "Hello from client"}
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for echo
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                echo_data = json.loads(response)
                if echo_data.get('type') == 'echo':
                    print("✅ Echo response received")
                else:
                    print(f"📨 Received: {echo_data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("⏰ No echo response received")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔥 WebSocket Fix Test")
    print("=" * 30)
    
    success = await test_websocket()
    
    if success:
        print("\n✅ WebSocket connection working!")
        print("💡 The WebSocket error should be resolved")
    else:
        print("\n❌ WebSocket connection has issues")
        print("💡 Check if backend is running on port 8000")

if __name__ == "__main__":
    asyncio.run(main())