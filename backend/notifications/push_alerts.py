"""ntfy.sh push notifications — free, no account required."""
import logging

import httpx

logger = logging.getLogger(__name__)
NTFY_BASE = "https://ntfy.sh"


def send_push(topic: str, title: str, message: str, priority: str = "high", tags: list[str] = None) -> bool:
    """Send a push notification via ntfy.sh."""
    if not topic:
        logger.warning("ntfy topic not configured — skipping push")
        return False

    try:
        headers = {
            "Title": title,
            "Priority": priority,
        }
        if tags:
            headers["Tags"] = ",".join(tags)

        with httpx.Client(timeout=10) as client:
            r = client.post(f"{NTFY_BASE}/{topic}", data=message.encode(), headers=headers)
            r.raise_for_status()

        logger.info("Push notification sent: %s", title)
        return True
    except Exception as e:
        logger.error("ntfy push failed: %s", e)
        return False


def send_signal_push(topic: str, ticker: str, score: float, direction: str, reasoning: str) -> bool:
    """Send a formatted signal alert push notification."""
    emoji = "📈" if direction == "BUY" else "📉"
    title = f"{emoji} {ticker} {direction} — {score:.0f}/100"
    message = f"Conviction: {score:.0f}/100\n\n{reasoning}"
    tags = ["chart_increasing" if direction == "BUY" else "chart_decreasing", "moneybag"]
    return send_push(topic, title, message, priority="high", tags=tags)
