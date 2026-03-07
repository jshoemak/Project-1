"""USASpending.gov federal contract data — no API key required."""
import logging

import httpx

logger = logging.getLogger(__name__)
BASE_URL = "https://api.usaspending.gov/api/v2"


def fetch_contracts_by_ticker(ticker: str, company_name: str = None, limit: int = 20) -> list[dict]:
    """Fetch federal contracts for a company by ticker/name."""
    contracts = []
    search_term = company_name or ticker

    try:
        payload = {
            "filters": {
                "keywords": [search_term],
                "award_type_codes": ["A", "B", "C", "D"],  # contracts only
                "time_period": [{"start_date": "2023-01-01", "end_date": "2025-12-31"}],
            },
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Awarding Agency", "Start Date", "Description",
            ],
            "page": 1,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc",
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{BASE_URL}/search/spending_by_award/", json=payload)
            if r.status_code != 200:
                logger.warning("USASpending returned %d for %s", r.status_code, ticker)
                return []
            data = r.json()
            for award in data.get("results", []):
                contracts.append({
                    "ticker": ticker.upper(),
                    "company": award.get("Recipient Name", search_term),
                    "agency": award.get("Awarding Agency", "Unknown"),
                    "value": award.get("Award Amount", 0),
                    "date": (award.get("Start Date") or "")[:10],
                    "description": award.get("Description", ""),
                })
    except Exception as e:
        logger.error("USASpending fetch failed for %s: %s", ticker, e)
    return contracts


def fetch_recent_contracts(days: int = 90, limit: int = 50) -> list[dict]:
    """Fetch recently awarded large contracts across all agencies."""
    from datetime import datetime, timedelta
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")

    contracts = []
    try:
        payload = {
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"],
                "time_period": [{"start_date": start, "end_date": end}],
                "award_amounts": [{"lower_bound": 1_000_000}],
            },
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Awarding Agency", "Start Date", "Description",
            ],
            "page": 1,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc",
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{BASE_URL}/search/spending_by_award/", json=payload)
            if r.status_code != 200:
                logger.warning("USASpending recent_contracts returned %d", r.status_code)
                return []
            data = r.json()
            for award in data.get("results", []):
                contracts.append({
                    "ticker": None,
                    "company": award.get("Recipient Name", "Unknown"),
                    "agency": award.get("Awarding Agency", "Unknown"),
                    "value": award.get("Award Amount", 0),
                    "date": (award.get("Start Date") or "")[:10],
                    "description": award.get("Description", ""),
                })
    except Exception as e:
        logger.error("USASpending fetch_recent_contracts failed: %s", e)
    return contracts
