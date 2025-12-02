"""Database module for storing watchlist and price history."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class Database:
    """SQLite database handler for MTG card tracking."""

    def __init__(self, db_path: str = "data/mtgpricer.db"):
        """Initialize database connection and create tables if needed."""
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables."""
        # Watchlist table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL UNIQUE,
                scryfall_id TEXT,
                current_price REAL,
                last_updated TEXT,
                added_at TEXT NOT NULL
            )
        """)
        
        # Price history table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                price REAL NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (card_name) REFERENCES watchlist(card_name)
            )
        """)
        
        # App metadata table (for last check timestamp)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        self.conn.commit()

    def add_card(self, card_name: str, scryfall_id: str, price: float) -> bool:
        """Add a card to the watchlist."""
        try:
            now = datetime.now().isoformat()
            self.cursor.execute("""
                INSERT INTO watchlist (card_name, scryfall_id, current_price, last_updated, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (card_name, scryfall_id, price, now, now))
            
            # Add to price history
            self.cursor.execute("""
                INSERT INTO price_history (card_name, price, recorded_at)
                VALUES (?, ?, ?)
            """, (card_name, price, now))
            
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Card already exists
            return False

    def remove_card(self, card_name: str) -> bool:
        """Remove a card from the watchlist."""
        self.cursor.execute("DELETE FROM watchlist WHERE card_name = ?", (card_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_watchlist(self) -> List[dict]:
        """Get all cards in the watchlist."""
        self.cursor.execute("""
            SELECT card_name, scryfall_id, current_price, last_updated, added_at
            FROM watchlist
            ORDER BY added_at DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_price(self, card_name: str, new_price: float) -> Tuple[bool, Optional[float]]:
        """
        Update the price for a card.
        
        Returns:
            Tuple of (success, old_price)
        """
        # Get old price
        self.cursor.execute("SELECT current_price FROM watchlist WHERE card_name = ?", (card_name,))
        row = self.cursor.fetchone()
        
        if not row:
            return False, None
        
        old_price = row["current_price"]
        now = datetime.now().isoformat()
        
        # Update current price
        self.cursor.execute("""
            UPDATE watchlist
            SET current_price = ?, last_updated = ?
            WHERE card_name = ?
        """, (new_price, now, card_name))
        
        # Add to price history
        self.cursor.execute("""
            INSERT INTO price_history (card_name, price, recorded_at)
            VALUES (?, ?, ?)
        """, (card_name, new_price, now))
        
        self.conn.commit()
        return True, old_price

    def get_last_check(self) -> Optional[str]:
        """Get the timestamp of the last price check."""
        self.cursor.execute("SELECT value FROM app_metadata WHERE key = 'last_check'")
        row = self.cursor.fetchone()
        return row["value"] if row else None

    def set_last_check(self, timestamp: str):
        """Set the timestamp of the last price check."""
        self.cursor.execute("""
            INSERT OR REPLACE INTO app_metadata (key, value)
            VALUES ('last_check', ?)
        """, (timestamp,))
        self.conn.commit()

    def get_price_history(self, card_name: str, limit: int = 10) -> List[dict]:
        """Get price history for a specific card."""
        self.cursor.execute("""
            SELECT price, recorded_at
            FROM price_history
            WHERE card_name = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        """, (card_name, limit))
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        self.conn.close()

