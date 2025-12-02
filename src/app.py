"""Main Textual application for MTG price tracking."""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button
from textual.binding import Binding

from src.database import Database
from src.api import ScryfallAPI
from src.widgets import WatchlistWidget, SearchWidget


class MTGPricerApp(App):
    """A Textual app for tracking MTG card prices."""

    CSS = """
    Screen {
        background: $surface;
    }

    .section-title {
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
        text-align: center;
        text-style: bold;
    }

    #main-container {
        height: 100%;
        padding: 1;
    }

    #watchlist-container {
        height: 50%;
        border: solid $primary;
        margin-bottom: 1;
    }

    #search-container {
        height: 70%;
        border: solid $accent;
    }

    DataTable {
        height: 100%;
    }

    .search-bar {
        height: auto;
        margin-bottom: 1;
    }

    #search-input {
        width: 4fr;
    }

    #search-button {
        width: 1fr;
        min-width: 10;
    }

    #log-container {
        height: auto;
        background: $panel;
        padding: 1;
        margin-bottom: 1;
        border: solid $warning;
    }

    #action-bar {
        height: auto;
        padding: 1;
        background: $panel;
    }

    .action-button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh Prices"),
        Binding("d", "delete", "Delete Selected"),
        Binding("a", "add_from_search", "Add Selected Search Result"),
    ]

    def __init__(self):
        """Initialize the app."""
        super().__init__()
        self.db = Database()
        self.api = ScryfallAPI()
        self.price_changes = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical(id="main-container"):
            yield Static("", id="log-container")
            with Container(id="watchlist-container"):
                yield WatchlistWidget()
            with Container(id="search-container"):
                yield SearchWidget()
            with Horizontal(id="action-bar"):
                yield Button("Refresh Prices", id="btn-refresh", variant="success", classes="action-button")
                yield Button("Delete Selected", id="btn-delete", variant="error", classes="action-button")
                yield Button("Clear Search", id="btn-clear", variant="default", classes="action-button")
        yield Footer()

    async def on_mount(self) -> None:
        """Handle app startup."""
        self.title = "MTG Price Tracker"
        self.sub_title = "Track your Magic: The Gathering card prices"
        
        # Load watchlist
        await self.load_watchlist()
        
        # Check prices on startup
        await self.check_prices()

    async def load_watchlist(self) -> None:
        """Load and display the watchlist."""
        cards = self.db.get_watchlist()
        watchlist = self.query_one(WatchlistWidget)
        watchlist.update_watchlist(cards)

    async def check_prices(self) -> None:
        """Check prices for all cards in watchlist and log changes."""
        last_check = self.db.get_last_check()
        cards = self.db.get_watchlist()
        
        self.price_changes = []
        
        for card in cards:
            # Get current price from Scryfall
            card_data = self.api.get_card_by_id(card['scryfall_id'])
            
            if card_data and card_data['price'] is not None:
                new_price = card_data['price']
                success, old_price = self.db.update_price(card['card_name'], new_price)
                
                if success and old_price is not None:
                    price_diff = new_price - old_price
                    if abs(price_diff) > 0.01:  # Only log if difference > 1 cent
                        self.price_changes.append({
                            'name': card['card_name'],
                            'old': old_price,
                            'new': new_price,
                            'diff': price_diff
                        })
        
        # Update last check timestamp
        now = datetime.now().isoformat()
        self.db.set_last_check(now)
        
        # Display log message
        self.update_log_message(last_check)
        
        # Refresh watchlist display
        await self.load_watchlist()

    def update_log_message(self, last_check: str | None) -> None:
        """Update the log message with price changes."""
        log = self.query_one("#log-container", Static)
        
        if not last_check:
            log.update("📊 First run - prices recorded!")
            return
        
        # Format last check time
        if 'T' in last_check:
            last_check_date = last_check.split('T')[0]
            last_check_time = last_check.split('T')[1].split('.')[0]
            last_check_str = f"{last_check_date} {last_check_time}"
        else:
            last_check_str = last_check
        
        if not self.price_changes:
            log.update(f"✅ Since {last_check_str}: No price changes detected")
        else:
            changes_text = f"📈 Since {last_check_str}, prices changed for:\n"
            for change in self.price_changes:
                direction = "📈" if change['diff'] > 0 else "📉"
                changes_text += f"  {direction} {change['name']}: ${change['old']:.2f} → ${change['new']:.2f} "
                changes_text += f"({change['diff']:+.2f})\n"
            log.update(changes_text.strip())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "btn-refresh":
            await self.action_refresh()
        elif event.button.id == "btn-delete":
            await self.action_delete()
        elif event.button.id == "btn-clear":
            search = self.query_one(SearchWidget)
            search.clear_search()

    async def on_search_widget_card_selected(self, message: SearchWidget.CardSelected) -> None:
        """Handle card selection from search results."""
        card = message.card
        
        if card['price'] is None:
            self.notify("⚠️  Card has no price data", severity="warning")
            return
        
        success = self.db.add_card(
            card['name'],
            card['scryfall_id'],
            card['price']
        )
        
        if success:
            self.notify(f"✅ Added {card['name']} to watchlist", severity="information")
            await self.load_watchlist()
        else:
            self.notify(f"⚠️  {card['name']} is already in watchlist", severity="warning")

    async def on_input_submitted(self, event) -> None:
        """Handle search input submission."""
        search = self.query_one(SearchWidget)
        query = search.get_search_query()
        
        if query:
            self.notify(f"🔍 Searching for '{query}'...")
            cards = self.api.search_cards(query, max_results=10)
            
            if cards:
                search.display_results(cards)
                self.notify(f"✅ Found {len(cards)} cards", severity="information")
            else:
                search.display_results([])
                self.notify("❌ No cards found", severity="warning")

    async def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in search results to add card."""
        # Check if it's the search results table
        if event.data_table.id == "search-results":
            search = self.query_one(SearchWidget)
            if hasattr(search, "_search_results"):
                # Get the row index
                row_key = event.row_key
                if isinstance(row_key, str) and row_key.startswith("card_"):
                    idx = int(row_key.split("_")[1])
                    if idx < len(search._search_results):
                        card = search._search_results[idx]
                        await self.on_search_widget_card_selected(
                            SearchWidget.CardSelected(card)
                        )

    async def action_refresh(self) -> None:
        """Refresh prices for all cards."""
        self.notify("🔄 Refreshing prices...")
        await self.check_prices()
        self.notify("✅ Prices refreshed!", severity="information")

    async def action_delete(self) -> None:
        """Delete selected card from watchlist."""
        watchlist = self.query_one(WatchlistWidget)
        selected = watchlist.get_selected_card()
        
        if selected:
            success = self.db.remove_card(selected)
            if success:
                self.notify(f"🗑️  Removed {selected} from watchlist", severity="warning")
                await self.load_watchlist()
            else:
                self.notify("❌ Failed to remove card", severity="error")
        else:
            self.notify("⚠️  No card selected", severity="warning")

    async def action_add_from_search(self) -> None:
        """Add selected search result to watchlist."""
        search = self.query_one(SearchWidget)
        table = search.query_one("#search-results")
        
        if table.cursor_row >= 0 and hasattr(search, "_search_results"):
            idx = table.cursor_row
            if idx < len(search._search_results):
                card = search._search_results[idx]
                await self.on_search_widget_card_selected(
                    SearchWidget.CardSelected(card)
                )

    def on_unmount(self) -> None:
        """Clean up when app closes."""
        self.db.close()
        self.api.close()

