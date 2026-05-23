from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from crewai.tools import tool
from datetime import date
import os

@tool("generate_investment_report_pdf")
def generate_investment_report_pdf(ticker: str, company_name: str, recommendation: str,
                                    current_price: float, target_price: float, executive_summary: str,
                                    business_overview: str, financial_highlights: dict, dcf_results: dict,
                                    risk_factors: list, sentiment_summary: str) -> str:
    """Generates a professional PDF equity research report."""

    filename = f"reports/{ticker}_research_{date.today()}.pdf"
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    navy = colors.HexColor("#1a3a5c")
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], textColor=navy, fontSize=24, spaceAfter=6)
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"], textColor=navy, fontSize=13, spaceAfter=4)
    body_style = styles["BodyText"]
    rec_colors = {"BUY": colors.green, "HOLD": colors.orange, "SELL": colors.red}
    rec_color = rec_colors.get(recommendation, colors.black)

    try:
        target_price = float(str(target_price).replace(",", "").replace("$", ""))
    except Exception:
        target_price = 0.0
    try:
        current_price = float(str(current_price).replace(",", "").replace("$", ""))
    except Exception:
        current_price = 0.0

    upside_pct = ((target_price / current_price) - 1) * 100 if current_price > 0 else 0.0

    # Header
    story.append(Paragraph(f"{company_name} ({ticker})", title_style))
    rec_html = (
        f'<font color="#{rec_color.hexval()[2:]}">'
        f'<b>{recommendation}</b></font>'
        f' &nbsp;|&nbsp; Price: <b>${current_price:.2f}</b>'
        f' &nbsp;|&nbsp; Target: <b>${target_price:.2f}</b>'
        f' &nbsp;|&nbsp; Upside: <b>{upside_pct:.1f}%</b>'
    )
    story.append(Paragraph(rec_html, styles["Heading2"]))
    story.append(Paragraph(f"Equity Research Report | {date.today()} | AI Research Desk", styles["Normal"]))
    story.append(HRFlowable(width="100%", thickness=2, color=navy))
    story.append(Spacer(1, 0.2*inch))

    # Executive Summary
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(executive_summary, body_style))
    story.append(Spacer(1, 0.15*inch))

    # Business Overview
    story.append(Paragraph("Business Overview", h1_style))
    story.append(Paragraph(business_overview, body_style))
    story.append(Spacer(1, 0.15*inch))

    # Financial Highlights Table — format numbers properly
    story.append(Paragraph("Financial Highlights", h1_style))

    formatted_highlights = {}
    for k, v in financial_highlights.items():
        label = k.replace("_", " ").title()
        try:
            num = float(str(v).replace(",", "").replace("$", ""))
            if num > 1_000_000_000:
                formatted_highlights[label] = f"${num/1e9:.2f}B"
            elif num > 1_000_000:
                formatted_highlights[label] = f"${num/1e6:.2f}M"
            elif num < 10 and num > 0:
                formatted_highlights[label] = f"{num:.4f}"
            else:
                formatted_highlights[label] = str(round(num, 2))
        except Exception:
            formatted_highlights[label] = str(v)

    table_data = [["Metric", "Value"]] + [[k, v] for k, v in formatted_highlights.items()]
    fin_table = Table(table_data, colWidths=[3*inch, 3*inch])
    fin_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), navy),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 0.15*inch))

    # DCF Valuation — handle multiple key naming styles
    story.append(Paragraph("DCF Valuation", h1_style))

    ev = (dcf_results.get("enterprise_value") or
          dcf_results.get("Enterprise Value") or 0)
    ivs = (dcf_results.get("intrinsic_per_share") or
           dcf_results.get("intrinsic_value_per_share") or
           dcf_results.get("Intrinsic Value/Share") or 0)

    try:
        ev = float(str(ev).replace(",", "").replace("$", ""))
    except Exception:
        ev = 0.0
    try:
        ivs = float(str(ivs).replace(",", "").replace("$", ""))
    except Exception:
        ivs = 0.0

    margin = ((ivs / current_price) - 1) * 100 if current_price > 0 else 0.0

    story.append(Paragraph(
        f"Enterprise Value: <b>${ev/1e9:.1f}B</b> | "
        f"Intrinsic Value/Share: <b>${ivs:.2f}</b> | "
        f"Margin of Safety: <b>{margin:.1f}%</b>",
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))

    # Market Sentiment
    story.append(Paragraph("Market Sentiment", h1_style))
    story.append(Paragraph(sentiment_summary, body_style))
    story.append(Spacer(1, 0.15*inch))

    # Risk Factors
    story.append(Paragraph("Key Risk Factors", h1_style))
    for i, risk in enumerate(risk_factors[:5], 1):
        story.append(Paragraph(f"<b>{i}.</b> {risk}", body_style))
        story.append(Spacer(1, 0.05*inch))

    # ── Disclaimer ──
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Paragraph(
        "DISCLAIMER: AI-generated report for informational purposes only. "
        "Not financial advice. Do your own research.",
        ParagraphStyle("disc", parent=body_style, textColor=colors.grey, fontSize=8)
    ))

    doc.build(story)
    return f"PDF saved: {filename}"