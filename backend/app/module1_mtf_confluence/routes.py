"""
Multi-Timeframe Analysis API Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from .mtf_confluence import ConfluenceEngine, TimeframeHierarchy

router = APIRouter()
logger = logging.getLogger(__name__)


class MTFAnalysisRequest(BaseModel):
    """Request model for MTF analysis"""
    symbol: str
    entry_tf: Optional[str] = "5m"
    htf: Optional[str] = "4h"
    mtf: Optional[str] = "1h"


class MTFAnalysisResponse(BaseModel):
    """Response model for MTF analysis"""
    confluence_score: int
    bias: str
    entry: Optional[float]
    sl: Optional[float]
    tp: Optional[float]
    reasons: list
    htf_analysis: dict
    mtf_analysis: dict
    ltf_analysis: dict
    signal_valid: bool
    analysis_timestamp: str
    next_analysis_in: Optional[int] = 5
    market_status: Optional[str] = "analyzing"


@router.post("/mtf-analyze", response_model=MTFAnalysisResponse)
async def analyze_mtf_confluence(request: MTFAnalysisRequest):
    """
    Analyze Multi-Timeframe confluence for trading signals
    
    This endpoint performs comprehensive MTF analysis:
    1. Analyzes HTF bias and key levels
    2. Finds MTF confirmation aligned with HTF
    3. Identifies precise LTF entry points
    4. Calculates confluence score (0-100)
    5. Only generates signals with score >= 60
    
    Rules:
    - Never generates BUY signal if HTF bias is bearish
    - Never generates SELL signal if HTF bias is bullish
    - Logs each confluence check with reasoning
    """
    try:
        logger.info(f"MTF Analysis request: {request.symbol} - HTF:{request.htf}, MTF:{request.mtf}, LTF:{request.entry_tf}")
        
        # Validate timeframes
        try:
            TimeframeHierarchy.get_timeframe_type(request.htf)
            TimeframeHierarchy.get_timeframe_type(request.mtf)
            TimeframeHierarchy.get_timeframe_type(request.entry_tf)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe: {str(e)}")
        
        # Initialize confluence engine
        confluence_engine = ConfluenceEngine()
        
        # Perform MTF confluence analysis
        result = await confluence_engine.analyze_mtf_confluence(
            symbol=request.symbol,
            entry_tf=request.entry_tf,
            htf=request.htf,
            mtf=request.mtf
        )
        
        # Prepare response
        response = MTFAnalysisResponse(
            confluence_score=result.confluence_score,
            bias=result.bias,
            entry=result.entry,
            sl=result.stop_loss,
            tp=result.take_profit,
            reasons=result.reasons,
            htf_analysis=result.htf_analysis,
            mtf_analysis=result.mtf_analysis,
            ltf_analysis=result.ltf_analysis,
            signal_valid=result.entry is not None and result.confluence_score >= 60,
            analysis_timestamp=result.htf_analysis.get("analysis_time", ""),
            next_analysis_in=getattr(result, 'next_analysis_in', 5),
            market_status=getattr(result, 'market_status', 'analyzing')
        )
        
        logger.info(f"MTF Analysis complete: Score {result.confluence_score}, Valid: {response.signal_valid}")
        return response
        
    except Exception as e:
        logger.error(f"Error in MTF analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MTF analysis failed: {str(e)}")


@router.get("/mtf-timeframes")
async def get_available_mtf_timeframes():
    """Get available timeframes for MTF analysis"""
    return {
        "htf_timeframes": TimeframeHierarchy.HTF_TIMEFRAMES,
        "mtf_timeframes": TimeframeHierarchy.MTF_TIMEFRAMES,
        "ltf_timeframes": TimeframeHierarchy.LTF_TIMEFRAMES,
        "recommended_combinations": [
            {"htf": "4h", "mtf": "1h", "ltf": "5m"},
            {"htf": "1d", "mtf": "4h", "ltf": "15m"},
            {"htf": "4h", "mtf": "15m", "ltf": "1m"}
        ]
    }


@router.get("/mtf-status/{symbol}")
async def get_mtf_status(symbol: str, htf: str = "4h"):
    """Get quick MTF status for a symbol"""
    try:
        confluence_engine = ConfluenceEngine()
        htf_analysis = await confluence_engine.analyze_htf_bias(symbol, htf)
        
        return {
            "symbol": symbol,
            "htf_bias": htf_analysis.get("bias", "neutral"),
            "htf_ob_count": len(htf_analysis.get("htf_ob", [])),
            "htf_liquidity_count": len(htf_analysis.get("htf_liquidity", [])),
            "analysis_time": htf_analysis.get("analysis_time"),
            "status": "active" if htf_analysis.get("bias") != "neutral" else "neutral"
        }
        
    except Exception as e:
        logger.error(f"Error getting MTF status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get MTF status: {str(e)}")


@router.get("/mtf-history/{symbol}")
async def get_mtf_confluence_history(
    symbol: str,
    days: int = 1,
    htf: Optional[str] = None,
    mtf: Optional[str] = None,
    ltf: Optional[str] = None
):
    """
    Get MTF confluence history for a symbol
    
    Args:
        symbol: Trading pair symbol
        days: Number of days to look back (1, 7, 30, 365)
        htf: Filter by higher timeframe (optional)
        mtf: Filter by medium timeframe (optional)
        ltf: Filter by lower timeframe (optional)
    """
    try:
        from ..core.database import db_manager
        import json
        
        # Validate days parameter
        valid_days = [1, 7, 30, 365]
        if days not in valid_days:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid days parameter. Must be one of: {valid_days}"
            )
        
        # Get historical data
        history_data = db_manager.get_mtf_confluence_history(
            symbol=symbol,
            days=days,
            htf=htf,
            mtf=mtf,
            ltf=ltf
        )
        
        # Format response
        formatted_history = []
        for row in history_data:
            try:
                formatted_entry = {
                    "id": row[0],
                    "symbol": row[1],
                    "htf": row[2],
                    "mtf": row[3],
                    "ltf": row[4],
                    "confluence_score": row[5],
                    "bias": row[6],
                    "entry_price": row[7],
                    "stop_loss": row[8],
                    "take_profit": row[9],
                    "signal_valid": bool(row[10]),
                    "htf_analysis": json.loads(row[11]) if row[11] else {},
                    "mtf_analysis": json.loads(row[12]) if row[12] else {},
                    "ltf_analysis": json.loads(row[13]) if row[13] else {},
                    "reasons": json.loads(row[14]) if row[14] else [],
                    "market_status": row[15],
                    "next_analysis_in": row[16],
                    "timestamp": row[17],
                    "created_at": row[18]
                }
                formatted_history.append(formatted_entry)
            except Exception as e:
                logger.error(f"Error formatting history entry: {e}")
                continue
        
        return {
            "symbol": symbol,
            "days": days,
            "filters": {
                "htf": htf,
                "mtf": mtf,
                "ltf": ltf
            },
            "total_entries": len(formatted_history),
            "history": formatted_history
        }
        
    except Exception as e:
        logger.error(f"Error getting MTF history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get MTF history: {str(e)}")


@router.get("/mtf-history-summary/{symbol}")
async def get_mtf_history_summary(symbol: str, days: int = 7):
    """
    Get MTF confluence history summary with statistics
    
    Args:
        symbol: Trading pair symbol
        days: Number of days to analyze
    """
    try:
        from ..core.database import db_manager
        import json
        from collections import Counter
        
        # Get historical data
        history_data = db_manager.get_mtf_confluence_history(symbol=symbol, days=days)
        
        if not history_data:
            return {
                "symbol": symbol,
                "days": days,
                "total_analyses": 0,
                "summary": "No historical data available"
            }
        
        # Calculate statistics
        total_analyses = len(history_data)
        valid_signals = sum(1 for row in history_data if row[10])  # signal_valid column
        
        # Bias distribution
        bias_counts = Counter(row[6] for row in history_data)  # bias column
        
        # Average confluence score
        scores = [row[5] for row in history_data]  # confluence_score column
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Score distribution
        high_confidence = sum(1 for score in scores if score >= 80)
        medium_confidence = sum(1 for score in scores if 60 <= score < 80)
        low_confidence = sum(1 for score in scores if score < 60)
        
        return {
            "symbol": symbol,
            "days": days,
            "total_analyses": total_analyses,
            "valid_signals": valid_signals,
            "signal_rate": round((valid_signals / total_analyses) * 100, 2) if total_analyses > 0 else 0,
            "average_confluence_score": round(avg_score, 2),
            "bias_distribution": dict(bias_counts),
            "confidence_distribution": {
                "high_confidence_80_plus": high_confidence,
                "medium_confidence_60_79": medium_confidence,
                "low_confidence_below_60": low_confidence
            },
            "latest_analysis": history_data[0][17] if history_data else None  # timestamp
        }
        
    except Exception as e:
        logger.error(f"Error getting MTF history summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get MTF history summary: {str(e)}")