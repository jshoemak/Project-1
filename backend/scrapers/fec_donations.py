"""FEC (Federal Election Commission) campaign donation data."""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)
BASE_URL = "https://api.open.fec.gov/v1"


def fetch_donations(member_name: str, api_key: str = "DEMO_KEY", cycle: int = 2024) -> list[dict]:
    """Fetch campaign donation records for a congressional member."""
    donations = []
    try:
        # Search for the candidate
        candidate_id = _find_candidate(member_name, api_key, cycle)
        if not candidate_id:
            logger.info("No FEC candidate found for: %s", member_name)
            return []

        # Fetch itemized receipts
        params = {
            "candidate_id": candidate_id,
            "two_year_transaction_period": cycle,
            "sort": "-contribution_receipt_date",
            "per_page": 100,
            "page": 1,
            "api_key": api_key,
        }
        with httpx.Client(timeout=20) as client:
            r = client.get(f"{BASE_URL}/schedules/schedule_a/", params=params)
            if r.status_code != 200:
                logger.warning("FEC API returned %d for %s", r.status_code, member_name)
                return []
            data = r.json()
            for item in data.get("results", []):
                donations.append({
                    "donor": item.get("contributor_name", "Unknown"),
                    "amount": item.get("contribution_receipt_amount", 0),
                    "date": item.get("contribution_receipt_date", "")[:10],
                    "industry": item.get("contributor_employer", "Unknown"),
                })
    except Exception as e:
        logger.error("FEC fetch_donations failed for %s: %s", member_name, e)
    return donations


def _find_candidate(name: str, api_key: str, cycle: int) -> Optional[str]:
    """Search FEC for a candidate by name and return their ID."""
    try:
        parts = name.split()
        last = parts[-1] if parts else name
        params = {
            "q": last,
            "election_year": cycle,
            "office": ["H", "S"],
            "per_page": 5,
            "api_key": api_key,
        }
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{BASE_URL}/candidates/search/", params=params)
            if r.status_code != 200:
                return None
            results = r.json().get("results", [])
            if not results:
                return None
            # Try to match name more precisely
            for candidate in results:
                cname = candidate.get("name", "").lower()
                if last.lower() in cname:
                    return candidate.get("candidate_id")
            return results[0].get("candidate_id")
    except Exception as e:
        logger.warning("FEC candidate search failed for %s: %s", name, e)
        return None
