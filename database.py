import sqlite3
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from contextlib import contextmanager

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages the SQLite database for the crypto alert app."""
    
    def __init__(self, db_path: str = "data/crypto_alert.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Sets up the database with all the tables we need."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create the tables
                self._create_tables(cursor)
                
                # Add indexes for better performance
                self._create_indexes(cursor)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _create_tables(self, cursor):
        """Creates all the database tables."""
        # Table for tracking coins we're watching
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL UNIQUE,
                coin_name TEXT NOT NULL,
                threshold_above REAL,
                threshold_below REAL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for storing price history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                volume_24h REAL,
                market_cap REAL,
                price_change_24h REAL,
                price_change_percentage_24h REAL
            )
        """)
        
        # Table for tracking alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                current_price REAL NOT NULL,
                message TEXT NOT NULL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                notification_sent BOOLEAN DEFAULT 0
            )
        """)
        
        # Table for tracking notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 0,
                error_message TEXT
            )
        """)
        
        # Table for user preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                theme TEXT DEFAULT 'light',
                default_timeframe TEXT DEFAULT '24h',
                email_notifications BOOLEAN DEFAULT 1,
                webhook_notifications BOOLEAN DEFAULT 0,
                sms_notifications BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_indexes(self, cursor):
        """Creates database indexes to make queries faster."""
        # Indexes for price history queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_coin_timestamp ON price_history(coin_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)")
        
        # Indexes for alert queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_coin_triggered ON alerts(coin_id, triggered_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)")
        
        # Indexes for watchlist queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_coin_id ON watchlist(coin_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_enabled ON watchlist(enabled)")
    
    @contextmanager
    def _get_connection(self):
        """Gets a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable row factory for named columns
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # Watchlist operations
    def add_to_watchlist(self, coin_id: str, coin_name: str, threshold_above: Optional[float] = None, 
                         threshold_below: Optional[float] = None) -> bool:
        """Adds a coin to the watchlist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO watchlist 
                    (coin_id, coin_name, threshold_above, threshold_below, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (coin_id, coin_name, threshold_above, threshold_below))
                
                conn.commit()
                logger.info(f"Added {coin_id} to watchlist")
                return True
                
        except Exception as e:
            logger.error(f"Error adding {coin_id} to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, coin_id: str) -> bool:
        """Removes a coin from the watchlist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM watchlist WHERE coin_id = ?", (coin_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Removed {coin_id} from watchlist")
                    return True
                else:
                    logger.warning(f"Coin {coin_id} not found in watchlist")
                    return False
                    
        except Exception as e:
            logger.error(f"Error removing {coin_id} from watchlist: {e}")
            return False
    
    def get_watchlist(self) -> List[Dict[str, Any]]:
        """Gets all coins in the watchlist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM watchlist WHERE enabled = 1 ORDER BY coin_name")
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []
    
    def update_watchlist_thresholds(self, coin_id: str, threshold_above: Optional[float] = None, 
                                   threshold_below: Optional[float] = None) -> bool:
        """Updates the alert thresholds for a coin."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                update_fields = []
                params = []
                
                if threshold_above is not None:
                    update_fields.append("threshold_above = ?")
                    params.append(threshold_above)
                
                if threshold_below is not None:
                    update_fields.append("threshold_below = ?")
                    params.append(threshold_below)
                
                if not update_fields:
                    return False
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                params.append(coin_id)
                
                query = f"UPDATE watchlist SET {', '.join(update_fields)} WHERE coin_id = ?"
                cursor.execute(query, params)
                
                conn.commit()
                logger.info(f"Updated thresholds for {coin_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating thresholds for {coin_id}: {e}")
            return False
    
    # Price history operations
    def save_price_data(self, coin_id: str, price: float, volume_24h: Optional[float] = None,
                       market_cap: Optional[float] = None, price_change_24h: Optional[float] = None,
                       price_change_percentage_24h: Optional[float] = None) -> bool:
        """Saves price data to the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO price_history 
                    (coin_id, price, volume_24h, market_cap, price_change_24h, price_change_percentage_24h)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (coin_id, price, volume_24h, market_cap, price_change_24h, price_change_percentage_24h))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving price data for {coin_id}: {e}")
            return False
    
    def get_price_history(self, coin_id: str, days: int = 30) -> pd.DataFrame:
        """Gets price history for a coin."""
        try:
            with self._get_connection() as conn:
                query = """
                    SELECT * FROM price_history 
                    WHERE coin_id = ? AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp
                """.format(days)
                
                df = pd.read_sql_query(query, conn, params=(coin_id,))
                return df
                
        except Exception as e:
            logger.error(f"Error getting price history for {coin_id}: {e}")
            return pd.DataFrame()
    
    def cleanup_old_price_data(self, days: int = 30) -> int:
        """Removes old price data to keep the database from getting too big."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM price_history 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old price records")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old price data: {e}")
            return 0
    
    # Alert operations
    def save_alert(self, coin_id: str, alert_type: str, threshold: float, 
                   current_price: float, message: str) -> bool:
        """Saves an alert to the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alerts 
                    (coin_id, alert_type, threshold, current_price, message)
                    VALUES (?, ?, ?, ?, ?)
                """, (coin_id, alert_type, threshold, current_price, message))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving alert for {coin_id}: {e}")
            return False
    
    def get_alerts(self, coin_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Gets alerts, optionally filtered by coin."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if coin_id:
                    cursor.execute("""
                        SELECT * FROM alerts WHERE coin_id = ? ORDER BY triggered_at DESC LIMIT ?
                    """, (coin_id, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM alerts ORDER BY triggered_at DESC LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Marks an alert as acknowledged."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE alerts SET acknowledged = 1 WHERE id = ?
                """, (alert_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    # Database maintenance
    def get_database_stats(self) -> Dict[str, Any]:
        """Gets statistics about the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = ['watchlist', 'price_history', 'alerts', 'notifications']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                stats['database_size_bytes'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """Creates a backup of the database."""
        try:
            import shutil
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def vacuum_database(self):
        """Optimizes the database by reclaiming unused space."""
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
                
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")

# Create a global database instance
db_manager = DatabaseManager()

# Helper functions for easy access
def add_to_watchlist(coin_id: str, coin_name: str, **kwargs) -> bool:
    """Adds a coin to the watchlist."""
    return db_manager.add_to_watchlist(coin_id, coin_name, **kwargs)

def remove_from_watchlist(coin_id: str) -> bool:
    """Removes a coin from the watchlist."""
    return db_manager.remove_from_watchlist(coin_id)

def get_watchlist() -> List[Dict[str, Any]]:
    """Gets the current watchlist."""
    return db_manager.get_watchlist()

def save_price_data(coin_id: str, price: float, **kwargs) -> bool:
    """Saves price data to the database."""
    return db_manager.save_price_data(coin_id, price, **kwargs)

def get_price_history(coin_id: str, days: int = 30) -> pd.DataFrame:
    """Gets price history for a coin."""
    return db_manager.get_price_history(coin_id, days)
