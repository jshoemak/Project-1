"""Gmail SMTP email alerts — requires App Password."""
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def send_signal_alert(
    gmail_address: str,
    app_password: str,
    recipient: str,
    ticker: str,
    score: float,
    direction: str,
    reasoning: str,
    members: list[str],
) -> bool:
    """Send an HTML email alert for a high-conviction signal."""
    if not gmail_address or not app_password or not recipient:
        logger.warning("Email not configured — skipping alert for %s", ticker)
        return False

    direction_color = "#10b981" if direction == "BUY" else "#f87171"
    score_color = "#f59e0b" if score >= 80 else "#3b82f6"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="background:#06090f;color:#e2e8f0;font-family:system-ui,sans-serif;padding:24px;">
      <div style="max-width:600px;margin:0 auto;">
        <h1 style="color:#3b82f6;margin-bottom:4px;">Congress Trade Tracker</h1>
        <p style="color:#64748b;margin-top:0;">High-Conviction Signal Detected</p>

        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:20px;margin:16px 0;">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span style="font-size:28px;font-weight:700;font-family:monospace;">{ticker}</span>
            <span style="background:{direction_color};color:#fff;padding:4px 12px;border-radius:4px;font-size:14px;font-weight:600;">{direction}</span>
            <span style="background:{score_color};color:#fff;padding:4px 12px;border-radius:4px;font-size:14px;font-weight:600;">{score:.0f}/100</span>
          </div>
          <p style="color:#94a3b8;margin:0;">{reasoning}</p>
        </div>

        <h3 style="color:#94a3b8;font-size:14px;text-transform:uppercase;letter-spacing:0.1em;">Contributing Members</h3>
        <ul style="color:#e2e8f0;padding-left:20px;">
          {"".join(f"<li>{m}</li>" for m in members)}
        </ul>

        <p style="color:#334155;font-size:12px;margin-top:32px;">
          Congress Trade Tracker · Self-hosted · Data from public disclosures only
        </p>
      </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Congress Tracker] {ticker} {direction} — {score:.0f}/100 Conviction"
        msg["From"] = gmail_address
        msg["To"] = recipient
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, recipient, msg.as_string())

        logger.info("Signal alert sent for %s to %s", ticker, recipient)
        return True
    except Exception as e:
        logger.error("Failed to send email alert for %s: %s", ticker, e)
        return False


def send_pdf_report(
    gmail_address: str,
    app_password: str,
    recipient: str,
    pdf_path: Path,
) -> bool:
    """Send the daily PDF report as an email attachment."""
    if not gmail_address or not app_password or not recipient:
        logger.warning("Email not configured — skipping PDF report")
        return False

    try:
        msg = MIMEMultipart()
        msg["Subject"] = "Congress Trade Tracker — Daily Report"
        msg["From"] = gmail_address
        msg["To"] = recipient

        body = MIMEText("Please find the attached daily report from Congress Trade Tracker.", "plain")
        msg.attach(body)

        with open(pdf_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
            attachment.add_header("Content-Disposition", "attachment", filename=pdf_path.name)
            msg.attach(attachment)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, recipient, msg.as_string())

        logger.info("PDF report sent to %s", recipient)
        return True
    except Exception as e:
        logger.error("Failed to send PDF report: %s", e)
        return False
