"""
Multi-Timeframe Confluence Engine - REAL MARKET ANALYSIS
Fixed to use actual Binance data and proper SMC logic
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfluenceResult:
    """Result of MTF confluence analysis"""
    confluence_score: int
    bias: str
    entry: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    reasons: List[str]
    htf_analysis: Dict
    mtf_analysis: Dict
    ltf_analysis: Dict

class BinanceDataFetcher:
    """Fetch real OHLCV data from Binance public API"""
    
    BASE_URL = "https://api.binance.com/api/v3/klines"
    
    @staticmethod
    def fetch_candles(symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
        """
        Fetch real candle data from Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (4h, 1h, 15m, 5m)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            logger.info(f"Fetching {limit} {interval} candles for {symbol} from Binance")
            response = requests.get(BinanceDataFetcher.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to proper types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ Fetched {len(df)} candles, latest price: ${df['close'].iloc[-1]:.2f}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch Binance data: {str(e)}")
            raise Exception(f"Binance API error: {str(e)}")

class SMCAnalyzer:
    """Smart Money Concepts analysis on real candle data"""
    
    @staticmethod
    def detect_trend_bias(df: pd.DataFrame) -> str:
        """
        Detect trend bias using swing highs and lows
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(df) < 20:
            return 'neutral'
        
        # Find swing highs and lows
        highs = df['high'].rolling(window=5, center=True).max()
        lows = df['low'].rolling(window=5, center=True).min()
        
        swing_highs = df[df['high'] == highs]['high'].dropna()
        swing_lows = df[df['low'] == lows]['low'].dropna()
        
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return 'neutral'
        
        # Get last 3 swing highs and lows
        recent_highs = swing_highs.tail(3).values
        recent_lows = swing_lows.tail(3).values
        
        # Check for Higher Highs + Higher Lows (bullish)
        hh = recent_highs[1] > recent_highs[0] and recent_highs[2] > recent_highs[1]
        hl = recent_lows[1] > recent_lows[0] and recent_lows[2] > recent_lows[1]
        
        # Check for Lower Highs + Lower Lows (bearish)
        lh = recent_highs[1] < recent_highs[0] and recent_highs[2] < recent_highs[1]
        ll = recent_lows[1] < recent_lows[0] and recent_lows[2] < recent_lows[1]
        
        if hh and hl:
            return 'bullish'
        elif lh and ll:
            return 'bearish'
        else:
            return 'neutral'
    
    @staticmethod
    def detect_order_blocks(df: pd.DataFrame, bias: str) -> List[Dict]:
        """
        Detect Order Blocks based on real candle patterns
        
        Args:
            df: OHLCV DataFrame
            bias: Current trend bias
            
        Returns:
            List of order block dictionaries
        """
        order_blocks = []
        
        if len(df) < 10:
            return order_blocks
        
        for i in range(5, len(df) - 1):
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish Order Block: bearish candle before bullish impulse
            if bias == 'bullish':
                if (current['close'] < current['open'] and  # Bearish candle
                    next_candle['close'] > next_candle['open'] and  # Next is bullish
                    next_candle['close'] > current['high']):  # Breaks above
                    
                    order_blocks.append({
                        'type': 'bullish',
                        'top': current['high'],
                        'bottom': current['low'],
                        'price': (current['high'] + current['low']) / 2,
                        'timestamp': current.name
                    })
            
            # Bearish Order Block: bullish candle before bearish impulse
            elif bias == 'bearish':
                if (current['close'] > current['open'] and  # Bullish candle
                    next_candle['close'] < next_candle['open'] and  # Next is bearish
                    next_candle['close'] < current['low']):  # Breaks below
                    
                    order_blocks.append({
                        'type': 'bearish',
                        'top': current['high'],
                        'bottom': current['low'],
                        'price': (current['high'] + current['low']) / 2,
                        'timestamp': current.name
                    })
        
        return order_blocks[-5:]  # Return last 5 order blocks
    
    @staticmethod
    def detect_liquidity_zones(df: pd.DataFrame) -> List[Dict]:
        """
        Detect liquidity zones (swing highs and lows)
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            List of liquidity zone dictionaries
        """
        liquidity_zones = []
        
        if len(df) < 10:
            return liquidity_zones
        
        # Find swing highs (sell-side liquidity)
        for i in range(2, len(df) - 2):
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and
                df['high'].iloc[i] > df['high'].iloc[i+2]):
                
                liquidity_zones.append({
                    'type': 'sell_side',
                    'price': df['high'].iloc[i],
                    'timestamp': df.index[i]
                })
        
        # Find swing lows (buy-side liquidity)
        for i in range(2, len(df) - 2):
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and
                df['low'].iloc[i] < df['low'].iloc[i+2]):
                
                liquidity_zones.append({
                    'type': 'buy_side',
                    'price': df['low'].iloc[i],
                    'timestamp': df.index[i]
                })
        
        return liquidity_zones[-10:]  # Return last 10 liquidity zones
    
    @staticmethod
    def detect_break_of_structure(df: pd.DataFrame, bias: str) -> Optional[Dict]:
        """
        Detect Break of Structure (BOS)
        
        Args:
            df: OHLCV DataFrame
            bias: Expected bias direction
            
        Returns:
            BOS information or None
        """
        if len(df) < 10:
            return None
        
        # Find recent swing high/low
        recent_data = df.tail(20)
        
        if bias == 'bullish':
            # Look for break above recent swing high
            swing_high = recent_data['high'].max()
            current_price = df['close'].iloc[-1]
            
            if current_price > swing_high:
                return {
                    'confirmed': True,
                    'direction': 'bullish',
                    'level': swing_high,
                    'current_price': current_price
                }
        
        elif bias == 'bearish':
            # Look for break below recent swing low
            swing_low = recent_data['low'].min()
            current_price = df['close'].iloc[-1]
            
            if current_price < swing_low:
                return {
                    'confirmed': True,
                    'direction': 'bearish',
                    'level': swing_low,
                    'current_price': current_price
                }
        
        return {'confirmed': False}
    
    @staticmethod
    def detect_fair_value_gap(df: pd.DataFrame) -> List[Dict]:
        """
        Detect Fair Value Gaps (FVG)
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            List of FVG dictionaries
        """
        fvgs = []
        
        if len(df) < 3:
            return fvgs
        
        for i in range(len(df) - 2):
            candle1 = df.iloc[i]
            candle2 = df.iloc[i + 1]
            candle3 = df.iloc[i + 2]
            
            # Bullish FVG: candle3.low > candle1.high
            if candle3['low'] > candle1['high']:
                fvgs.append({
                    'type': 'bullish',
                    'top': candle3['low'],
                    'bottom': candle1['high'],
                    'timestamp': candle2.name
                })
            
            # Bearish FVG: candle3.high < candle1.low
            elif candle3['high'] < candle1['low']:
                fvgs.append({
                    'type': 'bearish',
                    'top': candle1['low'],
                    'bottom': candle3['high'],
                    'timestamp': candle2.name
                })
        
        return fvgs[-5:]  # Return last 5 FVGs

class ConfluenceEngine:
    """Main MTF Confluence Engine using real market data"""
    
    def __init__(self):
        self.fetcher = BinanceDataFetcher()
        self.analyzer = SMCAnalyzer()
    
    async def analyze_htf_bias(self, symbol: str, htf: str = "4h") -> Dict:
        """
        Analyze Higher Timeframe bias using real Binance data
        
        Args:
            symbol: Trading pair symbol
            htf: Higher timeframe (4h, 1d)
            
        Returns:
            Dict with bias, order blocks, and liquidity zones
        """
        logger.info(f"🔍 Analyzing HTF bias for {symbol} on {htf}")
        
        try:
            # Fetch real candle data from Binance
            df = self.fetcher.fetch_candles(symbol, htf, 200)
            
            # Detect trend bias from real price action
            bias = self.analyzer.detect_trend_bias(df)
            logger.info(f"📊 HTF Bias detected: {bias}")
            
            # Detect order blocks
            order_blocks = self.analyzer.detect_order_blocks(df, bias)
            logger.info(f"📦 Found {len(order_blocks)} Order Blocks")
            
            # Detect liquidity zones
            liquidity_zones = self.analyzer.detect_liquidity_zones(df)
            logger.info(f"💧 Found {len(liquidity_zones)} Liquidity Zones")
            
            return {
                "bias": bias,
                "htf_ob": order_blocks,
                "htf_liquidity": liquidity_zones,
                "timeframe": htf,
                "analysis_time": datetime.now().isoformat(),
                "latest_price": float(df['close'].iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"❌ HTF analysis error: {str(e)}")
            return {
                "bias": "neutral",
                "htf_ob": [],
                "htf_liquidity": [],
                "error": str(e),
                "timeframe": htf,
                "analysis_time": datetime.now().isoformat()
            }
    
    async def find_mtf_confirmation(self, symbol: str, mtf: str = "1h", htf_analysis: Dict = None) -> Dict:
        """
        Find MTF confirmation using real Binance data
        
        Args:
            symbol: Trading pair symbol
            mtf: Medium timeframe (1h, 15m)
            htf_analysis: HTF analysis result
            
        Returns:
            Dict with confirmation status and BOS level
        """
        logger.info(f"🔍 Finding MTF confirmation for {symbol} on {mtf}")
        
        if not htf_analysis or htf_analysis.get("bias") == "neutral":
            return {"confirmed": False, "reason": "No HTF bias"}
        
        htf_bias = htf_analysis["bias"]
        
        try:
            # Fetch real MTF candle data
            df = self.fetcher.fetch_candles(symbol, mtf, 100)
            
            # Only look for confirmation in the same direction as HTF bias
            bos = self.analyzer.detect_break_of_structure(df, htf_bias)
            
            if bos and bos.get("confirmed"):
                logger.info(f"✅ MTF BOS confirmed: {bos['direction']} at {bos['level']}")
                return {
                    "confirmed": True,
                    "mtf_bos_level": bos["level"],
                    "mtf_bos_direction": bos["direction"],
                    "timeframe": mtf,
                    "analysis_time": datetime.now().isoformat()
                }
            else:
                logger.info(f"❌ MTF BOS not confirmed")
                return {
                    "confirmed": False,
                    "reason": f"No {htf_bias} BOS found on {mtf}",
                    "timeframe": mtf,
                    "analysis_time": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ MTF confirmation error: {str(e)}")
            return {"confirmed": False, "error": str(e)}
    
    async def find_ltf_entry(self, symbol: str, ltf: str = "5m", mtf_confirmation: Dict = None) -> Dict:
        """
        Find LTF entry using real Binance data
        
        Args:
            symbol: Trading pair symbol
            ltf: Lower timeframe (5m, 1m)
            mtf_confirmation: MTF confirmation result
            
        Returns:
            Dict with entry, stop loss, and take profit
        """
        logger.info(f"🔍 Finding LTF entry for {symbol} on {ltf}")
        
        if not mtf_confirmation or not mtf_confirmation.get("confirmed"):
            return {"entry": None, "reason": "No MTF confirmation"}
        
        try:
            # Fetch real LTF candle data
            df = self.fetcher.fetch_candles(symbol, ltf, 50)
            
            direction = mtf_confirmation["mtf_bos_direction"]
            
            # Look for Order Blocks
            order_blocks = self.analyzer.detect_order_blocks(df, direction)
            
            # Look for Fair Value Gaps
            fvgs = self.analyzer.detect_fair_value_gap(df)
            
            current_price = df['close'].iloc[-1]
            
            # Priority 1: Recent Order Block
            if order_blocks:
                ob = order_blocks[-1]  # Most recent
                entry = ob['price']
                
                if direction == 'bullish':
                    sl = ob['bottom'] * 0.999  # Below OB
                    tp = entry + (entry - sl) * 1.5  # 1:1.5 R:R
                else:
                    sl = ob['top'] * 1.001  # Above OB
                    tp = entry - (sl - entry) * 1.5  # 1:1.5 R:R
                
                logger.info(f"✅ LTF Entry found: Order Block at {entry}")
                return {
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "direction": "buy" if direction == "bullish" else "sell",
                    "entry_type": "Order Block",
                    "timeframe": ltf,
                    "analysis_time": datetime.now().isoformat()
                }
            
            # Priority 2: Fair Value Gap
            elif fvgs:
                fvg = fvgs[-1]  # Most recent
                entry = (fvg['top'] + fvg['bottom']) / 2
                
                if direction == 'bullish':
                    sl = fvg['bottom'] * 0.999
                    tp = entry + (entry - sl) * 1.5
                else:
                    sl = fvg['top'] * 1.001
                    tp = entry - (sl - entry) * 1.5
                
                logger.info(f"✅ LTF Entry found: FVG at {entry}")
                return {
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "direction": "buy" if direction == "bullish" else "sell",
                    "entry_type": "Fair Value Gap",
                    "timeframe": ltf,
                    "analysis_time": datetime.now().isoformat()
                }
            
            else:
                logger.info(f"❌ No LTF entry model found")
                return {"entry": None, "reason": "No entry model found"}
                
        except Exception as e:
            logger.error(f"❌ LTF entry error: {str(e)}")
            return {"entry": None, "error": str(e)}
    
    def confluence_score(self, htf_analysis: Dict, mtf_analysis: Dict, ltf_analysis: Dict) -> Tuple[int, List[str]]:
        """
        Calculate confluence score based on REAL detected conditions
        
        Args:
            htf_analysis: HTF analysis result
            mtf_analysis: MTF analysis result
            ltf_analysis: LTF analysis result
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 0
        reasons = []
        
        # HTF Order Block detected (+25 points)
        if htf_analysis.get("htf_ob") and len(htf_analysis["htf_ob"]) > 0:
            score += 25
            reasons.append("HTF Order Block detected: +25")
        else:
            reasons.append("HTF Order Block not found: +0")
        
        # MTF BOS confirmed (+20 points)
        if mtf_analysis.get("confirmed"):
            score += 20
            reasons.append("MTF Break of Structure confirmed: +20")
        else:
            reasons.append("MTF BOS not confirmed: +0")
        
        # LTF entry model found (+20 points)
        if ltf_analysis.get("entry") is not None:
            score += 20
            reasons.append(f"LTF entry model found ({ltf_analysis.get('entry_type', 'Unknown')}): +20")
        else:
            reasons.append("LTF entry model not found: +0")
        
        # Fair Value Gap present (+15 points)
        # This is checked within LTF analysis, so we infer from entry type
        if ltf_analysis.get("entry_type") == "Fair Value Gap":
            score += 15
            reasons.append("Fair Value Gap present at entry: +15")
        else:
            reasons.append("Fair Value Gap not present: +0")
        
        # Liquidity zones present (+20 points)
        if htf_analysis.get("htf_liquidity") and len(htf_analysis["htf_liquidity"]) > 0:
            score += 20
            reasons.append("Liquidity zones detected: +20")
        else:
            reasons.append("Liquidity zones not found: +0")
        
        logger.info(f"📊 Confluence score calculated: {score}/100 with {len(reasons)} factors")
        return score, reasons
    
    async def analyze_mtf_confluence(
        self, 
        symbol: str, 
        entry_tf: str = "5m",
        htf: str = "4h", 
        mtf: str = "1h"
    ) -> ConfluenceResult:
        """
        Complete Multi-Timeframe confluence analysis using REAL market data
        
        Args:
            symbol: Trading pair symbol
            entry_tf: Entry timeframe (LTF)
            htf: Higher timeframe
            mtf: Medium timeframe
            
        Returns:
            ConfluenceResult with complete analysis
        """
        logger.info(f"🚀 Starting REAL MTF confluence analysis for {symbol}")
        
        # Step 1: Analyze HTF bias using real Binance data
        htf_analysis = await self.analyze_htf_bias(symbol, htf)
        
        # Step 2: Find MTF confirmation using real Binance data
        mtf_analysis = await self.find_mtf_confirmation(symbol, mtf, htf_analysis)
        
        # Step 3: Find LTF entry using real Binance data
        ltf_analysis = await self.find_ltf_entry(symbol, entry_tf, mtf_analysis)
        
        # Step 4: Calculate REAL confluence score
        score, reasons = self.confluence_score(htf_analysis, mtf_analysis, ltf_analysis)
        
        # Step 5: Apply hard rules
        bias = htf_analysis.get("bias", "neutral")
        entry = ltf_analysis.get("entry") if score >= 60 else None
        
        # HARD RULE: Never generate conflicting signals
        if bias == "bearish" and ltf_analysis.get("direction") == "buy":
            entry = None
            reasons.append("❌ Signal rejected: BUY conflicts with bearish HTF bias")
        elif bias == "bullish" and ltf_analysis.get("direction") == "sell":
            entry = None
            reasons.append("❌ Signal rejected: SELL conflicts with bullish HTF bias")
        
        # HARD RULE: Minimum confluence score
        if score < 60:
            entry = None
            reasons.append(f"❌ Signal rejected: Confluence score {score} < 60")
        
        result = ConfluenceResult(
            confluence_score=score,
            bias=bias,
            entry=entry,
            stop_loss=ltf_analysis.get("sl"),
            take_profit=ltf_analysis.get("tp"),
            reasons=reasons,
            htf_analysis=htf_analysis,
            mtf_analysis=mtf_analysis,
            ltf_analysis=ltf_analysis
        )
        
        logger.info(f"🎯 MTF Analysis complete: Score {score}, Bias {bias}, Entry: {entry}")
        return result