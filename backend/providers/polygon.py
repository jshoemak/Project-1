"""Polygon.io provider stub — activated when API key is saved in config."""
import logging
from typing import Optional

import httpx

from .base import StockDataProvider

logger = logging.getLogger(__name__)
BASE_URL = "https://api.polygon.io"


class PolygonProvider(StockDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, path: str, params: dict = None) -> dict:
        params = params or {}
        params["apiKey"] = self.api_key
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{BASE_URL}{path}", params=params)
            r.raise_for_status()
            return r.json()

    def get_price(self, ticker: str) -> Optional[float]:
        try:
            data = self._get(f"/v2/last/trade/{ticker}")
            return float(data["results"]["p"])
        except Exception as e:
            logger.warning("Polygon get_price failed for %s: %s", ticker, e)
            return None

    def get_history(self, ticker: str, days: int = 90) -> list[dict]:
        try:
            from datetime import datetime, timedelta
            end = datetime.now()
            start = end - timedelta(days=days)
            data = self._get(
                f"/v2/aggs/ticker/{ticker}/range/1/day/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}",
                {"adjusted": "true", "sort": "asc", "limit": 365},
            )
            results = []
            for bar in data.get("results", []):
                from datetime import timezone
                dt = datetime.fromtimestamp(bar["t"] / 1000, tz=timezone.utc)
                results.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "close": round(bar["c"], 2),
                    "open": round(bar["o"], 2),
                    "high": round(bar["h"], 2),
                    "low": round(bar["l"], 2),
                    "volume": int(bar["v"]),
                })
            return results
        except Exception as e:
            logger.warning("Polygon get_history failed for %s: %s", ticker, e)
            return []

    def get_fundamentals(self, ticker: str) -> dict:
        try:
            data = self._get(f"/v3/reference/tickers/{ticker}")
            r = data.get("results", {})
            return {
                "market_cap": r.get("market_cap"),
                "pe_ratio": None,
                "week52_high": r.get("share_class_shares_outstanding"),
                "week52_low": None,
                "next_earnings": None,
                "sector": r.get("sic_description", "Unknown"),
                "description": r.get("description", ""),
                "provider": "Polygon.io",
            }
        except Exception as e:
            logger.warning("Polygon get_fundamentals failed for %s: %s", ticker, e)
            return {"provider": "Polygon.io", "error": str(e)}
