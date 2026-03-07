"""Capitol Trades scraper — congressional stock disclosures."""
import logging
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.capitoltrades.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SECTOR_MAP = {
    "Technology": "Technology",
    "Tech": "Technology",
    "Healthcare": "Healthcare",
    "Health Care": "Healthcare",
    "Finance": "Financials",
    "Financial": "Financials",
    "Energy": "Energy",
    "Industrials": "Industrials",
    "Consumer": "Consumer Discretionary",
    "Communication": "Communication Services",
    "Real Estate": "Real Estate",
    "Materials": "Materials",
    "Utilities": "Utilities",
}


def parse_amount(text: str) -> tuple[Optional[float], Optional[float]]:
    """Parse Capitol Trades amount ranges like '$1K – $15K'."""
    text = text.replace(",", "").replace("$", "").strip()
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}

    def convert(s: str) -> Optional[float]:
        s = s.strip()
        if not s:
            return None
        for suffix, mult in multipliers.items():
            if s.upper().endswith(suffix):
                try:
                    return float(s[:-1]) * mult
                except ValueError:
                    return None
        try:
            return float(s)
        except ValueError:
            return None

    parts = re.split(r"[-–—]", text, maxsplit=1)
    if len(parts) == 2:
        return convert(parts[0]), convert(parts[1])
    val = convert(parts[0])
    return val, val


def scrape_trades(pages: int = 5) -> list[dict]:
    """Scrape recent congressional trades from Capitol Trades."""
    all_trades = []
    try:
        with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            for page in range(1, pages + 1):
                url = f"{BASE_URL}/trades?page={page}&pageSize=96"
                try:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        logger.warning("Capitol Trades page %d returned %d", page, resp.status_code)
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    trades = _parse_trades_page(soup)
                    if not trades:
                        break
                    all_trades.extend(trades)
                    logger.info("Scraped %d trades from page %d", len(trades), page)
                except httpx.HTTPError as e:
                    logger.error("HTTP error on page %d: %s", page, e)
                    break
    except Exception as e:
        logger.error("Capitol Trades scrape failed: %s", e)
    return all_trades


def _parse_trades_page(soup: BeautifulSoup) -> list[dict]:
    trades = []
    rows = soup.select("table tbody tr") or soup.select(".trade-row") or soup.select("[data-trade]")

    if not rows:
        # Try generic row detection
        rows = soup.find_all("tr")
        rows = [r for r in rows if r.find("td")]

    for row in rows:
        try:
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            member_cell = cells[0]
            ticker_cell = cells[1] if len(cells) > 1 else None
            trade_type_cell = cells[2] if len(cells) > 2 else None
            amount_cell = cells[3] if len(cells) > 3 else None
            trade_date_cell = cells[4] if len(cells) > 4 else None
            disclosure_cell = cells[5] if len(cells) > 5 else None

            member_name = member_cell.get_text(strip=True)
            ticker = ticker_cell.get_text(strip=True).upper() if ticker_cell else ""
            trade_type = trade_type_cell.get_text(strip=True).upper() if trade_type_cell else "BUY"
            amount_text = amount_cell.get_text(strip=True) if amount_cell else ""
            trade_date_text = trade_date_cell.get_text(strip=True) if trade_date_cell else ""
            disclosure_text = disclosure_cell.get_text(strip=True) if disclosure_cell else ""

            if not ticker or not member_name:
                continue

            # Normalize trade type
            if "sell" in trade_type.lower():
                trade_type = "SELL"
            elif "buy" in trade_type.lower() or "purchase" in trade_type.lower():
                trade_type = "BUY"
            else:
                trade_type = "BUY"

            amount_low, amount_high = parse_amount(amount_text)

            def parse_date(s: str) -> str:
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y", "%d %b %Y"):
                    try:
                        return datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                return datetime.now().strftime("%Y-%m-%d")

            # Extract party from member info if available
            party = "U"
            if "(R)" in member_name or "Republican" in member_name:
                party = "R"
                member_name = member_name.replace("(R)", "").strip()
            elif "(D)" in member_name or "Democrat" in member_name:
                party = "D"
                member_name = member_name.replace("(D)", "").strip()

            trades.append({
                "member_name": member_name,
                "party": party,
                "ticker": ticker,
                "trade_type": trade_type,
                "trade_date": parse_date(trade_date_text),
                "disclosure_date": parse_date(disclosure_text) if disclosure_text else parse_date(trade_date_text),
                "amount_low": amount_low,
                "amount_high": amount_high,
                "sector": None,
            })
        except Exception as e:
            logger.debug("Failed to parse row: %s", e)
            continue

    return trades
