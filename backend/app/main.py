from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn
import json
import asyncio
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel

from app.routes import analysis, signals, backtest, mtf_analysis, risk, smc_precise, advanced_backtest, auth, ml, sessions, alerts, historical_data
from app.routes import data  # Import the enhanced data routes
from app.config import get_settings, validate_configuration
from app.utils.logger import setup_logging, get_logger
from app.utils.rate_limiter import limiter, rate_limit_exceeded_handler
from app.auth.auth import get_current_user

# Load environment variables
load_dotenv()

# Validate configuration
if not validate_configuration():
    exit(1)

# Setup logging
setup_logging()

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Predict endpoint models
class Candle(BaseModel):
    open_time: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class PredictRequest(BaseModel):
    candles: List[Candle]
    atr_sl_multiplier: float = 1.5

class PredictResponse(BaseModel):
    signal: str
    confidence: float
    entry: float
    stop_loss: float
    target: float
    rr_ratio: float
    xgb_pred: str
    rf_pred: str
    smc_pred: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            if websocket in self.active_connections and websocket.client_state.name == "CONNECTED":
                await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            # Remove the failed connection
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections.copy():  # Use copy to avoid modification during iteration
            try:
                # Check if connection is still open before sending
                if connection.client_state.name == "CONNECTED":
                    await connection.send_text(message)
                else:
                    disconnected.append(connection)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Background task for sending periodic updates
async def send_periodic_updates():
    """Send periodic market updates to all connected clients"""
    from app.services.data_manager import DataManager
    from datetime import datetime, timedelta
    
    # Initialize data manager for real market data
    data_manager = DataManager()
    
    while True:
        try:
            if manager.active_connections:
                try:
                    # Fetch real market data for major pairs
                    symbols = ["BTCUSDT", "ETHUSDT"]  # Only BTC and ETH for initial phase
                    price_data = {}
                    
                    # Get recent data (last 30 minutes to ensure we get data)
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(minutes=30)
                    
                    for symbol in symbols:
                        try:
                            # Get latest price data using correct method with dates
                            ohlcv_df = await data_manager.get_ohlcv(symbol, "1m", start_time, end_time)
                            
                            if not ohlcv_df.empty and len(ohlcv_df) >= 1:
                                # Get the most recent data
                                current = ohlcv_df.iloc[-1]
                                
                                current_price = float(current['close'])
                                
                                # Calculate change if we have previous data
                                change_pct = 0.0
                                if len(ohlcv_df) >= 2:
                                    previous = ohlcv_df.iloc[-2]
                                    previous_price = float(previous['close'])
                                    change_pct = ((current_price - previous_price) / previous_price) * 100
                                
                                price_data[symbol] = {
                                    "price": round(current_price, 2),
                                    "change": round(change_pct, 2),
                                    "volume": float(current['volume']),
                                    "high_24h": float(current['high']),
                                    "low_24h": float(current['low']),
                                    "timestamp": str(current['timestamp'])
                                }
                        except Exception as e:
                            logger.error(f"Failed to fetch data for {symbol}: {e}")
                            # Continue with other symbols
                            continue
                    
                    if price_data:
                        message = json.dumps({
                            "type": "price_update",
                            "data": price_data,
                            "timestamp": end_time.isoformat(),
                            "source": "live_data"
                        })
                        
                        await manager.broadcast(message)
                        logger.info(f"Broadcasted market data for {len(price_data)} symbols to {len(manager.active_connections)} connections")
                    else:
                        logger.warning("No price data available to broadcast")
                    
                except Exception as e:
                    logger.error(f"Error in periodic updates: {e}")
            else:
                logger.debug("No active WebSocket connections")
        except Exception as e:
            logger.error(f"Critical error in periodic updates: {e}")
        
        await asyncio.sleep(3)  # Update every 3 seconds for faster real-time data

app = FastAPI(
    title="SMC Trading System",
    description="Smart Money Concepts Algorithmic Trading Platform with Security",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None
)

# Start background task
@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    logger.info("Starting SMC Trading System...")
    asyncio.create_task(send_periodic_updates())

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(historical_data.router, prefix="/api/historical", tags=["historical-data"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(mtf_analysis.router, prefix="/api/mtf", tags=["mtf-analysis"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk-management"])
app.include_router(smc_precise.router, prefix="/api/smc", tags=["precise-smc"])
app.include_router(advanced_backtest.router, prefix="/api/advanced-backtest", tags=["advanced-backtest"])
app.include_router(ml.router, prefix="/api/ml", tags=["machine-learning"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["session-management"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alert-system"])

@app.get("/")
async def root():
    """Root endpoint with system information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "SMC Trading System API", 
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "docs_url": "/docs" if settings.is_development else "disabled",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.debug("Health check accessed")
    return {
        "status": "healthy", 
        "service": "smc-trading-system",
        "environment": settings.APP_ENV,
        "timestamp": "2024-01-01T00:00:00Z",
        "websocket_connections": len(manager.active_connections)
    }

@app.post("/predict", response_model=PredictResponse)
async def predict_signal(request: PredictRequest):
    """
    Predict trading signal using ML model
    """
    try:
        # For now, return a mock response since the ML model integration is complex
        # This prevents the 404 error while you can implement the full ML integration later
        
        if len(request.candles) < 10:
            raise HTTPException(status_code=400, detail="Send at least 10 candles")
        
        # Get the latest candle for entry price
        latest_candle = request.candles[-1]
        entry_price = latest_candle.close
        
        # Mock ATR calculation (you can replace with real ATR calculation)
        mock_atr = abs(latest_candle.high - latest_candle.low) * 0.8
        sl_distance = mock_atr * request.atr_sl_multiplier
        tp_distance = sl_distance * 2.0
        
        # Mock signal generation (replace with your ML model)
        import random
        signals = ["BUY", "SELL", "HOLD"]
        mock_signal = random.choice(signals)
        mock_confidence = random.uniform(60, 95)
        
        # Calculate stop loss and target based on signal
        if mock_signal == "BUY":
            stop_loss = round(entry_price - sl_distance, 4)
            target = round(entry_price + tp_distance, 4)
        elif mock_signal == "SELL":
            stop_loss = round(entry_price + sl_distance, 4)
            target = round(entry_price - tp_distance, 4)
        else:  # HOLD
            stop_loss = round(entry_price - sl_distance, 4)
            target = round(entry_price + tp_distance, 4)
        
        rr_ratio = round(tp_distance / (sl_distance + 1e-9), 2)
        
        response = PredictResponse(
            signal=mock_signal,
            confidence=round(mock_confidence, 2),
            entry=round(entry_price, 4),
            stop_loss=stop_loss,
            target=target,
            rr_ratio=rr_ratio,
            xgb_pred=mock_signal,
            rf_pred=mock_signal,
            smc_pred=mock_signal
        )
        
        logger.info(f"Generated prediction: {mock_signal} with {mock_confidence:.1f}% confidence")
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    try:
        await manager.connect(websocket)
        
        # Send initial connection message
        current_time = datetime.utcnow()
        await manager.send_personal_message(json.dumps({
            "type": "connection",
            "message": "Connected to ZERO money - Live Market Data",
            "timestamp": current_time.isoformat()
        }), websocket)
        
        # Send initial real market data
        try:
            from app.services.data_manager import DataManager
            from datetime import timedelta
            
            data_manager = DataManager()
            
            # Get current BTC price with a wider time range
            current_datetime = datetime.utcnow()
            end_time = current_datetime
            start_time = current_datetime - timedelta(hours=1)  # Last hour to ensure we get data
            
            btc_df = await data_manager.get_ohlcv("BTCUSDT", "1m", start_time, end_time)
            if not btc_df.empty:
                current_btc = btc_df.iloc[-1]
                await manager.send_personal_message(json.dumps({
                    "type": "price_update",
                    "data": {
                        "BTCUSDT": {
                            "price": float(current_btc['close']),
                            "change": 0.0,  # Will be calculated in next update
                            "volume": float(current_btc['volume']),
                            "timestamp": current_datetime.isoformat()
                        }
                    },
                    "source": "live_data"
                }), websocket)
        except Exception as e:
            logger.error(f"Failed to send initial market data: {e}")
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Echo back for now (can be enhanced for specific message handling)
                response_time = datetime.utcnow()
                await manager.send_personal_message(json.dumps({
                    "type": "echo",
                    "original": message,
                    "timestamp": response_time.isoformat()
                }), websocket)
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    import time
    
    start_time = time.time()
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(f"Response: {response.status_code} for {request.method} {request.url.path} in {duration:.3f}s")
    
    return response

if __name__ == "__main__":
    logger.info(f"Starting SMC Trading System in {settings.APP_ENV} mode")
    logger.info(f"Server will run on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.is_development,
        workers=settings.WORKERS if not settings.is_development else 1,
        log_level=settings.LOG_LEVEL.lower()
    )