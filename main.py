"""
MTG Price Tracker - A TUI application for tracking Magic: The Gathering card prices.

This application allows you to:
- Search for MTG cards using the Scryfall API
- Add cards to a watchlist
- Track price changes over time
- View price history and changes since last app start
"""
from ui.app import run_app


if __name__ == "__main__":
    run_app()
