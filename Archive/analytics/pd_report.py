from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(df, filename="AI_Report.pdf"):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("<b>AI-Based Social Media Analytics Report</b>", styles["Title"])
    )

    story.append(
        Paragraph(f"Total Comments : {len(df)}", styles["Normal"])
    )

    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    story.append(
        Paragraph(f"Positive : {positive}", styles["Normal"])
    )

    story.append(
        Paragraph(f"Neutral : {neutral}", styles["Normal"])
    )

    story.append(
        Paragraph(f"Negative : {negative}", styles["Normal"])
    )

    top_emotion = df["emotion"].mode()[0]

    story.append(
        Paragraph(f"Top Emotion : {top_emotion}", styles["Normal"])
    )

    story.append(
        Paragraph("<br/><b>AI Recommendation</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(
            "Audience sentiment is mostly positive. Continue creating similar content.",
            styles["Normal"]
        )
    )

    doc.build(story)

    return filename