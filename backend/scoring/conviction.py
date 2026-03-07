"""Conviction scoring engine (0–100 scale).

Weight breakdown (must sum to 1.0):
  congressional_vol    0.20
  committee_relevance  0.20
  bipartisan           0.15
  contract_correlation 0.15
  donation_alignment   0.10
  direction_consensus  0.10
  freshness            0.10
"""
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

WEIGHTS = {
    "congressional_vol": 0.20,
    "committee_relevance": 0.20,
    "bipartisan": 0.15,
    "contract_correlation": 0.15,
    "donation_alignment": 0.10,
    "direction_consensus": 0.10,
    "freshness": 0.10,
}

# Committee → sector mapping for relevance scoring
COMMITTEE_SECTOR_MAP = {
    "Armed Services": ["Defense", "Aerospace", "Industrials"],
    "Banking": ["Financials", "Finance"],
    "Energy": ["Energy", "Utilities"],
    "Finance": ["Financials", "Finance"],
    "Health": ["Healthcare", "Pharmaceuticals", "Biotechnology"],
    "Intelligence": ["Technology", "Defense", "Communication Services"],
    "Science": ["Technology", "Industrials"],
    "Technology": ["Technology", "Communication Services"],
    "Commerce": ["Consumer Discretionary", "Communication Services", "Technology"],
    "Agriculture": ["Consumer Staples", "Agriculture"],
    "Transportation": ["Industrials", "Transportation"],
}


def compute_signal(ticker: str, trades: list[dict], contracts: list[dict], donations: list[dict]) -> dict:
    """
    Compute a conviction signal for a ticker.

    Args:
        ticker: Stock ticker symbol.
        trades: List of trade dicts {member_name, party, trade_type, trade_date,
                disclosure_date, amount_low, amount_high, sector, committees}.
        contracts: List of contract dicts for this ticker.
        donations: List of donation dicts for members trading this ticker.

    Returns:
        dict with conviction_score (0-100) and component scores.
    """
    if not trades:
        return _empty_signal(ticker)

    # 1. Congressional volume score (more members = higher score)
    n_members = len(set(t["member_name"] for t in trades))
    vol_score = min(1.0, n_members / 10.0)  # caps at 10 members = 100%

    # 2. Committee relevance score
    sector = _determine_sector(trades)
    committee_score = _committee_relevance(trades, sector)

    # 3. Bipartisan score
    parties = {t.get("party", "U") for t in trades}
    bipartisan_score = 1.0 if ("R" in parties and "D" in parties) else 0.3

    # 4. Contract correlation score
    contract_score = min(1.0, len(contracts) / 5.0) if contracts else 0.0
    if contracts:
        total_contract_value = sum(c.get("value", 0) or 0 for c in contracts)
        if total_contract_value > 100_000_000:
            contract_score = min(1.0, contract_score * 1.5)

    # 5. Donation alignment score
    member_names = {t["member_name"] for t in trades}
    relevant_donations = [d for d in donations if d.get("member_name") in member_names]
    donation_score = min(1.0, len(relevant_donations) / 20.0) if relevant_donations else 0.0

    # 6. Direction consensus score (mostly buys = high score)
    buys = sum(1 for t in trades if t.get("trade_type", "").upper() == "BUY")
    sells = sum(1 for t in trades if t.get("trade_type", "").upper() == "SELL")
    total_dir = buys + sells
    if total_dir > 0:
        direction_score = buys / total_dir
    else:
        direction_score = 0.5

    # 7. Freshness score (penalize stale disclosures; max delay 45 days)
    freshness_score = _freshness(trades)

    # Weighted sum → 0-100
    raw = (
        WEIGHTS["congressional_vol"] * vol_score
        + WEIGHTS["committee_relevance"] * committee_score
        + WEIGHTS["bipartisan"] * bipartisan_score
        + WEIGHTS["contract_correlation"] * contract_score
        + WEIGHTS["donation_alignment"] * donation_score
        + WEIGHTS["direction_consensus"] * direction_score
        + WEIGHTS["freshness"] * freshness_score
    )
    conviction_score = round(raw * 100, 1)

    trade_direction = "BUY" if buys >= sells else "SELL"
    contributing = list({t["member_name"] for t in trades})

    reasoning = _generate_reasoning(
        ticker, n_members, parties, buys, sells, contracts, committee_score, freshness_score
    )

    return {
        "ticker": ticker,
        "conviction_score": conviction_score,
        "congressional_vol": round(vol_score * 100, 1),
        "committee_relevance": round(committee_score * 100, 1),
        "bipartisan": round(bipartisan_score * 100, 1),
        "contract_correlation": round(contract_score * 100, 1),
        "donation_alignment": round(donation_score * 100, 1),
        "direction_consensus": round(direction_score * 100, 1),
        "freshness": round(freshness_score * 100, 1),
        "trade_direction": trade_direction,
        "contributing_members": json.dumps(contributing),
        "reasoning": reasoning,
    }


def _empty_signal(ticker: str) -> dict:
    return {
        "ticker": ticker,
        "conviction_score": 0.0,
        "congressional_vol": 0.0,
        "committee_relevance": 0.0,
        "bipartisan": 0.0,
        "contract_correlation": 0.0,
        "donation_alignment": 0.0,
        "direction_consensus": 0.0,
        "freshness": 0.0,
        "trade_direction": "BUY",
        "contributing_members": "[]",
        "reasoning": "Insufficient data.",
    }


def _determine_sector(trades: list[dict]) -> str:
    sectors = [t.get("sector") for t in trades if t.get("sector")]
    if not sectors:
        return "Unknown"
    return max(set(sectors), key=sectors.count)


def _committee_relevance(trades: list[dict], sector: str) -> float:
    if sector == "Unknown":
        return 0.0
    score = 0.0
    for trade in trades:
        committees = trade.get("committees", []) or []
        for committee in committees:
            for committee_key, sectors in COMMITTEE_SECTOR_MAP.items():
                if committee_key.lower() in committee.lower():
                    if any(s.lower() in sector.lower() for s in sectors):
                        score = max(score, 1.0)
                    else:
                        score = max(score, 0.3)
    return score


def _freshness(trades: list[dict]) -> float:
    """Score freshness: recent disclosures score higher. Max delay = 45 days."""
    now = datetime.now()
    scores = []
    for trade in trades:
        try:
            disc_date = datetime.strptime(trade["disclosure_date"], "%Y-%m-%d")
            days_old = (now - disc_date).days
            # Perfect score if < 7 days; zero if > 45 days
            if days_old <= 7:
                scores.append(1.0)
            elif days_old >= 45:
                scores.append(0.0)
            else:
                scores.append(1.0 - (days_old - 7) / 38.0)
        except (KeyError, ValueError):
            scores.append(0.5)
    return sum(scores) / len(scores) if scores else 0.5


def _generate_reasoning(
    ticker, n_members, parties, buys, sells, contracts, committee_score, freshness
) -> str:
    parts = []
    parts.append(f"{n_members} member{'s' if n_members != 1 else ''} traded {ticker}.")
    if "R" in parties and "D" in parties:
        parts.append("Bipartisan buying detected — strong cross-party conviction.")
    if buys > sells:
        parts.append(f"Buying pressure dominant ({buys} buys vs {sells} sells).")
    elif sells > buys:
        parts.append(f"Selling pressure dominant ({sells} sells vs {buys} buys).")
    if contracts:
        total = sum(c.get("value", 0) or 0 for c in contracts)
        parts.append(f"Active federal contracts totaling ${total:,.0f}.")
    if committee_score > 0.5:
        parts.append("Committee members with direct sector oversight are trading.")
    if freshness < 0.4:
        parts.append("Note: Some disclosures are approaching the 45-day limit.")
    return " ".join(parts)
