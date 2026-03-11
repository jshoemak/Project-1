"""Yahoo Finance provider via yfinance (free, default)."""
import logging
from datetime import datetime, timedelta
from typing import Optional

import yfinance as yf

from .base import StockDataProvider

logger = logging.getLogger(__name__)


class YahooFinanceProvider(StockDataProvider):
    def get_price(self, ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info
            return float(info.last_price)
        except Exception as e:
            logger.warning("Yahoo get_price failed for %s: %s", ticker, e)
            return None

    def get_history(self, ticker: str, days: int = 90) -> list[dict]:
        try:
            t = yf.Ticker(ticker)
            end = datetime.now()
            start = end - timedelta(days=days)
            hist = t.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
            result = []
            for date, row in hist.iterrows():
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(float(row["Close"]), 2),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                })
            return result
        except Exception as e:
            logger.warning("Yahoo get_history failed for %s: %s", ticker, e)
            return []

    def get_fundamentals(self, ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {
                "name": info.get("longName") or info.get("shortName") or "",
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "week52_high": info.get("fiftyTwoWeekHigh"),
                "week52_low": info.get("fiftyTwoWeekLow"),
                "next_earnings": info.get("earningsDate"),
                "sector": info.get("sector", "Unknown"),
                "description": info.get("longBusinessSummary", ""),
                "dividend_yield": info.get("dividendYield"),
                "revenue": info.get("totalRevenue"),
                "provider": "Yahoo Finance",
            }
        except Exception as e:
            logger.warning("Yahoo get_fundamentals failed for %s: %s", ticker, e)
            return {"provider": "Yahoo Finance", "error": str(e)}
