from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn
from dotenv import load_dotenv

from app.routes import analysis, signals, backtest, mtf_analysis, risk, smc_precise, advanced_backtest, auth, ml, sessions, alerts
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

app = FastAPI(
    title="SMC Trading System",
    description="Smart Money Concepts Algorithmic Trading Platform with Security",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None
)

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
        "timestamp": "2024-01-01T00:00:00Z"
    }

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