"""Congress Trade Tracker — FastAPI backend."""
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))
from setup_db import get_connection, init_db

app = FastAPI(title="Congress Trade Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database helpers ──────────────────────────────────────────────────────────

def db():
    return get_connection()


def get_config(key: str, default: str = "") -> str:
    conn = db()
    row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


# ── Stock provider factory ────────────────────────────────────────────────────

def get_stock_provider():
    provider_name = get_config("stock_provider", "yahoo")
    if provider_name == "polygon":
        key = get_config("polygon_api_key")
        if key:
            from providers.polygon import PolygonProvider
            return PolygonProvider(key)
    if provider_name == "alpha_vantage":
        key = get_config("alpha_vantage_api_key")
        if key:
            from providers.alpha_vantage import AlphaVantageProvider
            return AlphaVantageProvider(key)
    from providers.yahoo import YahooFinanceProvider
    return YahooFinanceProvider()


# ── Scheduler ─────────────────────────────────────────────────────────────────

def _refresh_data():
    """Periodic data refresh — called by scheduler."""
    try:
        logger.info("Scheduled data refresh started")
        conn = db()

        from scrapers.capitol_trades import scrape_trades
        trades = scrape_trades(pages=5)
        for t in trades:
            conn.execute(
                "INSERT OR IGNORE INTO members (name, party, chamber, state) VALUES (?,?,?,?)",
                (t["member_name"], t.get("party", "U"), "Unknown", "Unknown"),
            )
        conn.commit()

        for t in trades:
            row = conn.execute("SELECT id FROM members WHERE name=?", (t["member_name"],)).fetchone()
            if row:
                conn.execute(
                    """INSERT OR IGNORE INTO trades
                       (member_id, ticker, trade_type, trade_date, disclosure_date,
                        amount_low, amount_high, sector)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (row["id"], t["ticker"], t["trade_type"], t["trade_date"],
                     t["disclosure_date"], t.get("amount_low"), t.get("amount_high"), t.get("sector")),
                )
        conn.commit()

        # Recompute signals
        _recompute_signals(conn)

        # Check for new alerts
        _check_alerts(conn)

        conn.close()
        logger.info("Scheduled data refresh complete")
    except Exception as e:
        logger.error("Refresh error: %s", e)


def _recompute_signals(conn):
    from scoring.conviction import compute_signal
    tickers = [r[0] for r in conn.execute("SELECT DISTINCT ticker FROM trades").fetchall()]
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
        member_ids = list({r["member_id"] for r in rows})
        donations = []
        if member_ids:
            ph = ",".join("?" * len(member_ids))
            donations = [dict(r) for r in conn.execute(
                f"SELECT d.*, m.name as member_name FROM donations d JOIN members m ON d.member_id=m.id WHERE d.member_id IN ({ph})",
                member_ids,
            ).fetchall()]
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


def _check_alerts(conn):
    threshold = float(get_config("alert_threshold", "80"))
    signals = conn.execute(
        "SELECT * FROM signals WHERE conviction_score >= ?", (threshold,)
    ).fetchall()
    for s in signals:
        already_sent = conn.execute(
            "SELECT id FROM alerts WHERE ticker=? AND sent_at > datetime('now','-24 hours')",
            (s["ticker"],),
        ).fetchone()
        if already_sent:
            continue

        ticker = s["ticker"]
        score = s["conviction_score"]
        direction = s["trade_direction"]
        reasoning = s["reasoning"] or ""
        try:
            members = json.loads(s["contributing_members"] or "[]")
        except Exception:
            members = []

        ntfy_topic = get_config("ntfy_topic")
        if ntfy_topic:
            from notifications.push_alerts import send_signal_push
            send_signal_push(ntfy_topic, ticker, score, direction, reasoning)

        gmail = get_config("gmail_address")
        pwd = get_config("gmail_app_password")
        recipient = get_config("alert_recipient_email")
        if gmail and pwd and recipient:
            from notifications.email_alerts import send_signal_alert
            send_signal_alert(gmail, pwd, recipient, ticker, score, direction, reasoning, members)

        conn.execute(
            "INSERT INTO alerts (ticker, score, channel) VALUES (?,?,?)",
            (ticker, score, "both"),
        )
    conn.commit()


@app.on_event("startup")
def startup():
    init_db()
    # Start scheduler
    interval_hours = int(get_config("data_refresh_interval", "6") or "6")
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(_refresh_data, "interval", hours=interval_hours, id="refresh")
        scheduler.start()
        logger.info("Scheduler started — refresh every %d hours", interval_hours)
    except Exception as e:
        logger.warning("Scheduler failed to start: %s", e)


# ── Models ────────────────────────────────────────────────────────────────────

class HoldingCreate(BaseModel):
    ticker: str
    name: str = ""
    shares: float
    avg_cost: float
    sector: str = ""
    purchase_date: str = ""


class SourceConnect(BaseModel):
    api_key: str


class ProfileUpdate(BaseModel):
    name: str = ""
    email: str = ""
    weights: dict = {}


class LoginRequest(BaseModel):
    email: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/signals")
def get_signals(min_score: float = Query(0, ge=0, le=100)):
    conn = db()
    rows = conn.execute(
        "SELECT * FROM signals WHERE conviction_score >= ? ORDER BY conviction_score DESC",
        (min_score,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/signals/{ticker}")
def get_signal_detail(ticker: str):
    ticker = ticker.upper()
    conn = db()
    signal = conn.execute("SELECT * FROM signals WHERE ticker=?", (ticker,)).fetchone()
    if not signal:
        conn.close()
        raise HTTPException(status_code=404, detail="Signal not found")

    trades = conn.execute(
        """SELECT t.*, m.name as member_name, m.party, m.chamber, m.state, m.committees
           FROM trades t JOIN members m ON t.member_id=m.id
           WHERE t.ticker=?
           ORDER BY t.trade_date DESC""",
        (ticker,),
    ).fetchall()

    contracts = conn.execute(
        "SELECT * FROM contracts WHERE ticker=? ORDER BY value DESC",
        (ticker,),
    ).fetchall()

    member_ids = list({r["member_id"] for r in trades})
    donations = []
    if member_ids:
        ph = ",".join("?" * len(member_ids))
        donations = conn.execute(
            f"SELECT d.*, m.name as member_name FROM donations d JOIN members m ON d.member_id=m.id WHERE d.member_id IN ({ph})",
            member_ids,
        ).fetchall()

    conn.close()
    return {
        **dict(signal),
        "trades": [dict(r) for r in trades],
        "contracts": [dict(r) for r in contracts],
        "donations": [dict(r) for r in donations],
    }


@app.get("/api/trades")
def get_trades(
    ticker: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
):
    conn = db()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    if ticker:
        rows = conn.execute(
            """SELECT t.*, m.name as member_name, m.party, m.chamber
               FROM trades t JOIN members m ON t.member_id=m.id
               WHERE t.ticker=? AND t.trade_date >= ?
               ORDER BY t.trade_date DESC""",
            (ticker.upper(), since),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT t.*, m.name as member_name, m.party, m.chamber
               FROM trades t JOIN members m ON t.member_id=m.id
               WHERE t.trade_date >= ?
               ORDER BY t.trade_date DESC
               LIMIT 200""",
            (since,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/holdings")
def get_holdings():
    conn = db()
    rows = conn.execute("SELECT * FROM holdings ORDER BY added_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/holdings")
def add_holding(body: HoldingCreate):
    conn = db()
    purchase_date = body.purchase_date or datetime.now().strftime("%Y-%m-%d")
    cur = conn.execute(
        "INSERT INTO holdings (ticker, name, shares, avg_cost, sector, purchase_date) VALUES (?,?,?,?,?,?)",
        (body.ticker.upper(), body.name, body.shares, body.avg_cost, body.sector, purchase_date),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM holdings WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/api/holdings/{holding_id}")
def delete_holding(holding_id: int):
    conn = db()
    conn.execute("DELETE FROM holdings WHERE id=?", (holding_id,))
    conn.commit()
    conn.close()
    return {"deleted": holding_id}


@app.get("/api/portfolio/performance")
def portfolio_performance(range: str = Query("30D")):
    range_map = {"30D": 30, "60D": 60, "1Q": 90, "YTD": None, "1Y": 365}
    days = range_map.get(range, 30)
    if days is None:
        now = datetime.now()
        days = (now - datetime(now.year, 1, 1)).days + 1

    conn = db()
    holdings = conn.execute("SELECT * FROM holdings").fetchall()
    conn.close()

    if not holdings:
        return []

    provider = get_stock_provider()
    result = []

    # Get history for each holding
    ticker_histories: dict[str, list[dict]] = {}
    for h in holdings:
        hist = provider.get_history(h["ticker"], days=days)
        ticker_histories[h["ticker"]] = hist

    # Build daily portfolio values
    all_dates: set[str] = set()
    for hist in ticker_histories.values():
        all_dates.update(d["date"] for d in hist)

    for date in sorted(all_dates):
        total = 0.0
        for h in holdings:
            # Only include this holding for dates >= its purchase_date
            purchase_date = h["purchase_date"] or ""
            if purchase_date and date < purchase_date:
                continue
            hist = ticker_histories.get(h["ticker"], [])
            price = next((d["close"] for d in hist if d["date"] == date), None)
            if price:
                total += price * h["shares"]
        if total > 0:
            result.append({"date": date, "value": round(total, 2)})

    return result


@app.get("/api/ticker/{ticker}/info")
def ticker_info(ticker: str):
    """Quick lookup: company name, current price, and sector for auto-fill."""
    ticker = ticker.upper()
    provider = get_stock_provider()
    fundamentals = provider.get_fundamentals(ticker)
    hist = provider.get_history(ticker, days=2)
    current_price = hist[-1]["close"] if hist else None
    return {
        "ticker": ticker,
        "name": fundamentals.get("name") or fundamentals.get("longName") or "",
        "sector": fundamentals.get("sector") or "",
        "current_price": current_price,
    }


@app.get("/api/ticker/{ticker}/chart")
def ticker_chart(ticker: str, days: int = Query(90, ge=1, le=365)):
    provider = get_stock_provider()
    history = provider.get_history(ticker.upper(), days=days)
    if not history:
        raise HTTPException(status_code=404, detail="No price data available")
    return history


@app.get("/api/ticker/{ticker}/fundamentals")
def ticker_fundamentals(ticker: str):
    provider = get_stock_provider()
    data = provider.get_fundamentals(ticker.upper())
    return data


@app.get("/api/sources")
def get_sources():
    conn = db()
    config_rows = conn.execute("SELECT key, value FROM config").fetchall()
    conn.close()
    config = {r["key"]: r["value"] for r in config_rows}

    def _connected(key: str) -> bool:
        val = config.get(key, "")
        return bool(val and val not in ("", "DEMO_KEY"))

    return {
        "free": [
            {"name": "capitol_trades", "label": "Capitol Trades", "connected": True,
             "description": "Congressional trade disclosures via web scraping"},
            {"name": "fec", "label": "FEC Bulk Data", "connected": True,
             "description": "Campaign donation records — free API key"},
            {"name": "usaspending", "label": "USASpending.gov", "connected": True,
             "description": "Federal contract awards — no key required"},
            {"name": "yahoo", "label": "Yahoo Finance", "connected": True,
             "description": "Stock prices & fundamentals via yfinance"},
        ],
        "premium": [
            {"name": "quiver", "label": "Quiver Quantitative", "price": "$10/mo",
             "connected": _connected("quiver_api_key"),
             "description": "Real-time congressional trades API"},
            {"name": "polygon", "label": "Polygon.io", "price": "$29/mo",
             "connected": _connected("polygon_api_key"),
             "description": "Professional-grade market data"},
            {"name": "alpha_vantage", "label": "Alpha Vantage", "price": "$50/mo",
             "connected": _connected("alpha_vantage_api_key"),
             "description": "Market data with extended fundamentals"},
            {"name": "unusual_whales", "label": "Unusual Whales", "price": "$30/mo",
             "connected": _connected("unusual_whales_api_key"),
             "description": "Congressional + insider analytics"},
            {"name": "opensecrets", "label": "OpenSecrets", "price": "$25/mo",
             "connected": _connected("opensecrets_api_key"),
             "description": "Deep lobbying & donation data"},
        ],
        "active_stock_provider": config.get("stock_provider", "yahoo"),
    }


@app.post("/api/sources/{name}/connect")
def connect_source(name: str, body: SourceConnect):
    key_map = {
        "quiver": "quiver_api_key",
        "polygon": "polygon_api_key",
        "alpha_vantage": "alpha_vantage_api_key",
        "unusual_whales": "unusual_whales_api_key",
        "opensecrets": "opensecrets_api_key",
    }
    if name not in key_map:
        raise HTTPException(status_code=400, detail=f"Unknown source: {name}")

    config_key = key_map[name]
    conn = db()
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?,?,CURRENT_TIMESTAMP)",
        (config_key, body.api_key),
    )

    # Update active stock provider if relevant
    if name in ("polygon", "alpha_vantage") and body.api_key:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES ('stock_provider',?,CURRENT_TIMESTAMP)",
            (name,),
        )

    conn.commit()
    conn.close()
    return {"connected": True, "provider": name}


@app.post("/api/refresh")
def manual_refresh():
    _refresh_data()
    return {"status": "ok", "message": "Data refresh initiated"}


@app.post("/api/report")
def generate_report():
    conn = db()
    signals = [dict(r) for r in conn.execute(
        "SELECT * FROM signals ORDER BY conviction_score DESC LIMIT 20"
    ).fetchall()]
    holdings = [dict(r) for r in conn.execute("SELECT * FROM holdings").fetchall()]
    conn.close()

    from notifications.pdf_report import generate_daily_report
    output_dir = Path(__file__).parent / "data"
    pdf_path = generate_daily_report(signals, holdings, output_dir)

    if not pdf_path:
        raise HTTPException(status_code=500, detail="PDF generation failed")

    gmail = get_config("gmail_address")
    pwd = get_config("gmail_app_password")
    recipient = get_config("alert_recipient_email")
    if gmail and pwd and recipient:
        from notifications.email_alerts import send_pdf_report
        send_pdf_report(gmail, pwd, recipient, pdf_path)

    return {"status": "ok", "pdf": str(pdf_path)}


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/api/profile")
def get_profile():
    conn = db()
    row = conn.execute("SELECT * FROM profile WHERE id=1").fetchone()
    conn.close()
    if not row:
        return {"name": "", "email": "", "weights": {}}
    weights = {}
    try:
        weights = json.loads(row["weights"] or "{}")
    except Exception:
        pass
    return {"name": row["name"] or "", "email": row["email"] or "", "weights": weights}


@app.put("/api/profile")
def update_profile(body: ProfileUpdate):
    conn = db()
    conn.execute(
        """INSERT INTO profile (id, name, email, weights, updated_at)
           VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(id) DO UPDATE SET
             name=excluded.name,
             email=excluded.email,
             weights=excluded.weights,
             updated_at=excluded.updated_at""",
        (body.name, body.email, json.dumps(body.weights)),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


# ── Auth ──────────────────────────────────────────────────────────────────────

def _get_profile_email() -> str:
    conn = db()
    row = conn.execute("SELECT email FROM profile WHERE id=1").fetchone()
    conn.close()
    return (row["email"] or "").strip() if row else ""


@app.post("/api/auth/login")
def auth_login(body: LoginRequest):
    profile_email = _get_profile_email()
    # First-run: no email configured yet — allow any email to bootstrap
    if profile_email and body.email.strip().lower() != profile_email.lower():
        raise HTTPException(status_code=401, detail="Email does not match profile.")
    token = str(uuid.uuid4())
    expires = datetime.now() + timedelta(days=30)
    conn = db()
    # Clean up expired sessions
    conn.execute("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
    conn.execute(
        "INSERT INTO sessions (token, email, expires_at) VALUES (?,?,?)",
        (token, body.email.strip(), expires.isoformat()),
    )
    conn.commit()
    conn.close()
    return {"token": token, "email": body.email.strip()}


@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(None)):
    token = _extract_token(authorization)
    # Allow the local_setup placeholder token
    if token == "local_setup":
        return {"email": "", "setup_required": True}
    conn = db()
    row = conn.execute(
        "SELECT * FROM sessions WHERE token=? AND expires_at > CURRENT_TIMESTAMP",
        (token,),
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return {"email": row["email"]}


@app.post("/api/auth/logout")
def auth_logout(authorization: Optional[str] = Header(None)):
    token = _extract_token(authorization)
    conn = db()
    conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    conn.commit()
    conn.close()
    return {"ok": True}


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token.")
    return authorization.split(" ", 1)[1]


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
