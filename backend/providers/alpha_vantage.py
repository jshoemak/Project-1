"""Alpha Vantage provider stub — activated when API key is saved in config."""
import logging
from typing import Optional

import httpx

from .base import StockDataProvider

logger = logging.getLogger(__name__)
BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageProvider(StockDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, params: dict) -> dict:
        params["apikey"] = self.api_key
        with httpx.Client(timeout=20) as client:
            r = client.get(BASE_URL, params=params)
            r.raise_for_status()
            return r.json()

    def get_price(self, ticker: str) -> Optional[float]:
        try:
            data = self._get({"function": "GLOBAL_QUOTE", "symbol": ticker})
            return float(data["Global Quote"]["05. price"])
        except Exception as e:
            logger.warning("AlphaVantage get_price failed for %s: %s", ticker, e)
            return None

    def get_history(self, ticker: str, days: int = 90) -> list[dict]:
        try:
            size = "compact" if days <= 100 else "full"
            data = self._get({"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": ticker, "outputsize": size})
            series = data.get("Time Series (Daily)", {})
            results = []
            for date_str in sorted(series.keys())[-days:]:
                bar = series[date_str]
                results.append({
                    "date": date_str,
                    "close": round(float(bar["5. adjusted close"]), 2),
                    "open": round(float(bar["1. open"]), 2),
                    "high": round(float(bar["2. high"]), 2),
                    "low": round(float(bar["3. low"]), 2),
                    "volume": int(bar["6. volume"]),
                })
            return results
        except Exception as e:
            logger.warning("AlphaVantage get_history failed for %s: %s", ticker, e)
            return []

    def get_fundamentals(self, ticker: str) -> dict:
        try:
            data = self._get({"function": "OVERVIEW", "symbol": ticker})
            return {
                "market_cap": int(data.get("MarketCapitalization", 0)) or None,
                "pe_ratio": float(data.get("PERatio", 0)) or None,
                "week52_high": float(data.get("52WeekHigh", 0)) or None,
                "week52_low": float(data.get("52WeekLow", 0)) or None,
                "next_earnings": data.get("NextEarningsDate"),
                "sector": data.get("Sector", "Unknown"),
                "description": data.get("Description", ""),
                "provider": "Alpha Vantage",
            }
        except Exception as e:
            logger.warning("AlphaVantage get_fundamentals failed for %s: %s", ticker, e)
            return {"provider": "Alpha Vantage", "error": str(e)}
