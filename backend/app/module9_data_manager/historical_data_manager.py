#!/usr/bin/env python3
"""
Enhanced Historical Data Manager
Fetches maximum available historical data for all timeframes
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import sqlite3
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class TimeframeConfig:
    """Configuration for each timeframe"""
    name: str
    binance_interval: str
    max_candles_per_request: int
    max_historical_days: int
    description: str

class HistoricalDataManager:
    """Enhanced manager for fetching maximum historical data"""
    
    # All supported timeframes with their configurations
    TIMEFRAMES = {
        "1m": TimeframeConfig("1m", "1m", 1000, 30, "1 Minute"),
        "3m": TimeframeConfig("3m", "3m", 1000, 90, "3 Minutes"),
        "5m": TimeframeConfig("5m", "5m", 1000, 150, "5 Minutes"),
        "15m": TimeframeConfig("15m", "15m", 1000, 450, "15 Minutes"),
        "30m": TimeframeConfig("30m", "30m", 1000, 900, "30 Minutes"),
        "1h": TimeframeConfig("1h", "1h", 1000, 1800, "1 Hour"),
        "2h": TimeframeConfig("2h", "2h", 1000, 3600, "2 Hours"),
        "4h": TimeframeConfig("4h", "4h", 1000, 7200, "4 Hours"),
        "6h": TimeframeConfig("6h", "6h", 1000, 10800, "6 Hours"),
        "8h": TimeframeConfig("8h", "8h", 1000, 14400, "8 Hours"),
        "12h": TimeframeConfig("12h", "12h", 1000, 21600, "12 Hours"),
        "1d": TimeframeConfig("1d", "1d", 1000, 365000, "1 Day"),
        "3d": TimeframeConfig("3d", "3d", 1000, 1095000, "3 Days"),
        "1w": TimeframeConfig("1w", "1w", 1000, 2555000, "1 Week"),
        "1M": TimeframeConfig("1M", "1M", 1000, 36500000, "1 Month")
    }
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.session = None
        self.db_path = "historical_data.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for caching historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timeframe_timestamp 
            ON historical_data(symbol, timeframe, timestamp)
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_metadata (
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                earliest_timestamp INTEGER,
                latest_timestamp INTEGER,
                total_candles INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(symbol, timeframe)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            
    def get_supported_timeframes(self) -> Dict[str, TimeframeConfig]:
        """Get all supported timeframes"""
        return self.TIMEFRAMES.copy()
        
    async def fetch_all_historical_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch maximum historical data for all specified timeframes
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframes: List of timeframes to fetch (if None, fetches all)
            
        Returns:
            Dictionary with timeframe as key and DataFrame as value
        """
        if timeframes is None:
            timeframes = list(self.TIMEFRAMES.keys())
            
        results = {}
        
        logger.info(f"Starting historical data fetch for {symbol} - {len(timeframes)} timeframes")
        
        # Fetch data for each timeframe concurrently
        tasks = []
        for tf in timeframes:
            if tf in self.TIMEFRAMES:
                task = self.fetch_timeframe_data(symbol, tf)
                tasks.append((tf, task))
            else:
                logger.warning(f"Unsupported timeframe: {tf}")
                
        # Execute all tasks concurrently
        for tf, task in tasks:
            try:
                df = await task
                results[tf] = df
                logger.info(f"✅ {symbol} {tf}: {len(df)} candles fetched")
            except Exception as e:
                logger.error(f"❌ Failed to fetch {symbol} {tf}: {e}")
                results[tf] = pd.DataFrame()
                
        return results
        
    async def fetch_timeframe_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Fetch maximum historical data for a specific timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
            
        config = self.TIMEFRAMES[timeframe]
        
        # Check if we have cached data
        cached_df = self._get_cached_data(symbol, timeframe)
        if not cached_df.empty:
            # Check if we need to update with recent data
            latest_cached = cached_df['timestamp'].max()
            now = int(datetime.now().timestamp() * 1000)
            
            # If cached data is recent (within last hour), return it
            if now - latest_cached < 3600000:  # 1 hour in milliseconds
                logger.info(f"Using cached data for {symbol} {timeframe}: {len(cached_df)} candles")
                return cached_df
                
        # Fetch fresh data from API
        logger.info(f"Fetching fresh data for {symbol} {timeframe}")
        df = await self._fetch_from_binance(symbol, config)
        
        # Cache the data
        if not df.empty:
            self._cache_data(symbol, timeframe, df)
            
        return df
        
    async def _fetch_from_binance(self, symbol: str, config: TimeframeConfig) -> pd.DataFrame:
        """
        Fetch data from Binance API with pagination to get maximum history
        
        Args:
            symbol: Trading symbol
            config: Timeframe configuration
            
        Returns:
            DataFrame with historical data
        """
        session = await self.get_session()
        all_data = []
        
        # Calculate how far back we can go
        now = datetime.now()
        max_start_date = now - timedelta(days=config.max_historical_days)
        
        # Start from the earliest possible date
        end_time = int(now.timestamp() * 1000)
        
        logger.info(f"Fetching {symbol} {config.name} from {max_start_date} to {now}")
        
        batch_count = 0
        max_batches = 50  # Prevent infinite loops
        
        while batch_count < max_batches:
            try:
                params = {
                    'symbol': symbol,
                    'interval': config.binance_interval,
                    'limit': config.max_candles_per_request,
                    'endTime': end_time
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if not data or len(data) == 0:
                            logger.info(f"No more data available for {symbol} {config.name}")
                            break
                            
                        # Convert to our format
                        batch_df = self._convert_binance_data(data)
                        
                        if batch_df.empty:
                            break
                            
                        all_data.append(batch_df)
                        
                        # Check if we've reached the maximum historical date
                        earliest_timestamp = batch_df['timestamp'].min()
                        earliest_date = datetime.fromtimestamp(earliest_timestamp / 1000)
                        
                        if earliest_date <= max_start_date:
                            logger.info(f"Reached maximum historical date for {symbol} {config.name}")
                            break
                            
                        # Set end_time for next batch (earliest timestamp - 1ms)
                        end_time = earliest_timestamp - 1
                        batch_count += 1
                        
                        # Rate limiting
                        await asyncio.sleep(0.1)  # 100ms delay between requests
                        
                    elif response.status == 429:
                        # Rate limit hit, wait longer
                        logger.warning(f"Rate limit hit for {symbol} {config.name}, waiting...")
                        await asyncio.sleep(60)  # Wait 1 minute
                        
                    else:
                        logger.error(f"API error {response.status} for {symbol} {config.name}")
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching batch for {symbol} {config.name}: {e}")
                break
                
        # Combine all batches
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            # Remove duplicates and sort by timestamp
            combined_df = combined_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            combined_df = combined_df.reset_index(drop=True)
            
            logger.info(f"Successfully fetched {len(combined_df)} candles for {symbol} {config.name}")
            return combined_df
        else:
            logger.warning(f"No data fetched for {symbol} {config.name}")
            return pd.DataFrame()
            
    def _convert_binance_data(self, data: List) -> pd.DataFrame:
        """Convert Binance API response to DataFrame"""
        if not data:
            return pd.DataFrame()
            
        df_data = []
        for candle in data:
            df_data.append({
                'timestamp': int(candle[0]),
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            })
            
        return pd.DataFrame(df_data)
        
    def _get_cached_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Get cached data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT timestamp, open, high, low, close, volume
                FROM historical_data
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, timeframe))
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading cached data: {e}")
            return pd.DataFrame()
            
    def _cache_data(self, symbol: str, timeframe: str, df: pd.DataFrame):
        """Cache data to database"""
        if df.empty:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data for this symbol/timeframe
            cursor.execute(
                'DELETE FROM historical_data WHERE symbol = ? AND timeframe = ?',
                (symbol, timeframe)
            )
            
            # Insert new data
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO historical_data 
                    (symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, timeframe, int(row['timestamp']),
                    float(row['open']), float(row['high']), float(row['low']),
                    float(row['close']), float(row['volume'])
                ))
                
            # Update metadata
            cursor.execute('''
                INSERT OR REPLACE INTO data_metadata
                (symbol, timeframe, earliest_timestamp, latest_timestamp, total_candles)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                symbol, timeframe,
                int(df['timestamp'].min()),
                int(df['timestamp'].max()),
                len(df)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cached {len(df)} candles for {symbol} {timeframe}")
            
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            
    def get_data_summary(self, symbol: str = None) -> Dict:
        """Get summary of available data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if symbol:
                query = '''
                    SELECT symbol, timeframe, total_candles, 
                           datetime(earliest_timestamp/1000, 'unixepoch') as earliest_date,
                           datetime(latest_timestamp/1000, 'unixepoch') as latest_date,
                           last_updated
                    FROM data_metadata
                    WHERE symbol = ?
                    ORDER BY symbol, timeframe
                '''
                cursor = conn.execute(query, (symbol,))
            else:
                query = '''
                    SELECT symbol, timeframe, total_candles,
                           datetime(earliest_timestamp/1000, 'unixepoch') as earliest_date,
                           datetime(latest_timestamp/1000, 'unixepoch') as latest_date,
                           last_updated
                    FROM data_metadata
                    ORDER BY symbol, timeframe
                '''
                cursor = conn.execute(query)
                
            results = cursor.fetchall()
            conn.close()
            
            summary = {
                'total_datasets': len(results),
                'datasets': []
            }
            
            for row in results:
                summary['datasets'].append({
                    'symbol': row[0],
                    'timeframe': row[1],
                    'total_candles': row[2],
                    'earliest_date': row[3],
                    'latest_date': row[4],
                    'last_updated': row[5]
                })
                
            return summary
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {'total_datasets': 0, 'datasets': []}

# Global instance
historical_data_manager = HistoricalDataManager()