"""Database operations for storing watchlist and price history."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class CardDatabase:
    """SQLite database manager for card watchlist and price history."""
    
    def __init__(self, db_path: str = "data/cards.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Watchlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL UNIQUE,
                scryfall_id TEXT,
                set_name TEXT,
                set_code TEXT,
                collector_number TEXT,
                current_price REAL,
                price_type TEXT,
                last_updated TIMESTAMP,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                price REAL NOT NULL,
                price_type TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_name) REFERENCES watchlist(card_name)
            )
        """)
        
        # App metadata table (for tracking last check time)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def add_to_watchlist(self, card_data: Dict[str, Any]) -> bool:
        """
        Add a card to the watchlist.
        
        Args:
            card_data: Dictionary containing card information
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO watchlist 
                (card_name, scryfall_id, set_name, set_code, collector_number, 
                 current_price, price_type, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card_data["name"],
                card_data.get("id"),
                card_data.get("set"),
                card_data.get("set_code"),
                card_data.get("collector_number"),
                card_data.get("price"),
                card_data.get("price_type"),
                now
            ))
            
            # Add initial price to history
            if card_data.get("price") is not None:
                cursor.execute("""
                    INSERT INTO price_history (card_name, price, price_type)
                    VALUES (?, ?, ?)
                """, (card_data["name"], card_data["price"], card_data.get("price_type")))
            
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Card already exists in watchlist
            return False
        except Exception as e:
            print(f"Error adding card to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, card_name: str) -> bool:
        """Remove a card from the watchlist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE card_name = ?", (card_name,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing card from watchlist: {e}")
            return False
    
    def get_watchlist(self) -> List[Dict[str, Any]]:
        """Get all cards in the watchlist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT card_name, set_name, set_code, current_price, price_type, 
                   last_updated, added_date
            FROM watchlist
            ORDER BY card_name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_card_price(self, card_name: str, new_price: float, 
                         price_type: str) -> bool:
        """
        Update a card's price in the watchlist and add to history.
        
        Args:
            card_name: Name of the card
            new_price: New price value
            price_type: Type of price (e.g., "USD", "EUR")
            
        Returns:
            True if updated successfully
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            # Update watchlist
            cursor.execute("""
                UPDATE watchlist 
                SET current_price = ?, price_type = ?, last_updated = ?
                WHERE card_name = ?
            """, (new_price, price_type, now, card_name))
            
            # Add to price history
            cursor.execute("""
                INSERT INTO price_history (card_name, price, price_type)
                VALUES (?, ?, ?)
            """, (card_name, new_price, price_type))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating card price: {e}")
            return False
    
    def get_price_changes_since(self, since_time: str) -> List[Dict[str, Any]]:
        """
        Get cards whose prices have changed since a given time.
        
        Args:
            since_time: ISO format timestamp
            
        Returns:
            List of cards with price changes
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT ph.card_name, w.current_price, w.price_type
            FROM price_history ph
            JOIN watchlist w ON ph.card_name = w.card_name
            WHERE ph.recorded_at > ?
            ORDER BY ph.card_name
        """, (since_time,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_last_check_time(self) -> Optional[str]:
        """Get the last time prices were checked."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT value FROM app_metadata WHERE key = 'last_price_check'
        """)
        
        row = cursor.fetchone()
        return row["value"] if row else None
    
    def update_last_check_time(self):
        """Update the last price check time to now."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO app_metadata (key, value, updated_at)
            VALUES ('last_price_check', ?, ?)
        """, (now, now))
        
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

