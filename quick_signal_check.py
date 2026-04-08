#!/usr/bin/env python3
"""
Quick Signal Check - Clean one-time check without JSON mess
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.strategies.mtf_confluence import ConfluenceEngine

async def quick_check(symbol="BTCUSDT"):
    """Quick clean check of current signal status"""
    print(f"🔍 Quick Signal Check - {symbol}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    engine = ConfluenceEngine()
    
    try:
        result = await engine.analyze_mtf_confluence(
            symbol=symbol,
            entry_tf="5m",
            htf="4h", 
            mtf="1h"
        )
        
        # Clean status display
        status = "🟢 VALID SIGNAL" if result.confluence_score >= 60 and result.entry else "🔍 ANALYZING"
        bias_icon = "📈" if result.bias == 'bullish' else "📉" if result.bias == 'bearish' else "➡️"
        
        print(f"Status: {status}")
        print(f"Confluence: {result.confluence_score}/100")
        print(f"HTF Bias: {bias_icon} {result.bias.upper()}")
        
        if result.entry:
            print(f"Entry: ${result.entry:.2f}")
            print(f"Stop: ${result.stop_loss:.2f}")
            print(f"Target: ${result.take_profit:.2f}")
        else:
            print("Entry: Waiting for confluence >= 60")
            
        # Show latest price from HTF analysis
        latest_price = result.htf_analysis.get('latest_price')
        if latest_price:
            print(f"Current Price: ${latest_price}")
            
        print("-" * 40)
        
        if result.confluence_score >= 60:
            print("✅ Signal meets criteria - check UI!")
        else:
            print("💤 No signal yet - system monitoring...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    asyncio.run(quick_check(symbol))