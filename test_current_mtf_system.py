#!/usr/bin/env python3
"""
Test current MTF system to see what data it's returning
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.strategies.mtf_confluence import ConfluenceEngine

async def test_current_mtf():
    """Test the current MTF confluence engine"""
    print("🔍 TESTING CURRENT MTF CONFLUENCE ENGINE")
    print("=" * 60)
    
    engine = ConfluenceEngine()
    
    try:
        # Test with BTCUSDT
        result = await engine.analyze_mtf_confluence(
            symbol="BTCUSDT",
            entry_tf="5m",
            htf="4h", 
            mtf="1h"
        )
        
        print(f"💰 Entry Price: {result.entry}")
        print(f"🛡️ Stop Loss: {result.stop_loss}")
        print(f"🎯 Take Profit: {result.take_profit}")
        print(f"✅ Signal Valid: {result.entry is not None}")
        print(f"📊 Confluence Score: {result.confluence_score}/100")
        print(f"📈 HTF Bias: {result.bias}")
        
        print(f"\n🔍 CONFLUENCE BREAKDOWN:")
        for reason in result.reasons:
            print(f"• {reason}")
            
        print(f"\n📊 HTF Analysis (4H):")
        htf = result.htf_analysis
        print(f"• Bias: {htf.get('bias', 'unknown')}")
        print(f"• Order Blocks: {len(htf.get('htf_ob', []))}")
        print(f"• Liquidity Zones: {len(htf.get('htf_liquidity', []))}")
        print(f"• Latest Price: ${htf.get('latest_price', 'N/A')}")
        
        print(f"\n📊 MTF Analysis (1H):")
        mtf = result.mtf_analysis
        print(f"• Confirmed: {mtf.get('confirmed', False)}")
        if mtf.get('mtf_bos_level'):
            print(f"• BOS Level: ${mtf.get('mtf_bos_level')}")
            
        print(f"\n📊 LTF Analysis (5M):")
        ltf = result.ltf_analysis
        if ltf.get('entry'):
            print(f"• Entry found: ${ltf.get('entry')}")
        else:
            print(f"• No entry found: {ltf.get('reason', 'No MTF confirmation')}")
            
        # Check if this looks like real data
        if result.confluence_score == 100:
            print(f"\n❌ WARNING: Score is 100 - might be hardcoded!")
        elif result.confluence_score == 0:
            print(f"\n⚠️ WARNING: Score is 0 - no confluence found")
        else:
            print(f"\n✅ SUCCESS: Score is {result.confluence_score} - appears to be real analysis")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_current_mtf())