from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Input, Button, RichLog
from textual.binding import Binding
from textual import on
from typing import List, Dict, Any

from api.scryfall import ScryfallAPI
from database.db import CardDatabase
from utils.price_checker import PriceChecker


class MTGPriceTracker(App):
    TITLE = "MTG Price Tracker"
    SUB_TITLE = "Track your Magic: The Gathering card prices"
    
    CSS = """
    Screen {
        background: #1a1a1a;
    }
    
    #main-container {
        height: 100%;
        layout: vertical;
    }
    
    #search-container {
        height: auto;
        border: heavy #505050;
        background: #262626;
        padding: 1 2;
    }
    
    #search-label {
        width: auto;
        margin-right: 2;
        color: #e0e0e0;
        text-style: bold;
    }
    
    #search-input {
        width: 1fr;
        margin-right: 2;
        border: solid #606060;
    }
    
    #search-button {
        min-width: 12;
        background: #404040;
        color: #ffffff;
        border: solid #606060;
    }
    
    #content-container {
        height: 1fr;
        layout: horizontal;
        padding: 0 1;
        margin-top: 1;
    }
    
    #watchlist-container {
        width: 1fr;
        height: 100%;
        layout: vertical;
        border: heavy #505050;
        background: #262626;
        padding: 0;
    }
    
    #search-results-container {
        width: 1fr;
        height: 100%;
        layout: vertical;
        border: heavy #505050;
        background: #262626;
        padding: 0;
        margin-left: 1;
    }
    
    .section-title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: #353535;
        color: #e0e0e0;
        border-bottom: heavy #505050;
    }
    
    #watchlist-table {
        height: 1fr;
        background: #1a1a1a;
    }
    
    #search-results-table {
        height: 1fr;
        background: #1a1a1a;
    }
    
    #button-container {
        dock: bottom;
        height: auto;
        background: #262626;
        padding: 1 2;
        border-top: heavy #505050;
        align: center middle;
    }
    
    #add-button {
        width: 60%;
        min-width: 20;
        max-width: 40;
        height: 3;
        background: transparent;
        color: #e0e0e0;
        border: solid #808080;
    }
    
    #add-button:hover {
        background: #353535;
        border: solid #a0a0a0;
    }
    
    #log-container {
        height: 12;
        border: heavy #505050;
        background: #262626;
        padding: 0;
        margin: 1 1 0 1;
    }
    
    #log-title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: #353535;
        color: #e0e0e0;
        border-bottom: heavy #505050;
    }
    
    #price-log {
        height: 1fr;
        background: #1a1a1a;
        border: none;
        padding: 1;
    }
    
    DataTable {
        height: 1fr;
    }
    
    DataTable > .datatable--header {
        background: #404040;
        color: #e0e0e0;
        text-style: bold;
    }
    
    DataTable > .datatable--cursor {
        background: #2d5a5a;
        color: #ffffff;
    }
    
    DataTable:focus > .datatable--cursor {
        background: #3a7070;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", key_display="Q"),
        Binding("r", "refresh_prices", "Refresh Prices", key_display="R"),
        Binding("d", "delete_selected", "Delete Selected", key_display="D"),
    ]
    
    def __init__(self):
        super().__init__()
        self.db = CardDatabase()
        self.api = ScryfallAPI()
        self.price_checker = PriceChecker(self.db, self.api)
        self.search_results: List[Dict[str, Any]] = []
        self.selected_watchlist_card: str | None = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal(id="search-container"):
                yield Static("Search Cards:", id="search-label")
                yield Input(placeholder="Enter card name (e.g., 'Hullbreacher', 'Teferi')...", id="search-input")
                yield Button("Search", id="search-button", variant="primary")
            
            with Horizontal(id="content-container"):
                with Container(id="watchlist-container"):
                    yield Static("Watchlist", classes="section-title")
                    watchlist_table = DataTable(id="watchlist-table")
                    watchlist_table.cursor_type = "row"
                    yield watchlist_table
                
                with Container(id="search-results-container"):
                    yield Static("Search Results", classes="section-title")
                    search_table = DataTable(id="search-results-table")
                    search_table.cursor_type = "row"
                    yield search_table
                    with Horizontal(id="button-container"):
                        yield Button("Add to Watchlist", id="add-button", variant="default")
            
            with Container(id="log-container"):
                yield Static("Price Change Log", id="log-title")
                yield RichLog(id="price-log", wrap=True, highlight=True, markup=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        watchlist_table = self.query_one("#watchlist-table", DataTable)
        watchlist_table.add_columns("Card Name", "Set", "Price", "Last Updated")
        watchlist_table.zebra_stripes = True
        watchlist_table.show_cursor = True
        
        search_table = self.query_one("#search-results-table", DataTable)
        search_table.add_columns("Card Name", "Set", "Price")
        search_table.zebra_stripes = True
        search_table.show_cursor = True
        
        self.load_watchlist()
        self.check_prices_on_startup()
    
    def load_watchlist(self):
        watchlist_table = self.query_one("#watchlist-table", DataTable)
        watchlist_table.clear()
        
        watchlist = self.db.get_watchlist()
        for card in watchlist:
            price_str = f"${card['current_price']:.2f}" if card['current_price'] else "N/A"
            if card.get('price_type'):
                price_str += f" ({card['price_type']})"
            
            last_updated = card.get('last_updated', 'N/A')
            if last_updated and last_updated != 'N/A':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_updated)
                    last_updated = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            watchlist_table.add_row(
                card['card_name'],
                card.get('set_name', 'N/A'),
                price_str,
                last_updated
            )
    
    def check_prices_on_startup(self):
        log = self.query_one("#price-log", RichLog)
        log.write("[bold]═══ Price Check Started ═══[/]")
        log.write("Fetching latest prices from Scryfall API...")
        
        last_check = self.db.get_last_check_time()
        results = self.price_checker.check_and_update_prices()
        
        message = self.price_checker.format_price_changes(results, last_check)
        log.write("")
        log.write(message)
        log.write("")
        log.write(f"[bold]✓[/] Checked {results['checked']} cards | Updated {results['updated']} prices")
        log.write("[bold]═══════════════════════════[/]")
        
        self.load_watchlist()
    
    @on(Button.Pressed, "#search-button")
    async def search_cards(self):
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()
        
        if not query:
            return
        
        log = self.query_one("#price-log", RichLog)
        log.write(f"[bold]→[/] Searching for: {query}")
        
        results = self.api.search_cards(query, max_results=10)
        self.search_results = results
        
        search_table = self.query_one("#search-results-table", DataTable)
        search_table.clear()
        
        for card in results:
            price_str = f"${card['price']:.2f}" if card['price'] else "N/A"
            if card.get('price_type'):
                price_str += f" ({card['price_type']})"
            
            search_table.add_row(
                card['name'],
                card.get('set', 'N/A'),
                price_str
            )
        
        log.write(f"[bold]✓[/] Found {len(results)} card(s)")
        
        if results:
            search_table.focus()
    
    @on(Input.Submitted, "#search-input")
    async def search_on_enter(self):
        await self.search_cards()
    
    @on(Button.Pressed, "#add-button")
    def add_to_watchlist(self):
        search_table = self.query_one("#search-results-table", DataTable)
        log = self.query_one("#price-log", RichLog)
        
        if not self.search_results:
            log.write("[bold]✗[/] No search results available")
            return
        
        if search_table.cursor_row is None or search_table.cursor_row < 0:
            log.write("[bold]✗[/] No card selected in search results")
            return
        
        idx = search_table.cursor_row
        if idx >= len(self.search_results):
            return
        
        card = self.search_results[idx]
        
        if self.db.add_to_watchlist(card):
            log.write(f"[bold]✓[/] Added '{card['name']}' to watchlist")
            self.load_watchlist()
        else:
            log.write(f"[bold]⚠[/] '{card['name']}' is already in watchlist")
    
    def action_refresh_prices(self):
        log = self.query_one("#price-log", RichLog)
        log.write("[bold]═══ Manual Price Refresh ═══[/]")
        log.write("Fetching latest prices from Scryfall API...")
        
        last_check = self.db.get_last_check_time()
        results = self.price_checker.check_and_update_prices()
        
        message = self.price_checker.format_price_changes(results, last_check)
        log.write("")
        log.write(message)
        log.write("")
        log.write(f"[bold]✓[/] Refreshed {results['updated']} price(s)")
        log.write("[bold]════════════════════════════[/]")
        
        self.load_watchlist()
    
    def action_delete_selected(self):
        watchlist_table = self.query_one("#watchlist-table", DataTable)
        log = self.query_one("#price-log", RichLog)
        
        if watchlist_table.cursor_row is None or watchlist_table.cursor_row < 0:
            log.write("[bold]✗[/] No card selected in watchlist")
            return
        
        row_key = watchlist_table.get_row_at(watchlist_table.cursor_row)
        card_name = row_key[0]
        
        if self.db.remove_from_watchlist(card_name):
            log.write(f"[bold]✓[/] Removed '{card_name}' from watchlist")
            self.load_watchlist()
    
    def on_unmount(self):
        self.api.close()
        self.db.close()


def run_app():
    app = MTGPriceTracker()
    app.run()

