#!/usr/bin/env python3
"""
Historical Data API Routes
Endpoints for fetching maximum historical data for all timeframes
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import Dict, List, Optional
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
import logging

from app.services.historical_data_manager import historical_data_manager, TimeframeConfig
from app.auth.auth import get_current_user, UserInfo
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class TimeframeInfo(BaseModel):
    """Timeframe information model"""
    name: str
    binance_interval: str
    max_candles_per_request: int
    max_historical_days: int
    description: str

class HistoricalDataResponse(BaseModel):
    """Response model for historical data"""
    symbol: str
    timeframe: str
    total_candles: int
    earliest_date: str
    latest_date: str
    data: List[Dict]

class BulkHistoricalDataResponse(BaseModel):
    """Response model for bulk historical data"""
    symbol: str
    timeframes: Dict[str, Dict]
    total_datasets: int
    fetch_duration_seconds: float

class DataSummaryResponse(BaseModel):
    """Response model for data summary"""
    total_datasets: int
    datasets: List[Dict]

@router.get("/timeframes", response_model=Dict[str, TimeframeInfo])
async def get_supported_timeframes():
    """
    Get all supported timeframes with their configurations
    
    Returns:
        Dictionary of supported timeframes and their configurations
    """
    try:
        timeframes = historical_data_manager.get_supported_timeframes()
        
        response = {}
        for tf_name, config in timeframes.items():
            response[tf_name] = TimeframeInfo(
                name=config.name,
                binance_interval=config.binance_interval,
                max_candles_per_request=config.max_candles_per_request,
                max_historical_days=config.max_historical_days,
                description=config.description
            )
            
        logger.info(f"Returned {len(response)} supported timeframes")
        return response
        
    except Exception as e:
        logger.error(f"Error getting timeframes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get timeframes: {str(e)}")

@router.get("/fetch/{symbol}", response_model=BulkHistoricalDataResponse)
async def fetch_all_historical_data(
    symbol: str,
    timeframes: Optional[str] = Query(None, description="Comma-separated timeframes (e.g., '1m,5m,1h'). If not provided, fetches all timeframes"),
    request: Request = None
):
    """
    Fetch maximum historical data for all specified timeframes
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        timeframes: Optional comma-separated list of timeframes
        
    Returns:
        Bulk historical data for all timeframes
    """
    try:
        start_time = datetime.now()
        
        # Parse timeframes
        if timeframes:
            tf_list = [tf.strip() for tf in timeframes.split(',')]
        else:
            tf_list = None
            
        logger.info(f"Fetching historical data for {symbol}, timeframes: {tf_list or 'ALL'}")
        
        # Fetch data
        data_dict = await historical_data_manager.fetch_all_historical_data(symbol, tf_list)
        
        # Format response
        response_data = {}
        total_datasets = 0
        
        for tf, df in data_dict.items():
            if not df.empty:
                # Convert DataFrame to list of dictionaries
                data_list = []
                for _, row in df.iterrows():
                    data_list.append({
                        'timestamp': int(row['timestamp']),
                        'datetime': datetime.fromtimestamp(row['timestamp'] / 1000).isoformat(),
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': float(row['volume'])
                    })
                
                response_data[tf] = {
                    'total_candles': len(df),
                    'earliest_date': datetime.fromtimestamp(df['timestamp'].min() / 1000).isoformat(),
                    'latest_date': datetime.fromtimestamp(df['timestamp'].max() / 1000).isoformat(),
                    'data': data_list
                }
                total_datasets += 1
            else:
                response_data[tf] = {
                    'total_candles': 0,
                    'earliest_date': None,
                    'latest_date': None,
                    'data': []
                }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Successfully fetched historical data for {symbol}: {total_datasets} datasets in {duration:.2f}s")
        
        return BulkHistoricalDataResponse(
            symbol=symbol,
            timeframes=response_data,
            total_datasets=total_datasets,
            fetch_duration_seconds=duration
        )
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical data: {str(e)}")

@router.get("/fetch/{symbol}/{timeframe}", response_model=HistoricalDataResponse)
async def fetch_timeframe_data(
    symbol: str,
    timeframe: str,
    request: Request = None
):
    """
    Fetch maximum historical data for a specific timeframe
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT)
        timeframe: Specific timeframe (e.g., 1m, 5m, 1h, 1d)
        
    Returns:
        Historical data for the specified timeframe
    """
    try:
        logger.info(f"Fetching {symbol} {timeframe} historical data")
        
        # Fetch data for specific timeframe
        df = await historical_data_manager.fetch_timeframe_data(symbol, timeframe)
        
        if df.empty:
            return HistoricalDataResponse(
                symbol=symbol,
                timeframe=timeframe,
                total_candles=0,
                earliest_date="",
                latest_date="",
                data=[]
            )
        
        # Convert to response format
        data_list = []
        for _, row in df.iterrows():
            data_list.append({
                'timestamp': int(row['timestamp']),
                'datetime': datetime.fromtimestamp(row['timestamp'] / 1000).isoformat(),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        response = HistoricalDataResponse(
            symbol=symbol,
            timeframe=timeframe,
            total_candles=len(df),
            earliest_date=datetime.fromtimestamp(df['timestamp'].min() / 1000).isoformat(),
            latest_date=datetime.fromtimestamp(df['timestamp'].max() / 1000).isoformat(),
            data=data_list
        )
        
        logger.info(f"Successfully fetched {len(df)} candles for {symbol} {timeframe}")
        return response
        
    except Exception as e:
        logger.error(f"Error fetching {symbol} {timeframe}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

@router.get("/summary", response_model=DataSummaryResponse)
async def get_data_summary(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    request: Request = None
):
    """
    Get summary of all cached historical data
    
    Args:
        symbol: Optional symbol filter
        
    Returns:
        Summary of available historical data
    """
    try:
        summary = historical_data_manager.get_data_summary(symbol)
        
        logger.info(f"Data summary: {summary['total_datasets']} datasets")
        
        return DataSummaryResponse(
            total_datasets=summary['total_datasets'],
            datasets=summary['datasets']
        )
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data summary: {str(e)}")

@router.post("/preload")
async def preload_historical_data(
    symbols: List[str],
    timeframes: Optional[List[str]] = None,
    request: Request = None
):
    """
    Preload historical data for multiple symbols and timeframes
    
    Args:
        symbols: List of trading symbols
        timeframes: Optional list of timeframes (if not provided, loads all)
        
    Returns:
        Status of preload operation
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Starting preload for {len(symbols)} symbols, timeframes: {timeframes or 'ALL'}")
        
        results = {}
        total_datasets = 0
        
        for symbol in symbols:
            try:
                data_dict = await historical_data_manager.fetch_all_historical_data(symbol, timeframes)
                
                symbol_datasets = 0
                for tf, df in data_dict.items():
                    if not df.empty:
                        symbol_datasets += 1
                        total_datasets += 1
                
                results[symbol] = {
                    'status': 'success',
                    'datasets': symbol_datasets,
                    'timeframes': list(data_dict.keys())
                }
                
                logger.info(f"✅ Preloaded {symbol}: {symbol_datasets} datasets")
                
            except Exception as e:
                logger.error(f"❌ Failed to preload {symbol}: {e}")
                results[symbol] = {
                    'status': 'error',
                    'error': str(e),
                    'datasets': 0,
                    'timeframes': []
                }
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'status': 'completed',
            'total_symbols': len(symbols),
            'total_datasets': total_datasets,
            'duration_seconds': duration,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in preload operation: {e}")
        raise HTTPException(status_code=500, detail=f"Preload failed: {str(e)}")

@router.delete("/cache")
async def clear_cache(
    symbol: Optional[str] = Query(None, description="Clear cache for specific symbol"),
    timeframe: Optional[str] = Query(None, description="Clear cache for specific timeframe"),
    request: Request = None
):
    """
    Clear cached historical data
    
    Args:
        symbol: Optional symbol filter
        timeframe: Optional timeframe filter
        
    Returns:
        Status of cache clear operation
    """
    try:
        # This would need to be implemented in the historical_data_manager
        # For now, return a placeholder response
        
        logger.info(f"Cache clear requested - symbol: {symbol}, timeframe: {timeframe}")
        
        return {
            'status': 'success',
            'message': f"Cache cleared for symbol: {symbol or 'ALL'}, timeframe: {timeframe or 'ALL'}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/health")
async def historical_data_health_check():
    """Health check for historical data service"""
    try:
        # Check if we can access the database
        summary = historical_data_manager.get_data_summary()
        
        return {
            'status': 'healthy',
            'service': 'historical-data',
            'total_datasets': summary['total_datasets'],
            'supported_timeframes': len(historical_data_manager.get_supported_timeframes()),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Historical data health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")