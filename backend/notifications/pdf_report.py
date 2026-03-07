"""ReportLab PDF daily summary report generator."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def generate_daily_report(
    signals: list[dict],
    holdings: list[dict],
    output_dir: Path,
) -> Optional[Path]:
    """Generate a PDF daily report and return its path."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        logger.error("reportlab is not installed — cannot generate PDF")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = output_dir / f"congress_tracker_report_{date_str}.pdf"

    # Colors
    NAVY = colors.HexColor("#06090f")
    BLUE = colors.HexColor("#3b82f6")
    AMBER = colors.HexColor("#f59e0b")
    EMERALD = colors.HexColor("#10b981")
    CORAL = colors.HexColor("#f87171")
    LIGHT = colors.HexColor("#e2e8f0")
    MUTED = colors.HexColor("#64748b")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=20, textColor=BLUE, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=10, textColor=MUTED, spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontSize=13, textColor=BLUE, spaceBefore=16, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, textColor=LIGHT, leading=14,
    )

    story = []

    # Header
    story.append(Paragraph("Congress Trade Tracker", title_style))
    story.append(Paragraph(f"Daily Report — {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 0.1 * inch))

    # Top Signals
    story.append(Paragraph("Top Conviction Signals", section_style))
    if signals:
        signal_data = [["Ticker", "Direction", "Score", "Members", "Reasoning"]]
        for s in sorted(signals, key=lambda x: x.get("conviction_score", 0), reverse=True)[:10]:
            import json
            members = json.loads(s.get("contributing_members", "[]"))
            direction = s.get("trade_direction", "BUY")
            score = s.get("conviction_score", 0)
            signal_data.append([
                s.get("ticker", ""),
                direction,
                f"{score:.0f}",
                ", ".join(members[:3]) + ("..." if len(members) > 3 else ""),
                (s.get("reasoning", "") or "")[:80],
            ])

        signal_table = Table(signal_data, colWidths=[0.7*inch, 0.7*inch, 0.5*inch, 2*inch, 3*inch])
        signal_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0f172a"), colors.HexColor("#1e293b")]),
            ("TEXTCOLOR", (0, 1), (-1, -1), LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#334155")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(signal_table)
    else:
        story.append(Paragraph("No signals available.", body_style))

    story.append(Spacer(1, 0.2 * inch))

    # Portfolio Snapshot
    story.append(Paragraph("Portfolio Snapshot", section_style))
    if holdings:
        holding_data = [["Ticker", "Name", "Shares", "Avg Cost", "Sector"]]
        for h in holdings:
            holding_data.append([
                h.get("ticker", ""),
                h.get("name", ""),
                f"{h.get('shares', 0):,.2f}",
                f"${h.get('avg_cost', 0):,.2f}",
                h.get("sector", ""),
            ])
        holding_table = Table(holding_data, colWidths=[0.7*inch, 2*inch, 0.8*inch, 0.9*inch, 2.5*inch])
        holding_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), EMERALD),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0f172a"), colors.HexColor("#1e293b")]),
            ("TEXTCOLOR", (0, 1), (-1, -1), LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#334155")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(holding_table)
    else:
        story.append(Paragraph("No holdings in portfolio.", body_style))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "Data sourced from public congressional disclosures, FEC, and USASpending.gov. "
        "Not financial advice.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=MUTED),
    ))

    doc.build(story)
    logger.info("PDF report generated: %s", output_path)
    return output_path
