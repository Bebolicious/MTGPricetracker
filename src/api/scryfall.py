"""Scryfall API integration for fetching MTG card data."""

import httpx
from typing import List, Optional, Dict


class ScryfallAPI:
    """Client for interacting with the Scryfall API."""

    BASE_URL = "https://api.scryfall.com"

    def __init__(self):
        """Initialize the Scryfall API client."""
        self.client = httpx.Client(timeout=10.0)

    async def search_cards_async(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for cards asynchronously (for use with async context).
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of card dictionaries with name, id, and price info
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/cards/search",
                    params={"q": query, "unique": "prints"}
                )
                response.raise_for_status()
                data = response.json()
                
                cards = []
                for card in data.get("data", [])[:max_results]:
                    cards.append(self._parse_card(card))
                
                return cards
            except httpx.HTTPError as e:
                print(f"Error searching cards: {e}")
                return []

    def search_cards(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for cards synchronously.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of card dictionaries with name, id, and price info
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/cards/search",
                params={"q": query, "unique": "prints"}
            )
            response.raise_for_status()
            data = response.json()
            
            cards = []
            for card in data.get("data", [])[:max_results]:
                cards.append(self._parse_card(card))
            
            return cards
        except httpx.HTTPError as e:
            print(f"Error searching cards: {e}")
            return []

    def get_card_by_name(self, card_name: str) -> Optional[Dict]:
        """
        Get exact card by name.
        
        Args:
            card_name: Exact card name
            
        Returns:
            Card dictionary or None if not found
        """
        try:
            response = self.client.get(
                f"{self.BASE_URL}/cards/named",
                params={"exact": card_name}
            )
            response.raise_for_status()
            card_data = response.json()
            return self._parse_card(card_data)
        except httpx.HTTPError:
            return None

    def get_card_by_id(self, scryfall_id: str) -> Optional[Dict]:
        """
        Get card by Scryfall ID.
        
        Args:
            scryfall_id: Scryfall UUID
            
        Returns:
            Card dictionary or None if not found
        """
        try:
            response = self.client.get(f"{self.BASE_URL}/cards/{scryfall_id}")
            response.raise_for_status()
            card_data = response.json()
            return self._parse_card(card_data)
        except httpx.HTTPError:
            return None

    def _parse_card(self, card_data: Dict) -> Dict:
        """
        Parse card data from Scryfall API response.
        
        Args:
            card_data: Raw card data from Scryfall
            
        Returns:
            Parsed card dictionary with essential info
        """
        prices = card_data.get("prices", {})
        
        # Prefer USD price, fallback to EUR, then USD foil
        price = None
        if prices.get("usd"):
            price = float(prices["usd"])
        elif prices.get("eur"):
            price = float(prices["eur"])
        elif prices.get("usd_foil"):
            price = float(prices["usd_foil"])
        
        return {
            "name": card_data.get("name"),
            "scryfall_id": card_data.get("id"),
            "set": card_data.get("set_name"),
            "set_code": card_data.get("set"),
            "price": price,
            "image_uri": card_data.get("image_uris", {}).get("small"),
            "type_line": card_data.get("type_line"),
            "rarity": card_data.get("rarity"),
        }

    def close(self):
        """Close the HTTP client."""
        self.client.close()

