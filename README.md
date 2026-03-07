# Congress Trade Tracker

A self-hosted personal investment intelligence platform that monitors publicly disclosed US congressional stock trades and cross-references them with campaign donation data (FEC) and federal contract data (USASpending.gov) to generate conviction-scored investment signals.

---

## Features

- **Conviction Scoring** — 0-100 score per ticker weighted across 7 factors: congressional volume, committee relevance, bipartisan signal, federal contract correlation, donation alignment, direction consensus, and freshness
- **Live Dashboards** — Portfolio value, performance charts, signal list with expandable research panels
- **Automated Refresh** — APScheduler pulls fresh data every 6 hours (configurable)
- **Notifications** — Email alerts (Gmail + App Password) + mobile push (ntfy.sh, free)
- **PDF Reports** — ReportLab daily summary with top signals and portfolio snapshot
- **Provider Abstraction** — Yahoo Finance by default; swap to Polygon.io or Alpha Vantage by pasting an API key

---

## Requirements

- **Python 3.11+**
- **Node.js 18+**
- **Git**

---

## Windows Setup

### 1. Clone and enter the project
```bat
git clone <repo-url>
cd congress-tracker
```

### 2. Set up the Python backend
```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment
```bat
copy .env.example .env
```
Open `.env` in Notepad and fill in:
- `GMAIL_ADDRESS` — your Gmail address
- `GMAIL_APP_PASSWORD` — [generate an App Password](https://myaccount.google.com/apppasswords) (Gmail 2FA must be on)
- `ALERT_RECIPIENT_EMAIL` — where to send alerts (can be same as Gmail)
- `NTFY_TOPIC` — a secret unique topic name, e.g. `my-congress-alerts-abc123`
- `FEC_API_KEY` — get a free key at https://api.data.gov/signup (optional, `DEMO_KEY` works with rate limits)

### 4. Initialize the database and load data
```bat
python setup_db.py
python initial_data_pull.py
```
This seeds realistic sample data and attempts to pull live congressional trades. Takes ~30 seconds.

### 5. Install frontend dependencies
```bat
cd ..\frontend
npm install
```

### 6. Launch the app
```bat
cd ..
start_app.bat
```

- **Dashboard**: http://localhost:3000
- **API docs**: http://localhost:8000/docs

---

## Pages

### Portfolio (/)
- Subtle amber signal indicator linking to Signals page when high-conviction signals exist
- Portfolio cost basis header
- Area chart with 30D/60D/1Q/YTD/1Y range selectors (requires holdings + live prices)
- Holdings list with inline expand -> 90-day chart + position details
- Add Position button -> inline form

### Trade Signals (/signals)
- All signals sorted by conviction score, filterable by threshold (All / 60+ / 80+)
- Click any signal to expand a full research panel:
  - Catalyst text, 90-day price chart, fundamentals table
  - Congressional activity table with party badges
  - Federal contracts + Campaign donations
  - Score component breakdown bars

### Data Sources (/sources)
- Free tier: Capitol Trades, FEC, USASpending, Yahoo Finance -- all active
- Premium: Polygon.io, Alpha Vantage, Quiver Quantitative, Unusual Whales, OpenSecrets
  - Click **Connect** -> paste API key -> saved instantly, stock provider auto-swaps
- Generate PDF daily report on-demand

---

## Conviction Score Weights

| Factor | Weight | Description |
|---|---|---|
| Congressional Volume | 20% | More members trading = stronger signal |
| Committee Relevance | 20% | Member oversees the stock's sector |
| Bipartisan | 15% | Both parties buying |
| Contract Correlation | 15% | Company has active federal contracts |
| Donation Alignment | 10% | Industry donated to trading member |
| Direction Consensus | 10% | Mostly buys vs mixed |
| Freshness | 10% | Penalizes stale 45-day disclosures |

Scores >= 80 trigger email + push alerts.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GMAIL_ADDRESS` | -- | Gmail address for alerts |
| `GMAIL_APP_PASSWORD` | -- | Gmail App Password (not your login password) |
| `ALERT_RECIPIENT_EMAIL` | -- | Email to receive alerts |
| `NTFY_TOPIC` | -- | ntfy.sh topic for push notifications |
| `ALERT_THRESHOLD` | 80 | Minimum score to trigger alert |
| `DATA_REFRESH_INTERVAL` | 6 | Hours between auto-refresh |
| `FEC_API_KEY` | DEMO_KEY | FEC API key (free at api.data.gov) |
| `API_HOST` | 127.0.0.1 | Backend host |
| `API_PORT` | 8000 | Backend port |

---

## Data Sources

### Free (default)
- **Capitol Trades** -- scrapes congressional trade disclosures
- **FEC Bulk Data** -- campaign donation records via REST API
- **USASpending.gov** -- federal contract awards via REST API (no key)
- **Yahoo Finance** -- stock prices and fundamentals via `yfinance`

### Premium (upgrade via Data Sources page)
| Provider | Price | Replaces |
|---|---|---|
| Quiver Quantitative | $10/mo | Capitol Trades (real-time) |
| Polygon.io | $29/mo | Yahoo Finance |
| Alpha Vantage | $50/mo | Yahoo Finance |
| Unusual Whales | $30/mo | Congressional analytics layer |
| OpenSecrets | $25/mo | FEC donations (deeper data) |

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/signals?min_score=N` | List signals |
| GET | `/api/signals/{ticker}` | Signal detail with trades/contracts/donations |
| GET | `/api/trades?ticker=X&days=N` | Congressional trades |
| GET | `/api/holdings` | Portfolio holdings |
| POST | `/api/holdings` | Add holding |
| DELETE | `/api/holdings/{id}` | Remove holding |
| GET | `/api/portfolio/performance?range=30D` | Portfolio value history |
| GET | `/api/ticker/{ticker}/chart?days=90` | Price history |
| GET | `/api/ticker/{ticker}/fundamentals` | Fundamentals |
| GET | `/api/sources` | Data source status |
| POST | `/api/sources/{name}/connect` | Activate premium source |
| POST | `/api/refresh` | Manual data refresh |
| POST | `/api/report` | Generate + send PDF report |

Interactive docs at http://localhost:8000/docs

---

## File Structure

```
congress-tracker/
├── backend/
│   ├── main.py
│   ├── setup_db.py
│   ├── initial_data_pull.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/
│   ├── scrapers/
│   │   ├── capitol_trades.py
│   │   ├── fec_donations.py
│   │   └── usa_spending.py
│   ├── scoring/
│   │   └── conviction.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── yahoo.py
│   │   ├── polygon.py
│   │   └── alpha_vantage.py
│   └── notifications/
│       ├── email_alerts.py
│       ├── push_alerts.py
│       └── pdf_report.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/useApi.js
│   │   └── utils/format.js
├── start_app.bat
└── README.md
```

---

## Troubleshooting

**Backend won't start**
- Make sure the venv is activated: `venv\Scripts\activate`
- Check all pip packages installed: `pip install -r requirements.txt`

**No signals showing**
- Run `python initial_data_pull.py` from the `backend/` folder with venv active

**Email alerts not sending**
- Gmail requires a dedicated App Password, not your Google login
- 2-Step Verification must be enabled on your Google account

**Yahoo Finance errors**
- yfinance occasionally rate-limits; wait and retry, or upgrade to Polygon.io

**Port already in use**
- Change `API_PORT` in `.env` and update `vite.config.js` proxy target to match

---

## Disclaimer

Data sourced exclusively from public congressional disclosures, FEC filings, and federal contract databases. This tool is for informational and educational purposes only -- not financial advice.
