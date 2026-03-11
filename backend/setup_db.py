"""Database initialization — run once before starting the app."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "congress_tracker.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            party       TEXT NOT NULL,
            chamber     TEXT NOT NULL,
            state       TEXT NOT NULL,
            committees  TEXT DEFAULT '[]',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trades (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id        INTEGER REFERENCES members(id),
            ticker           TEXT NOT NULL,
            trade_type       TEXT NOT NULL,
            trade_date       DATE NOT NULL,
            disclosure_date  DATE NOT NULL,
            amount_low       REAL,
            amount_high      REAL,
            sector           TEXT,
            source           TEXT DEFAULT 'capitol_trades',
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS donations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER REFERENCES members(id),
            donor     TEXT,
            amount    REAL,
            date      DATE,
            industry  TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS contracts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker      TEXT,
            company     TEXT,
            agency      TEXT,
            value       REAL,
            date        DATE,
            description TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS signals (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker              TEXT NOT NULL UNIQUE,
            conviction_score    REAL NOT NULL,
            congressional_vol   REAL DEFAULT 0,
            committee_relevance REAL DEFAULT 0,
            bipartisan          REAL DEFAULT 0,
            contract_correlation REAL DEFAULT 0,
            donation_alignment  REAL DEFAULT 0,
            direction_consensus REAL DEFAULT 0,
            freshness           REAL DEFAULT 0,
            contributing_members TEXT DEFAULT '[]',
            reasoning           TEXT,
            trade_direction     TEXT DEFAULT 'BUY',
            updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker     TEXT,
            score      REAL,
            channel    TEXT,
            sent_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sector_signals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            sector       TEXT NOT NULL UNIQUE,
            avg_score    REAL,
            etf_ticker   TEXT,
            trade_count  INTEGER DEFAULT 0,
            updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS holdings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker        TEXT NOT NULL,
            name          TEXT,
            shares        REAL NOT NULL,
            avg_cost      REAL NOT NULL,
            sector        TEXT,
            purchase_date DATE,
            added_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS config (
            key        TEXT PRIMARY KEY,
            value      TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profile (
            id         INTEGER PRIMARY KEY CHECK (id = 1),
            name       TEXT DEFAULT '',
            email      TEXT DEFAULT '',
            weights    TEXT DEFAULT '{}',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token      TEXT PRIMARY KEY,
            email      TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_trades_ticker      ON trades(ticker);
        CREATE INDEX IF NOT EXISTS idx_trades_member      ON trades(member_id);
        CREATE INDEX IF NOT EXISTS idx_trades_trade_date  ON trades(trade_date);
        CREATE INDEX IF NOT EXISTS idx_contracts_ticker   ON contracts(ticker);
        CREATE INDEX IF NOT EXISTS idx_signals_score      ON signals(conviction_score DESC);
    """)

    # Seed default config values
    defaults = [
        ("stock_provider", "yahoo"),
        ("alert_threshold", "80"),
        ("data_refresh_interval", "6"),
        ("ntfy_topic", ""),
        ("gmail_address", ""),
        ("gmail_app_password", ""),
        ("alert_recipient_email", ""),
        ("fec_api_key", "DEMO_KEY"),
        ("quiver_api_key", ""),
        ("polygon_api_key", ""),
        ("alpha_vantage_api_key", ""),
        ("unusual_whales_api_key", ""),
        ("opensecrets_api_key", ""),
    ]
    for key, val in defaults:
        cur.execute(
            "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (key, val)
        )

    # Migrations for existing databases
    cols = [r[1] for r in cur.execute("PRAGMA table_info(holdings)").fetchall()]
    if "purchase_date" not in cols:
        cur.execute("ALTER TABLE holdings ADD COLUMN purchase_date DATE")

    # Seed default profile row
    cur.execute("INSERT OR IGNORE INTO profile (id, name, email, weights) VALUES (1, '', '', '{}')")

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
