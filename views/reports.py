from io import BytesIO
from pathlib import Path
from collections import Counter
import re

import pandas as pd
import streamlit as st
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / "evaluation" / "evaluation_metrics.csv"

STOPWORDS = {
    "the","and","for","that","this","with","from","have","has","had",
    "was","were","are","you","your","they","their","them","but","not",
    "all","too","very","just","about","what","when","where","which",
    "who","why","how","can","could","would","should","will","been",
    "being","into","than","then","there","here","its","our","out",
    "get","got","also","more","most","some","only","really","still",
    "much","many","one","two","like","make","made","did","does","is",
    "it","in","on","of","to","a","an","as","at","by","be","or","if",
    "so","we","i","me","my","he","she","his","her","us","video",
    "videos","comment","comments","youtube","watch","watched",
    "watching","people","thing","things","content","thanks","thank",
    "hello","hey","guys"
}


def normalize_sentiment(value):
    value = str(value).strip().lower()
    if value in ("positive", "pos"):
        return "Positive"
    if value in ("negative", "neg"):
        return "Negative"
    if value in ("neutral", "neu"):
        return "Neutral"
    return value.title()


def find_text_column(df):
    candidates = [
        "comment","comments","text","content","review",
        "reviews","message","feedback","clean_comment"
    ]

    for col in candidates:
        if col in df.columns:
            return col

    best = None
    best_length = 0

    for col in df.select_dtypes(include=["object","string"]).columns:
        length = df[col].fillna("").astype(str).str.len().sum()
        if length > best_length:
            best = col
            best_length = length

    return best


def get_topics(df, text_col, limit=10):
    if not text_col:
        return []

    counter = Counter()

    for text in df[text_col].fillna("").astype(str):
        words = re.findall(r"[A-Za-z]{3,}", text.lower())
        counter.update(set(w for w in words if w not in STOPWORDS))

    return counter.most_common(limit)


def load_metrics():
    if not METRICS_FILE.exists():
        return {}

    try:
        df = pd.read_csv(METRICS_FILE)
    except Exception:
        return {}

    result = {}

    for _, row in df.iterrows():
        if len(row) < 2:
            continue
        key = str(row.iloc[0]).strip().lower()
        try:
            result[key] = float(row.iloc[1])
        except (TypeError, ValueError):
            pass

    return result


def metric(metrics, word):
    for key, value in metrics.items():
        if word in key:
            return value
    return None


def fmt(value):
    if value is None:
        return "—"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{value * 100:.2f}%" if value <= 1 else f"{value:.2f}%"


def build_pdf(data, source, total, positive, neutral, negative,
              dominant_sentiment, dominant_emotion, topics, metrics):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, PageBreak
        )
    except ImportError:
        return None

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    center = ParagraphStyle(
        "Center",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER
    )

    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=9,
        spaceAfter=6
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13
    )

    story = [
        Paragraph("AI-Based Social Media Analytics", title),
        Paragraph("Analytical Report", center),
        Spacer(1, 8 * mm),
        Paragraph(f"<b>Source:</b> {str(source)[:180]}", body),
        Paragraph(f"<b>Records analyzed:</b> {total}", body),
        Spacer(1, 4 * mm),
        Paragraph("1. Executive Summary", heading)
    ]

    summary = [
        ["Metric", "Result"],
        ["Positive", f"{positive} ({positive/total*100:.1f}%)"],
        ["Neutral", f"{neutral} ({neutral/total*100:.1f}%)"],
        ["Negative", f"{negative} ({negative/total*100:.1f}%)"],
        ["Dominant Sentiment", dominant_sentiment],
        ["Dominant Emotion", dominant_emotion]
    ]

    table = Table(summary, colWidths=[65*mm, 95*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#667eea")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),
        ("PADDING",(0,0),(-1,-1),6)
    ]))
    story.append(table)

    story.append(Paragraph("2. Discussion Trends", heading))

    topic_rows = [["Rank","Topic","Mentions"]]
    for i, (topic, count) in enumerate(topics, 1):
        topic_rows.append([str(i), topic, str(count)])

    if len(topic_rows) == 1:
        story.append(Paragraph("No meaningful topics were extracted.", body))
    else:
        topic_table = Table(
            topic_rows,
            colWidths=[20*mm,100*mm,35*mm]
        )
        topic_table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#764ba2")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.4,colors.grey),
            ("PADDING",(0,0),(-1,-1),5)
        ]))
        story.append(topic_table)

    story.append(Paragraph("3. Model Evaluation", heading))

    eval_rows = [
        ["Metric","Value"],
        ["Accuracy",fmt(metric(metrics,"accuracy"))],
        ["Precision",fmt(metric(metrics,"precision"))],
        ["Recall",fmt(metric(metrics,"recall"))],
        ["Weighted F1",fmt(metric(metrics,"f1"))]
    ]

    eval_table = Table(eval_rows, colWidths=[75*mm,55*mm])
    eval_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#11998e")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),
        ("PADDING",(0,0),(-1,-1),5)
    ]))
    story.append(eval_table)

    story.append(Paragraph(
        "Evaluation values are based on the project's manually labelled "
        "test dataset and are not a universal benchmark.",
        body
    ))

    story.append(PageBreak())
    story.append(Paragraph("4. Analyzed Records", heading))

    text_col = find_text_column(data)
    cols = []

    if text_col:
        cols.append(text_col)

    for col in ["sentiment","emotion","sentiment_score","emotion_score"]:
        if col in data.columns:
            cols.append(col)

    if cols:
        rows = [[str(c)[:25] for c in cols]]
        for _, row in data[cols].head(30).iterrows():
            rows.append([str(row[c])[:80] for c in cols])

        detail = Table(rows, repeatRows=1)
        detail.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#667eea")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.3,colors.grey),
            ("FONTSIZE",(0,0),(-1,-1),7),
            ("PADDING",(0,0),(-1,-1),4)
        ]))
        story.append(detail)

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Generated by AI-Based Social Media Analytics.",
        center
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def show():

    st.title("📄 Reports")
    st.caption(
        "Create a clean analytical report from the current "
        "YouTube, Text or CSV analysis."
    )

    df = st.session_state.get("analysis_df")

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.info(
            "📂 Analyze a YouTube video, text, or CSV file first."
        )
        return

    data = df.copy()

    if "sentiment" not in data.columns:
        st.error("The current analysis has no sentiment results.")
        return

    data["report_sentiment"] = data["sentiment"].apply(
        normalize_sentiment
    )

    total = len(data)
    positive = int((data["report_sentiment"] == "Positive").sum())
    neutral = int((data["report_sentiment"] == "Neutral").sum())
    negative = int((data["report_sentiment"] == "Negative").sum())

    dominant_sentiment = (
        data["report_sentiment"].value_counts().idxmax()
    )

    if "emotion" in data.columns:
        emotions = (
            data["emotion"].astype(str).str.strip().str.title()
        )
        emotions = emotions[
            ~emotions.isin(["","Nan","None","Unknown"])
        ]
    else:
        emotions = pd.Series(dtype=str)

    dominant_emotion = (
        emotions.value_counts().idxmax()
        if not emotions.empty else "N/A"
    )

    video = st.session_state.get("video_details")
    if isinstance(video, dict) and video.get("title"):
        source = video["title"]
    else:
        source = st.session_state.get(
            "csv_filename",
            "Current Analysis"
        )

    text_col = find_text_column(data)
    topics = get_topics(data, text_col)
    metrics = load_metrics()

    # ------------------------------------------------------
    # OVERVIEW
    # ------------------------------------------------------

    st.markdown("### 📋 Report Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("📊 Records", f"{total:,}")
    c2.metric("😊 Positive", f"{positive/total*100:.1f}%")
    c3.metric("😐 Neutral", f"{neutral/total*100:.1f}%")
    c4.metric("😟 Negative", f"{negative/total*100:.1f}%")
    c5.metric("🎭 Emotion", dominant_emotion)

    st.info(
        f"**Source:** {source}  •  "
        f"**Dominant sentiment:** {dominant_sentiment}  •  "
        f"**Dominant emotion:** {dominant_emotion}"
    )

    # ------------------------------------------------------
    # VISUAL SUMMARY
    # ------------------------------------------------------

    left, right = st.columns(2)

    with left:
        st.markdown("### 😊 Sentiment Summary")

        sentiment_df = pd.DataFrame({
            "Sentiment": ["Positive","Neutral","Negative"],
            "Records": [positive,neutral,negative]
        })

        fig = px.pie(
            sentiment_df,
            names="Sentiment",
            values="Records",
            hole=.55,
            color="Sentiment",
            color_discrete_map={
                "Positive":"#22c55e",
                "Neutral":"#f59e0b",
                "Negative":"#ef4444"
            }
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(
            height=300,
            margin=dict(l=5,r=5,t=10,b=5)
        )
        st.plotly_chart(fig,use_container_width=True)

    with right:
        st.markdown("### 🔥 Top Discussion Topics")

        if topics:
            topic_df = pd.DataFrame(
                topics,
                columns=["Topic","Mentions"]
            )

            fig = px.bar(
                topic_df.sort_values("Mentions"),
                x="Mentions",
                y="Topic",
                orientation="h",
                text="Mentions",
                color="Mentions",
                color_continuous_scale="Turbo"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=300,
                coloraxis_showscale=False,
                margin=dict(l=5,r=5,t=10,b=5)
            )
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("No meaningful topics were extracted.")

    # ------------------------------------------------------
    # EMOTION
    # ------------------------------------------------------

    if not emotions.empty:

        st.markdown("### 🎭 Emotion Summary")

        emotion_df = (
            emotions.value_counts()
            .head(8)
            .reset_index()
        )
        emotion_df.columns = ["Emotion","Records"]

        fig = px.bar(
            emotion_df.sort_values("Records"),
            x="Records",
            y="Emotion",
            orientation="h",
            text="Records",
            color="Records",
            color_continuous_scale="Plasma"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=290,
            coloraxis_showscale=False,
            margin=dict(l=5,r=5,t=10,b=5)
        )
        st.plotly_chart(fig,use_container_width=True)

    # ------------------------------------------------------
    # MODEL EVALUATION
    # ------------------------------------------------------

    if metrics:

        st.markdown("### 🧪 Model Evaluation")

        m1,m2,m3,m4 = st.columns(4)

        m1.metric(
            "Accuracy",
            fmt(metric(metrics,"accuracy"))
        )
        m2.metric(
            "Precision",
            fmt(metric(metrics,"precision"))
        )
        m3.metric(
            "Recall",
            fmt(metric(metrics,"recall"))
        )
        m4.metric(
            "Weighted F1",
            fmt(metric(metrics,"f1"))
        )

        st.caption(
            "Based on the project's manually labelled evaluation dataset."
        )

    # ------------------------------------------------------
    # DATA PREVIEW
    # ------------------------------------------------------

    with st.expander("💬 Preview analyzed records"):

        cols = []

        if text_col:
            cols.append(text_col)

        for col in [
            "sentiment",
            "emotion",
            "sentiment_score",
            "emotion_score"
        ]:
            if col in data.columns:
                cols.append(col)

        st.dataframe(
            data[cols].head(50) if cols else data.head(50),
            use_container_width=True,
            hide_index=True,
            height=280
        )

    # ------------------------------------------------------
    # EXPORT
    # ------------------------------------------------------

    st.markdown("### ⬇️ Export")

    pdf = build_pdf(
        data,
        source,
        total,
        positive,
        neutral,
        negative,
        dominant_sentiment,
        dominant_emotion,
        topics,
        metrics
    )

    e1,e2,e3 = st.columns(3)

    with e1:
        if pdf:
            st.download_button(
                "📄 Download PDF Report",
                data=pdf,
                file_name="social_media_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning(
                "Install reportlab to enable PDF reports."
            )

    with e2:
        csv_data = (
            data
            .drop(columns=["report_sentiment"],errors="ignore")
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "📊 Download CSV Data",
            data=csv_data,
            file_name="social_media_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

    with e3:
        summary = pd.DataFrame({
            "Metric": [
                "Source","Records","Positive","Neutral",
                "Negative","Dominant Sentiment","Dominant Emotion"
            ],
            "Value": [
                source,total,positive,neutral,negative,
                dominant_sentiment,dominant_emotion
            ]
        })

        st.download_button(
            "📝 Download Summary",
            data=summary.to_csv(index=False).encode("utf-8"),
            file_name="analysis_summary.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.caption(
        "The report is generated from the current analysis DataFrame. "
        "No Gemini service is used."
    )


show_reports = show