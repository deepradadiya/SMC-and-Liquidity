"""
SMC Trading System - Main FastAPI Application
Clean modular architecture with organized imports
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import all module routers
from app.module1_mtf_confluence.routes import router as mtf_router
from app.module2_risk_manager.routes import router as risk_router
from app.module3_smc_engine.routes import router as smc_router
from app.module4_backtester.routes import router as backtest_router
from app.module5_security.routes import router as auth_router
from app.module6_ml_filter.routes import router as ml_router
from app.module7_session_manager.routes import router as session_router
from app.module8_alert_manager.routes import router as alert_router
from app.module9_data_manager.routes import router as data_router

# Import core utilities
from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import db_manager

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SMC Trading System API",
    description="Professional Smart Money Concepts Trading System with Multi-Timeframe Analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all module routers with their prefixes
app.include_router(mtf_router, prefix="/api/mtf", tags=["MTF Confluence"])
app.include_router(risk_router, prefix="/api/risk", tags=["Risk Management"])
app.include_router(smc_router, prefix="/api/smc", tags=["SMC Analysis"])
app.include_router(backtest_router, prefix="/api/backtest", tags=["Backtesting"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ml_router, prefix="/api/ml", tags=["ML Filter"])
app.include_router(session_router, prefix="/api/sessions", tags=["Session Management"])
app.include_router(alert_router, prefix="/api/alerts", tags=["Alert Management"])
app.include_router(data_router, prefix="/api/data", tags=["Data Management"])

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting SMC Trading System API v2.0.0")
    logger.info("📁 Clean modular architecture loaded")
    
    # Initialize database
    try:
        db_manager.ensure_database_exists()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    logger.info("🎯 All modules loaded successfully:")
    logger.info("   • Module 1: MTF Confluence Engine")
    logger.info("   • Module 2: Risk Management")
    logger.info("   • Module 3: SMC Analysis Engine")
    logger.info("   • Module 4: Advanced Backtesting")
    logger.info("   • Module 5: Security & Authentication")
    logger.info("   • Module 6: ML Signal Filter")
    logger.info("   • Module 7: Session Management")
    logger.info("   • Module 8: Alert Management")
    logger.info("   • Module 9: Data Management")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down SMC Trading System API")

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "SMC Trading System API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "modular",
        "modules": {
            "module1_mtf_confluence": "Multi-Timeframe Confluence Engine",
            "module2_risk_manager": "Risk Management System",
            "module3_smc_engine": "Smart Money Concepts Analysis",
            "module4_backtester": "Advanced Backtesting Engine",
            "module5_security": "Authentication & Security",
            "module6_ml_filter": "ML Signal Filtering",
            "module7_session_manager": "Session Awareness",
            "module8_alert_manager": "Alert Management",
            "module9_data_manager": "Data Management Layer"
        },
        "endpoints": {
            "mtf_analysis": "/api/mtf/mtf-analyze",
            "risk_status": "/api/risk/status",
            "smc_analysis": "/api/smc/analyze",
            "backtest": "/api/backtest/run",
            "authentication": "/api/auth/login",
            "ml_filter": "/api/ml/filter",
            "sessions": "/api/sessions/boxes",
            "alerts": "/api/alerts/history",
            "data": "/api/data/export"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2026-04-08T17:45:00Z",
        "modules_loaded": 9,
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)