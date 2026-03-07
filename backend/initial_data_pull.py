"""First-run data population script.

Attempts to pull real data from all free sources.
Falls back to realistic sample data if any source fails.
"""
import json
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# Ensure we can import from sibling modules
sys.path.insert(0, os.path.dirname(__file__))

from setup_db import get_connection, init_db

# --- Sample data (always available as fallback) ---

SAMPLE_MEMBERS = [
    {"name": "Nancy Pelosi", "party": "D", "chamber": "House", "state": "CA",
     "committees": ["Intelligence", "Judiciary"]},
    {"name": "Dan Crenshaw", "party": "R", "chamber": "House", "state": "TX",
     "committees": ["Armed Services", "Homeland Security"]},
    {"name": "Tommy Tuberville", "party": "R", "chamber": "Senate", "state": "AL",
     "committees": ["Armed Services", "Agriculture"]},
    {"name": "Mark Warner", "party": "D", "chamber": "Senate", "state": "VA",
     "committees": ["Intelligence", "Banking", "Finance"]},
    {"name": "Ro Khanna", "party": "D", "chamber": "House", "state": "CA",
     "committees": ["Armed Services", "Science, Space, and Technology"]},
    {"name": "Michael McCaul", "party": "R", "chamber": "House", "state": "TX",
     "committees": ["Foreign Affairs", "Homeland Security"]},
    {"name": "Josh Gottheimer", "party": "D", "chamber": "House", "state": "NJ",
     "committees": ["Financial Services", "Intelligence"]},
    {"name": "Marjorie Taylor Greene", "party": "R", "chamber": "House", "state": "GA",
     "committees": ["Homeland Security", "Oversight"]},
]

SAMPLE_TRADES = [
    {"member_name": "Nancy Pelosi", "ticker": "NVDA", "trade_type": "BUY",
     "trade_date": "2024-11-15", "disclosure_date": "2024-11-28",
     "amount_low": 500000, "amount_high": 1000000, "sector": "Technology"},
    {"member_name": "Dan Crenshaw", "ticker": "LMT", "trade_type": "BUY",
     "trade_date": "2024-11-10", "disclosure_date": "2024-11-22",
     "amount_low": 50000, "amount_high": 100000, "sector": "Defense"},
    {"member_name": "Tommy Tuberville", "ticker": "LMT", "trade_type": "BUY",
     "trade_date": "2024-11-12", "disclosure_date": "2024-11-25",
     "amount_low": 100000, "amount_high": 250000, "sector": "Defense"},
    {"member_name": "Mark Warner", "ticker": "NVDA", "trade_type": "BUY",
     "trade_date": "2024-11-08", "disclosure_date": "2024-11-20",
     "amount_low": 250000, "amount_high": 500000, "sector": "Technology"},
    {"member_name": "Ro Khanna", "ticker": "NVDA", "trade_type": "BUY",
     "trade_date": "2024-11-14", "disclosure_date": "2024-11-27",
     "amount_low": 15000, "amount_high": 50000, "sector": "Technology"},
    {"member_name": "Nancy Pelosi", "ticker": "MSFT", "trade_type": "BUY",
     "trade_date": "2024-10-30", "disclosure_date": "2024-11-10",
     "amount_low": 250000, "amount_high": 500000, "sector": "Technology"},
    {"member_name": "Josh Gottheimer", "ticker": "JPM", "trade_type": "BUY",
     "trade_date": "2024-11-05", "disclosure_date": "2024-11-18",
     "amount_low": 50000, "amount_high": 100000, "sector": "Financials"},
    {"member_name": "Michael McCaul", "ticker": "RTX", "trade_type": "BUY",
     "trade_date": "2024-11-01", "disclosure_date": "2024-11-15",
     "amount_low": 100000, "amount_high": 250000, "sector": "Defense"},
    {"member_name": "Dan Crenshaw", "ticker": "RTX", "trade_type": "BUY",
     "trade_date": "2024-11-03", "disclosure_date": "2024-11-17",
     "amount_low": 50000, "amount_high": 100000, "sector": "Defense"},
    {"member_name": "Marjorie Taylor Greene", "ticker": "TSLA", "trade_type": "BUY",
     "trade_date": "2024-11-07", "disclosure_date": "2024-11-20",
     "amount_low": 15000, "amount_high": 50000, "sector": "Consumer Discretionary"},
    {"member_name": "Mark Warner", "ticker": "MSFT", "trade_type": "BUY",
     "trade_date": "2024-10-28", "disclosure_date": "2024-11-08",
     "amount_low": 100000, "amount_high": 250000, "sector": "Technology"},
    {"member_name": "Ro Khanna", "ticker": "AAPL", "trade_type": "BUY",
     "trade_date": "2024-11-16", "disclosure_date": "2024-11-29",
     "amount_low": 15000, "amount_high": 50000, "sector": "Technology"},
    {"member_name": "Nancy Pelosi", "ticker": "AAPL", "trade_type": "SELL",
     "trade_date": "2024-10-15", "disclosure_date": "2024-10-28",
     "amount_low": 1000000, "amount_high": 5000000, "sector": "Technology"},
    {"member_name": "Tommy Tuberville", "ticker": "NOC", "trade_type": "BUY",
     "trade_date": "2024-11-09", "disclosure_date": "2024-11-22",
     "amount_low": 50000, "amount_high": 100000, "sector": "Defense"},
]

SAMPLE_CONTRACTS = [
    {"ticker": "LMT", "company": "Lockheed Martin", "agency": "Department of Defense",
     "value": 4_800_000_000, "date": "2024-10-15", "description": "F-35 production contract"},
    {"ticker": "RTX", "company": "RTX Corporation", "agency": "Department of Defense",
     "value": 2_100_000_000, "date": "2024-09-20", "description": "Patriot missile systems"},
    {"ticker": "NOC", "company": "Northrop Grumman", "agency": "Department of Defense",
     "value": 1_700_000_000, "date": "2024-10-01", "description": "B-21 Raider program"},
    {"ticker": "MSFT", "company": "Microsoft", "agency": "Department of Defense",
     "value": 21_900_000_000, "date": "2024-04-25", "description": "JEDI / IVAS HoloLens contract"},
    {"ticker": "NVDA", "company": "NVIDIA", "agency": "Department of Energy",
     "value": 97_000_000, "date": "2024-08-10", "description": "AI supercomputing for national labs"},
]

SAMPLE_DONATIONS = [
    {"member_name": "Dan Crenshaw", "donor": "Defense Industry PAC", "amount": 25000,
     "date": "2024-03-15", "industry": "Defense"},
    {"member_name": "Tommy Tuberville", "donor": "Aerospace Workers PAC", "amount": 10000,
     "date": "2024-02-20", "industry": "Defense"},
    {"member_name": "Nancy Pelosi", "donor": "Tech Industry Coalition", "amount": 50000,
     "date": "2024-05-01", "industry": "Technology"},
    {"member_name": "Mark Warner", "donor": "Finance & Banking PAC", "amount": 35000,
     "date": "2024-01-10", "industry": "Financials"},
]

SAMPLE_HOLDINGS = [
    {"ticker": "AAPL", "name": "Apple Inc.", "shares": 50, "avg_cost": 175.50, "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "shares": 25, "avg_cost": 385.00, "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "shares": 10, "avg_cost": 650.00, "sector": "Technology"},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "shares": 20, "avg_cost": 490.00, "sector": "ETF"},
]


def _get_member_id(conn, name: str) -> int | None:
    row = conn.execute("SELECT id FROM members WHERE name=?", (name,)).fetchone()
    return row["id"] if row else None


def load_sample_data(conn):
    """Insert all sample data into the database."""
    logger.info("Loading sample data...")

    # Members
    for m in SAMPLE_MEMBERS:
        conn.execute(
            "INSERT OR IGNORE INTO members (name, party, chamber, state, committees) VALUES (?,?,?,?,?)",
            (m["name"], m["party"], m["chamber"], m["state"], json.dumps(m["committees"])),
        )
    conn.commit()

    # Trades
    for t in SAMPLE_TRADES:
        member_id = _get_member_id(conn, t["member_name"])
        if not member_id:
            continue
        conn.execute(
            """INSERT OR IGNORE INTO trades
               (member_id, ticker, trade_type, trade_date, disclosure_date,
                amount_low, amount_high, sector)
               VALUES (?,?,?,?,?,?,?,?)""",
            (member_id, t["ticker"], t["trade_type"], t["trade_date"],
             t["disclosure_date"], t["amount_low"], t["amount_high"], t["sector"]),
        )
    conn.commit()

    # Contracts
    for c in SAMPLE_CONTRACTS:
        conn.execute(
            """INSERT OR IGNORE INTO contracts
               (ticker, company, agency, value, date, description)
               VALUES (?,?,?,?,?,?)""",
            (c["ticker"], c["company"], c["agency"], c["value"], c["date"], c["description"]),
        )
    conn.commit()

    # Donations
    for d in SAMPLE_DONATIONS:
        member_id = _get_member_id(conn, d["member_name"])
        if not member_id:
            continue
        conn.execute(
            """INSERT OR IGNORE INTO donations
               (member_id, donor, amount, date, industry)
               VALUES (?,?,?,?,?)""",
            (member_id, d["donor"], d["amount"], d["date"], d["industry"]),
        )
    conn.commit()

    # Holdings (only if empty)
    existing = conn.execute("SELECT COUNT(*) as c FROM holdings").fetchone()["c"]
    if existing == 0:
        for h in SAMPLE_HOLDINGS:
            conn.execute(
                "INSERT INTO holdings (ticker, name, shares, avg_cost, sector) VALUES (?,?,?,?,?)",
                (h["ticker"], h["name"], h["shares"], h["avg_cost"], h["sector"]),
            )
        conn.commit()

    logger.info("Sample data loaded successfully")


def compute_and_store_signals(conn):
    """Run conviction scoring on all tickers with trades."""
    from scoring.conviction import compute_signal

    tickers = [row[0] for row in conn.execute("SELECT DISTINCT ticker FROM trades").fetchall()]
    logger.info("Computing signals for %d tickers: %s", len(tickers), tickers)

    for ticker in tickers:
        rows = conn.execute(
            """SELECT t.*, m.name as member_name, m.party, m.committees
               FROM trades t JOIN members m ON t.member_id=m.id
               WHERE t.ticker=?""",
            (ticker,),
        ).fetchall()

        trades = []
        for r in rows:
            try:
                committees = json.loads(r["committees"] or "[]")
            except Exception:
                committees = []
            trades.append({
                "member_name": r["member_name"],
                "party": r["party"],
                "trade_type": r["trade_type"],
                "trade_date": r["trade_date"],
                "disclosure_date": r["disclosure_date"],
                "amount_low": r["amount_low"],
                "amount_high": r["amount_high"],
                "sector": r["sector"],
                "committees": committees,
            })

        contracts = [dict(r) for r in conn.execute(
            "SELECT * FROM contracts WHERE ticker=?", (ticker,)
        ).fetchall()]

        # Donations for members trading this ticker
        member_ids = [r["member_id"] for r in rows]
        donations = []
        if member_ids:
            placeholders = ",".join("?" * len(member_ids))
            donation_rows = conn.execute(
                f"SELECT d.*, m.name as member_name FROM donations d JOIN members m ON d.member_id=m.id WHERE d.member_id IN ({placeholders})",
                member_ids,
            ).fetchall()
            donations = [dict(r) for r in donation_rows]

        signal = compute_signal(ticker, trades, contracts, donations)

        conn.execute(
            """INSERT OR REPLACE INTO signals
               (ticker, conviction_score, congressional_vol, committee_relevance,
                bipartisan, contract_correlation, donation_alignment,
                direction_consensus, freshness, trade_direction,
                contributing_members, reasoning, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)""",
            (
                signal["ticker"], signal["conviction_score"],
                signal["congressional_vol"], signal["committee_relevance"],
                signal["bipartisan"], signal["contract_correlation"],
                signal["donation_alignment"], signal["direction_consensus"],
                signal["freshness"], signal["trade_direction"],
                signal["contributing_members"], signal["reasoning"],
            ),
        )
    conn.commit()
    logger.info("Signals computed and stored")


def try_live_scrape(conn):
    """Attempt to pull real data from Capitol Trades."""
    try:
        from scrapers.capitol_trades import scrape_trades
        logger.info("Attempting to scrape Capitol Trades...")
        trades = scrape_trades(pages=3)
        if not trades:
            logger.info("No live trades scraped — using sample data")
            return False

        for t in trades:
            # Upsert member
            conn.execute(
                "INSERT OR IGNORE INTO members (name, party, chamber, state) VALUES (?,?,?,?)",
                (t["member_name"], t.get("party", "U"), "Unknown", "Unknown"),
            )
            conn.commit()
            member_id = _get_member_id(conn, t["member_name"])
            if member_id:
                conn.execute(
                    """INSERT OR IGNORE INTO trades
                       (member_id, ticker, trade_type, trade_date, disclosure_date,
                        amount_low, amount_high, sector)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (member_id, t["ticker"], t["trade_type"], t["trade_date"],
                     t["disclosure_date"], t.get("amount_low"), t.get("amount_high"),
                     t.get("sector")),
                )
        conn.commit()
        logger.info("Live scrape successful: %d trades", len(trades))
        return True
    except Exception as e:
        logger.warning("Live scrape failed: %s — using sample data", e)
        return False


if __name__ == "__main__":
    logger.info("=== Congress Trade Tracker — Initial Data Pull ===")
    init_db()
    conn = get_connection()

    # Always load sample data first to ensure the app has data
    load_sample_data(conn)

    # Try to supplement with live data
    try_live_scrape(conn)

    # Compute conviction signals
    compute_and_store_signals(conn)

    conn.close()
    logger.info("=== Initial data pull complete. Start the app with start_app.bat ===")
