#!/usr/bin/env python3
"""Demo script to showcase the MTG Price Tracker UI."""
import sys
sys.path.insert(0, "/home/alex/Documents/personal/mtgpricer_v2")

from ui.app import run_app

if __name__ == "__main__":
    print("Starting MTG Price Tracker...")
    print("=" * 50)
    print("Controls:")
    print("  • Search: Type a card name and press Enter")
    print("  • Add: Select a card from search and click 'Add to Watchlist'")
    print("  • Delete: Select a card in watchlist and press 'D'")
    print("  • Refresh: Press 'R' to refresh all prices")
    print("  • Quit: Press 'Q' to exit")
    print("=" * 50)
    print()
    
    run_app()

