"""
Database connection and management utilities
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connections and table creation"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager"""
        if db_path is None:
            # Default to backend directory
            backend_dir = Path(__file__).parent.parent.parent
            db_path = backend_dir / "smc_trading.db"
        
        self.db_path = str(db_path)
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure database file and basic tables exist"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create database file if it doesn't exist
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create basic tables
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        signal_type TEXT NOT NULL,
                        entry_price REAL,
                        stop_loss REAL,
                        take_profit REAL,
                        confidence REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        signal_id INTEGER,
                        entry_time DATETIME,
                        exit_time DATETIME,
                        entry_price REAL,
                        exit_price REAL,
                        pnl REAL,
                        pnl_percent REAL,
                        status TEXT,
                        FOREIGN KEY (signal_id) REFERENCES signals (id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS risk_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE,
                        daily_pnl REAL,
                        balance REAL,
                        trades_count INTEGER,
                        circuit_breaker_triggered BOOLEAN DEFAULT FALSE,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute insert query and return last row id"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Database insert error: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()