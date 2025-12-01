"""Price checking and comparison utilities."""
from typing import List, Dict, Any
from datetime import datetime


class PriceChecker:
    """Handles price checking and change detection."""
    
    def __init__(self, db, api):
        """
        Initialize price checker.
        
        Args:
            db: CardDatabase instance
            api: ScryfallAPI instance
        """
        self.db = db
        self.api = api
    
    def check_and_update_prices(self) -> Dict[str, Any]:
        """
        Check current prices for all watchlist cards and update database.
        
        Returns:
            Dictionary with check results including changed cards
        """
        watchlist = self.db.get_watchlist()
        
        if not watchlist:
            return {
                "checked": 0,
                "updated": 0,
                "changed": [],
                "errors": []
            }
        
        # Get last check time before updating
        last_check = self.db.get_last_check_time()
        
        card_names = [card["card_name"] for card in watchlist]
        updated_cards = self.api.get_cards_by_names(card_names)
        
        results = {
            "checked": len(card_names),
            "updated": 0,
            "changed": [],
            "errors": []
        }
        
        for card in updated_cards:
            if card.get("price") is None:
                continue
            
            card_name = card["name"]
            new_price = card["price"]
            price_type = card.get("price_type", "USD")
            
            # Find old price
            old_card = next((c for c in watchlist if c["card_name"] == card_name), None)
            old_price = old_card.get("current_price") if old_card else None
            
            # Update price in database
            if self.db.update_card_price(card_name, new_price, price_type):
                results["updated"] += 1
                
                # Check if price changed
                if old_price is not None and abs(new_price - old_price) > 0.01:
                    change_pct = ((new_price - old_price) / old_price) * 100
                    results["changed"].append({
                        "name": card_name,
                        "old_price": old_price,
                        "new_price": new_price,
                        "change": new_price - old_price,
                        "change_pct": change_pct,
                        "price_type": price_type
                    })
        
        # Update last check time
        self.db.update_last_check_time()
        
        return results
    
    def format_price_changes(self, results: Dict[str, Any], 
                            last_check: str = None) -> str:
        """
        Format price change results into a readable message.
        
        Args:
            results: Results from check_and_update_prices()
            last_check: ISO timestamp of last check
            
        Returns:
            Formatted string message
        """
        if not results["changed"]:
            return "[dim]No price changes detected[/]"
        
        lines = []
        
        if last_check:
            try:
                last_dt = datetime.fromisoformat(last_check)
                time_str = last_dt.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[bold]Price changes since {time_str}:[/]")
            except:
                lines.append("[bold]Price changes:[/]")
        else:
            lines.append("[bold]Price changes:[/]")
        
        lines.append("")
        
        for change in results["changed"]:
            if change["change"] > 0:
                direction = "↑"
            else:
                direction = "↓"
            
            price_type = change.get("price_type", "USD")
            
            lines.append(
                f"  {direction} {change['name']}: "
                f"${change['old_price']:.2f} → ${change['new_price']:.2f} "
                f"({change['change_pct']:+.1f}%) [{price_type}]"
            )
        
        return "\n".join(lines)

