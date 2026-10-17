from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


def create_pdf(df):

    os.makedirs("reports", exist_ok=True)

    filename = "reports/analysis_report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "AI Based Social Media Analytics Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph("<br/><br/>", styles["Normal"])
    )

    total = len(df)

    positive = (df["sentiment"] == "positive").sum()
    neutral = (df["sentiment"] == "neutral").sum()
    negative = (df["sentiment"] == "negative").sum()

    elements.append(
        Paragraph(f"Total Records : {total}", styles["Heading2"])
    )

    elements.append(
        Paragraph(f"Positive : {positive}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Neutral : {neutral}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Negative : {negative}", styles["Normal"])
    )

    elements.append(
        Paragraph("<br/><br/>", styles["Normal"])
    )

    headers = list(df.columns)

    data = [headers]

    for row in df.head(20).values.tolist():
        data.append([str(i) for i in row])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
            ("GRID",(0,0),(-1,-1),1,colors.black),
            ("BACKGROUND",(0,1),(-1,-1),colors.beige)
        ])
    )

    elements.append(table)

    doc.build(elements)

    return filename