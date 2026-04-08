#!/usr/bin/env python3
"""
Test the completely rewritten MTF Engine with real Binance data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.strategies.mtf_confluence import ConfluenceEngine
import asyncio

async def test_real_mtf_engine():
    print('🚀 Testing COMPLETELY REWRITTEN MTF Engine with REAL Binance data')
    print('=' * 70)
    
    engine = ConfluenceEngine()
    
    try:
        # Test with BTCUSDT
        result = await engine.analyze_mtf_confluence('BTCUSDT', '5m', '4h', '1h')
        
        print(f'📊 Symbol: BTCUSDT')
        print(f'📈 Confluence Score: {result.confluence_score}/100')
        print(f'🎯 HTF Bias: {result.bias}')
        print(f'💰 Entry Price: {result.entry}')
        print(f'🛡️ Stop Loss: {result.stop_loss}')
        print(f'🎯 Take Profit: {result.take_profit}')
        print(f'✅ Signal Valid: {result.entry is not None}')
        
        print(f'\n🔍 CONFLUENCE BREAKDOWN:')
        for reason in result.reasons:
            print(f'   • {reason}')
        
        print(f'\n📊 HTF Analysis (4H):')
        print(f'   • Bias: {result.htf_analysis.get("bias")}')
        print(f'   • Order Blocks: {len(result.htf_analysis.get("htf_ob", []))}')
        print(f'   • Liquidity Zones: {len(result.htf_analysis.get("htf_liquidity", []))}')
        print(f'   • Latest Price: ${result.htf_analysis.get("latest_price", 0):.2f}')
        
        print(f'\n📊 MTF Analysis (1H):')
        print(f'   • Confirmed: {result.mtf_analysis.get("confirmed")}')
        if result.mtf_analysis.get("confirmed"):
            print(f'   • BOS Level: ${result.mtf_analysis.get("mtf_bos_level", 0):.2f}')
            print(f'   • Direction: {result.mtf_analysis.get("mtf_bos_direction")}')
        
        print(f'\n📊 LTF Analysis (5M):')
        if result.ltf_analysis.get("entry"):
            print(f'   • Entry Type: {result.ltf_analysis.get("entry_type")}')
            print(f'   • Direction: {result.ltf_analysis.get("direction")}')
        else:
            print(f'   • No entry found: {result.ltf_analysis.get("reason", "Unknown")}')
        
        # Validate this is REAL data
        if result.confluence_score == 100:
            print(f'\n⚠️ WARNING: Score is exactly 100 - might still be fake data')
        else:
            print(f'\n✅ SUCCESS: Score is {result.confluence_score} - appears to be real analysis')
            
        return result
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_real_mtf_engine())