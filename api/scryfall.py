"""Scryfall API integration for fetching MTG card data."""
import httpx
from typing import Optional, List, Dict, Any


class ScryfallAPI:
    """Interface for Scryfall API operations."""
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self):
        self.client = httpx.Client(timeout=10.0)
    
    def search_cards(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for cards by name.
        
        Args:
            query: The search query (card name)
            max_results: Maximum number of results to return
            
        Returns:
            List of card dictionaries with relevant data
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/cards/search",
                params={"q": query, "order": "name"}
            )
            response.raise_for_status()
            data = response.json()
            
            cards = []
            for card in data.get("data", [])[:max_results]:
                cards.append(self._extract_card_data(card))
            
            return cards
        except httpx.HTTPError as e:
            print(f"Error searching cards: {e}")
            return []
    
    def get_card_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific card by exact or fuzzy name match.
        
        Args:
            name: The card name
            
        Returns:
            Card dictionary or None if not found
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/cards/named",
                params={"fuzzy": name}
            )
            response.raise_for_status()
            card_data = response.json()
            return self._extract_card_data(card_data)
        except httpx.HTTPError as e:
            print(f"Error fetching card '{name}': {e}")
            return None
    
    def get_cards_by_names(self, names: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple cards by name.
        
        Args:
            names: List of card names
            
        Returns:
            List of card dictionaries
        """
        cards = []
        for name in names:
            card = self.get_card_by_name(name)
            if card:
                cards.append(card)
        return cards
    
    def _extract_card_data(self, card_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant card data from Scryfall response.
        
        Args:
            card_raw: Raw card data from Scryfall
            
        Returns:
            Simplified card dictionary
        """
        prices = card_raw.get("prices", {})
        
        # Prefer USD price, fallback to USD foil, then EUR
        price = None
        price_type = None
        
        if prices.get("usd"):
            price = float(prices["usd"])
            price_type = "USD"
        elif prices.get("usd_foil"):
            price = float(prices["usd_foil"])
            price_type = "USD (Foil)"
        elif prices.get("eur"):
            price = float(prices["eur"])
            price_type = "EUR"
        
        return {
            "id": card_raw.get("id"),
            "name": card_raw.get("name"),
            "set": card_raw.get("set_name"),
            "set_code": card_raw.get("set"),
            "collector_number": card_raw.get("collector_number"),
            "price": price,
            "price_type": price_type,
            "scryfall_uri": card_raw.get("scryfall_uri"),
        }
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()

