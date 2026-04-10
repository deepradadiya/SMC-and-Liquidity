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
                
                # MTF Confluence History Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mtf_confluence_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        htf TEXT NOT NULL,
                        mtf TEXT NOT NULL,
                        ltf TEXT NOT NULL,
                        confluence_score INTEGER NOT NULL,
                        bias TEXT NOT NULL,
                        entry_price REAL,
                        stop_loss REAL,
                        take_profit REAL,
                        signal_valid BOOLEAN NOT NULL,
                        htf_analysis TEXT,  -- JSON string
                        mtf_analysis TEXT,  -- JSON string
                        ltf_analysis TEXT,  -- JSON string
                        reasons TEXT,       -- JSON array of reasons
                        market_status TEXT DEFAULT 'analyzing',
                        next_analysis_in INTEGER DEFAULT 5,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_mtf_history_symbol_time 
                    ON mtf_confluence_history(symbol, timestamp DESC)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_mtf_history_timeframes 
                    ON mtf_confluence_history(htf, mtf, ltf)
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
    
    def store_mtf_confluence_history(self, symbol: str, htf: str, mtf: str, ltf: str, 
                                   confluence_data: dict) -> int:
        """Store MTF confluence analysis in history table"""
        import json
        from datetime import datetime
        
        def json_serializer(obj):
            """JSON serializer for objects not serializable by default json code"""
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy arrays
                return obj.tolist()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        query = """
            INSERT INTO mtf_confluence_history (
                symbol, htf, mtf, ltf, confluence_score, bias, entry_price, 
                stop_loss, take_profit, signal_valid, htf_analysis, mtf_analysis, 
                ltf_analysis, reasons, market_status, next_analysis_in
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            symbol,
            htf,
            mtf, 
            ltf,
            confluence_data.get('confluence_score', 0),
            confluence_data.get('bias', 'neutral'),
            confluence_data.get('entry'),
            confluence_data.get('stop_loss'),
            confluence_data.get('take_profit'),
            confluence_data.get('signal_valid', False),
            json.dumps(confluence_data.get('htf_analysis', {}), default=json_serializer),
            json.dumps(confluence_data.get('mtf_analysis', {}), default=json_serializer),
            json.dumps(confluence_data.get('ltf_analysis', {}), default=json_serializer),
            json.dumps(confluence_data.get('reasons', []), default=json_serializer),
            confluence_data.get('market_status', 'analyzing'),
            confluence_data.get('next_analysis_in', 5)
        )
        
        return self.execute_insert(query, params)
    
    def get_mtf_confluence_history(self, symbol: str, days: int = 1, 
                                 htf: str = None, mtf: str = None, ltf: str = None):
        """Get MTF confluence history for a symbol within specified days"""
        query = """
            SELECT * FROM mtf_confluence_history 
            WHERE symbol = ? AND timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        params = [symbol]
        
        # Add timeframe filters if specified
        if htf:
            query += " AND htf = ?"
            params.append(htf)
        if mtf:
            query += " AND mtf = ?"
            params.append(mtf)
        if ltf:
            query += " AND ltf = ?"
            params.append(ltf)
            
        query += " ORDER BY timestamp DESC"
        
        return self.execute_query(query, tuple(params))

# Global database manager instance
db_manager = DatabaseManager()