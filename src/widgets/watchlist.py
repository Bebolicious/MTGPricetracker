"""Watchlist widget for displaying tracked cards."""

from textual.app import ComposeResult
from textual.widgets import DataTable, Static
from textual.containers import Container
from typing import List, Dict


class WatchlistWidget(Container):
    """Widget displaying the watchlist of MTG cards."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("📋 Watchlist", classes="section-title")
        yield DataTable(id="watchlist-table")

    def on_mount(self) -> None:
        """Configure the table when mounted."""
        table = self.query_one("#watchlist-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Add columns
        table.add_column("Card Name", key="name")
        table.add_column("Set", key="set")
        table.add_column("Price (USD)", key="price")
        table.add_column("Last Updated", key="updated")

    def update_watchlist(self, cards: List[Dict]) -> None:
        """Update the watchlist table with card data."""
        table = self.query_one("#watchlist-table", DataTable)
        table.clear()
        
        for card in cards:
            price_str = f"${card['current_price']:.2f}" if card['current_price'] else "N/A"
            
            # Format timestamp to be more readable
            updated = card.get('last_updated', '')
            if updated and 'T' in updated:
                updated = updated.split('T')[0]  # Just show date
            
            table.add_row(
                card['card_name'],
                card.get('scryfall_id', 'N/A')[:8] + "...",  # Shortened ID as placeholder
                price_str,
                updated,
                key=card['card_name']
            )

    def get_selected_card(self) -> str | None:
        """Get the currently selected card name."""
        table = self.query_one("#watchlist-table", DataTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            return str(row_key)
        return None

