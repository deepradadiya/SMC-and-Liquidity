#!/usr/bin/env python3
"""
Silent Signal Monitor - Only shows output when valid signals are found
Runs in background and alerts when confluence >= 60
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.strategies.mtf_confluence import ConfluenceEngine

class SilentSignalMonitor:
    def __init__(self):
        self.engine = ConfluenceEngine()
        self.last_signal_time = None
        self.monitoring = True
        
    async def check_signal(self, symbol="BTCUSDT"):
        """Check for signals silently"""
        try:
            result = await self.engine.analyze_mtf_confluence(
                symbol=symbol,
                entry_tf="5m",
                htf="4h", 
                mtf="1h"
            )
            
            # Only show output if signal is valid (confluence >= 60)
            if result.confluence_score >= 60 and result.entry:
                self.show_signal_alert(result, symbol)
                return True
            
            return False
            
        except Exception as e:
            # Silent error handling - only log critical errors
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                print(f"⚠️  Connection issue at {datetime.now().strftime('%H:%M:%S')} - retrying...")
            return False
    
    def show_signal_alert(self, result, symbol):
        """Show alert when valid signal is found"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print("\n" + "🚨" * 20)
        print(f"🎯 VALID SIGNAL FOUND! - {current_time}")
        print("🚨" * 20)
        
        signal_type = "🟢 BUY" if result.bias == 'bullish' else "🔴 SELL" if result.bias == 'bearish' else "⚪ NEUTRAL"
        
        print(f"📊 {symbol} - {signal_type}")
        print(f"💯 Confluence Score: {result.confluence_score}/100")
        print(f"💰 Entry: ${result.entry:.2f}")
        print(f"🛡️  Stop Loss: ${result.stop_loss:.2f}")
        print(f"🎯 Take Profit: ${result.take_profit:.2f}")
        
        risk_reward = abs(result.take_profit - result.entry) / abs(result.entry - result.stop_loss)
        print(f"📈 Risk:Reward = 1:{risk_reward:.1f}")
        
        print(f"\n✅ REASONS:")
        for reason in result.reasons:
            if not reason.startswith("❌"):
                print(f"   • {reason}")
        
        print("\n" + "🚨" * 20)
        print("Signal sent to UI automatically!")
        print("🚨" * 20 + "\n")
        
        self.last_signal_time = datetime.now()
    
    async def monitor_continuously(self, symbol="BTCUSDT", interval=30):
        """Monitor continuously with minimal output"""
        print(f"🔍 Silent Signal Monitor Started")
        print(f"📊 Monitoring: {symbol}")
        print(f"⏱️  Check Interval: {interval}s")
        print(f"🎯 Will alert when confluence >= 60")
        print(f"💤 Running silently... (Ctrl+C to stop)")
        print("-" * 50)
        
        check_count = 0
        
        try:
            while self.monitoring:
                check_count += 1
                
                # Show minimal progress every 10 checks (5 minutes)
                if check_count % 10 == 0:
                    current_time = datetime.now().strftime('%H:%M:%S')
                    print(f"💤 {current_time} - Still monitoring... (Check #{check_count})")
                
                signal_found = await self.check_signal(symbol)
                
                if signal_found:
                    # Wait longer after finding a signal to avoid spam
                    await asyncio.sleep(300)  # 5 minutes
                else:
                    await asyncio.sleep(interval)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")

async def main():
    """Main function"""
    monitor = SilentSignalMonitor()
    
    # Allow custom symbol from command line
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    
    await monitor.monitor_continuously(symbol)

if __name__ == "__main__":
    asyncio.run(main())