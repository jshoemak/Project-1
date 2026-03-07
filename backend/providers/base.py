"""Abstract base class for stock data providers."""
from abc import ABC, abstractmethod
from typing import Optional


class StockDataProvider(ABC):
    """All providers must implement these three methods."""

    @abstractmethod
    def get_price(self, ticker: str) -> Optional[float]:
        """Return the latest price for a ticker, or None on failure."""

    @abstractmethod
    def get_history(self, ticker: str, days: int = 90) -> list[dict]:
        """Return a list of {date: str, close: float} dicts, oldest-first."""

    @abstractmethod
    def get_fundamentals(self, ticker: str) -> dict:
        """Return a dict with keys: market_cap, pe_ratio, week52_high,
        week52_low, next_earnings, sector, description."""
