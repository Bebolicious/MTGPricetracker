"""Search widget for finding MTG cards."""

from textual.app import ComposeResult
from textual.widgets import Input, DataTable, Static, Button
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message
from typing import List, Dict


class SearchWidget(Container):
    """Widget for searching MTG cards."""

    class CardSelected(Message):
        """Message sent when a card is selected to add to watchlist."""

        def __init__(self, card: Dict) -> None:
            self.card = card
            super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical():
            yield Static("🔍 Search Cards", classes="section-title")
            with Horizontal(classes="search-bar"):
                yield Input(placeholder="Search for cards...", id="search-input")
                yield Button("Search", id="search-button", variant="primary")
            yield DataTable(id="search-results")

    def on_mount(self) -> None:
        """Configure the table when mounted."""
        table = self.query_one("#search-results", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Add columns
        table.add_column("Card Name", key="name")
        table.add_column("Set", key="set")
        table.add_column("Type", key="type")
        table.add_column("Price (USD)", key="price")
        table.add_column("Action", key="action")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-button":
            await self.perform_search()
        elif event.button.id and event.button.id.startswith("add-"):
            # Extract card index from button id
            card_idx = int(event.button.id.split("-")[1])
            if hasattr(self, "_search_results") and card_idx < len(self._search_results):
                card = self._search_results[card_idx]
                self.post_message(self.CardSelected(card))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search input."""
        if event.input.id == "search-input":
            await self.perform_search()

    async def perform_search(self) -> None:
        """Perform the search (to be called by parent app)."""
        # This will be handled by the main app
        pass

    def display_results(self, cards: List[Dict]) -> None:
        """Display search results in the table."""
        table = self.query_one("#search-results", DataTable)
        table.clear()
        
        # Store results for add button functionality
        self._search_results = cards
        
        for idx, card in enumerate(cards):
            price_str = f"${card['price']:.2f}" if card['price'] is not None else "N/A"
            type_line = card.get('type_line', 'N/A')
            
            # Truncate long type lines
            if len(type_line) > 30:
                type_line = type_line[:27] + "..."
            
            table.add_row(
                card['name'],
                card.get('set', 'N/A'),
                type_line,
                price_str,
                f"[Add {idx}]",  # Placeholder for add action
                key=f"card_{idx}"
            )

    def get_search_query(self) -> str:
        """Get the current search query."""
        search_input = self.query_one("#search-input", Input)
        return search_input.value.strip()

    def clear_search(self) -> None:
        """Clear search input and results."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        table = self.query_one("#search-results", DataTable)
        table.clear()

