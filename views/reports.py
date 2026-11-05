
from collections import Counter
from html import escape
from io import BytesIO
from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import streamlit as st


# ==========================================================
# CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / "evaluation" / "evaluation_metrics.csv"

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "have",
    "has", "had", "was", "were", "are", "you", "your", "they",
    "their", "them", "but", "not", "all", "too", "very", "just",
    "about", "what", "when", "where", "which", "who", "why", "how",
    "can", "could", "would", "should", "will", "been", "being",
    "into", "than", "then", "there", "here", "its", "our", "out",
    "get", "got", "also", "more", "most", "some", "only", "really",
    "still", "much", "many", "one", "two", "like", "make", "made",
    "did", "does", "is", "it", "in", "on", "of", "to", "a", "an",
    "as", "at", "by", "be", "or", "if", "so", "we", "i", "me",
    "my", "he", "she", "his", "her", "us", "video", "videos",
    "comment", "comments", "youtube", "watch", "watched", "watching",
    "people", "thing", "things", "content", "thanks", "thank",
    "hello", "hey", "guys",
}


# ==========================================================
# SHARED DATA LOADER
# ==========================================================

def get_shared_analysis_data():
    """Get the currently available dataset from shared session state."""

    for key in ("analysis_df", "universal_analysis_df", "df"):
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


# ==========================================================
# COLUMN DETECTION
# ==========================================================

def find_column(df, candidates):
    """Find a column regardless of capitalization or surrounding spaces."""

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        actual = normalized.get(candidate.strip().lower())

        if actual is not None:
            return actual

    return None


def find_text_column(df):
    """Identify the most likely text/comment column."""

    candidates = [
        "comment",
        "comments",
        "text",
        "content",
        "review",
        "reviews",
        "message",
        "feedback",
        "clean_comment",
        "description",
    ]

    found = find_column(df, candidates)

    if found is not None:
        return found

    best_column = None
    best_length = 0

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        name = str(column).strip().lower()

        if name in {
            "sentiment",
            "predicted_sentiment",
            "sentiment_label",
            "emotion",
            "predicted_emotion",
            "emotion_label",
        }:
            continue

        length = (
            df[column]
            .fillna("")
            .astype(str)
            .str.len()
            .sum()
        )

        if length > best_length:
            best_column = column
            best_length = length

    return best_column


# ==========================================================
# SENTIMENT AND TOPIC HELPERS
# ==========================================================

def normalize_sentiment(value):
    value = str(value).strip().lower()

    mapping = {
        "positive": "Positive",
        "pos": "Positive",
        "good": "Positive",
        "favorable": "Positive",
        "favourable": "Positive",
        "happy": "Positive",
        "negative": "Negative",
        "neg": "Negative",
        "bad": "Negative",
        "unfavorable": "Negative",
        "unfavourable": "Negative",
        "angry": "Negative",
        "neutral": "Neutral",
        "neu": "Neutral",
        "unknown": "Unknown",
        "nan": "Unknown",
        "none": "Unknown",
        "null": "Unknown",
        "": "Unknown",
    }

    return mapping.get(value, value.title())


def get_topics(df, text_col, limit=10):
    """Extract frequent non-stopword terms from the text data."""

    if text_col is None or text_col not in df.columns:
        return []

    counter = Counter()

    for text in df[text_col].fillna("").astype(str):
        words = re.findall(r"[A-Za-z]{3,}", text.lower())

        counter.update(
            word
            for word in words
            if word not in STOPWORDS
        )

    return counter.most_common(limit)


# ==========================================================
# MODEL METRICS
# ==========================================================

def load_metrics():
    if not METRICS_FILE.exists():
        return {}

    try:
        metrics_df = pd.read_csv(METRICS_FILE)
    except Exception:
        return {}

    results = {}

    for _, row in metrics_df.iterrows():
        if len(row) < 2:
            continue

        key = str(row.iloc[0]).strip().lower()

        try:
            results[key] = float(row.iloc[1])
        except (TypeError, ValueError):
            continue

    return results


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

    if pd.isna(value):
        return "—"

    return f"{value * 100:.2f}%" if 0 <= value <= 1 else f"{value:.2f}%"


# ==========================================================
# PDF REPORT
# ==========================================================

def build_pdf(
    data,
    source,
    total,
    positive,
    neutral,
    negative,
    dominant_sentiment,
    dominant_emotion,
    topics,
    metrics,
):
    """Build a PDF report. Return None if ReportLab is unavailable."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle,
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
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
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        alignment=TA_CENTER,
        spaceAfter=5,
    )

    center_style = ParagraphStyle(
        "ReportCenter",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=9,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
    )

    def make_table(rows, header_color="#667eea", widths=None):
        table = Table(
            rows,
            colWidths=widths,
            repeatRows=1,
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(header_color),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ])
        )

        return table

    positive_pct = positive / total * 100 if total else 0
    neutral_pct = neutral / total * 100 if total else 0
    negative_pct = negative / total * 100 if total else 0

    story = [
        Paragraph("AI-Based Social Media Analytics", title_style),
        Paragraph("Analytical Report", center_style),
        Spacer(1, 8 * mm),
        Paragraph(
            f"<b>Source:</b> {escape(str(source)[:180])}",
            body_style,
        ),
        Paragraph(f"<b>Records analyzed:</b> {total}", body_style),
        Spacer(1, 4 * mm),
        Paragraph("1. Executive Summary", heading_style),
    ]

    summary_rows = [
        ["Metric", "Result"],
        ["Positive", f"{positive} ({positive_pct:.1f}%)"],
        ["Neutral", f"{neutral} ({neutral_pct:.1f}%)"],
        ["Negative", f"{negative} ({negative_pct:.1f}%)"],
        ["Dominant Sentiment", dominant_sentiment],
        ["Dominant Emotion", dominant_emotion],
    ]

    story.append(
        make_table(
            summary_rows,
            widths=[65 * mm, 95 * mm],
        )
    )

    story.append(Paragraph("2. Discussion Topics", heading_style))

    topic_rows = [["Rank", "Topic", "Mentions"]]

    for rank, (topic, count) in enumerate(topics, start=1):
        topic_rows.append(
            [str(rank), escape(str(topic)), str(count)]
        )

    if len(topic_rows) == 1:
        story.append(
            Paragraph("No meaningful topics were extracted.", body_style)
        )
    else:
        story.append(
            make_table(
                topic_rows,
                header_color="#764ba2",
                widths=[20 * mm, 100 * mm, 35 * mm],
            )
        )

    story.append(Paragraph("3. Model Evaluation", heading_style))

    evaluation_rows = [
        ["Metric", "Value"],
        ["Accuracy", fmt(metric(metrics, "accuracy"))],
        ["Precision", fmt(metric(metrics, "precision"))],
        ["Recall", fmt(metric(metrics, "recall"))],
        ["Weighted F1", fmt(metric(metrics, "f1"))],
    ]

    story.append(
        make_table(
            evaluation_rows,
            header_color="#11998e",
            widths=[75 * mm, 55 * mm],
        )
    )

    story.append(
        Paragraph(
            "Evaluation values come from the project's saved evaluation "
            "metrics, when available. They are not a universal benchmark.",
            body_style,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("4. Analyzed Records", heading_style))

    text_column = find_text_column(data)
    selected_columns = []

    if text_column is not None:
        selected_columns.append(text_column)

    for candidate in [
        "sentiment",
        "emotion",
        "sentiment_score",
        "emotion_score",
    ]:
        actual = find_column(data, [candidate])

        if actual is not None and actual not in selected_columns:
            selected_columns.append(actual)

    if selected_columns:
        rows = [
            [str(column)[:25] for column in selected_columns]
        ]

        for _, row in data[selected_columns].head(30).iterrows():
            rows.append([
                str(row[column])[:100]
                for column in selected_columns
            ])

        story.append(make_table(rows, header_color="#667eea"))
    else:
        story.append(
            Paragraph(
                "No suitable text or sentiment columns were found.",
                body_style,
            )
        )

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "Generated by AI-Based Social Media Analytics.",
            center_style,
        )
    )

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()


# ==========================================================
# MAIN REPORTS PAGE
# ==========================================================

def show():

    st.title("📄 Reports")

    st.caption(
        "Generate a downloadable analytical report from the current "
        "YouTube, text-analysis, or uploaded CSV dataset."
    )

    # ------------------------------------------------------
    # LOAD SHARED DATA
    # ------------------------------------------------------

    df = get_shared_analysis_data()

    if df is None:
        st.info(
            "📂 No dataset is available yet. Analyze YouTube comments, "
            "analyze text, or upload a CSV file first."
        )

        if st.button("📂 Go to CSV Upload"):
            st.session_state["navigation_page"] = "📂 CSV Upload"
            st.rerun()

        return

    data = df.copy()

    sentiment_column = find_column(
        data,
        [
            "sentiment",
            "predicted_sentiment",
            "sentiment_label",
            "sentiment_result",
            "polarity",
        ],
    )

    emotion_column = find_column(
        data,
        [
            "emotion",
            "predicted_emotion",
            "emotion_label",
            "dominant_emotion",
        ],
    )

    text_column = find_text_column(data)

    # ------------------------------------------------------
    # SOURCE
    # ------------------------------------------------------

    video = st.session_state.get("video_details")

    if isinstance(video, dict) and video.get("title"):
        source = str(video["title"])
    else:
        source = str(
            st.session_state.get(
                "csv_filename",
                st.session_state.get("uploaded_filename", "Current Analysis"),
            )
        )

    total = len(data)

    st.subheader("📋 Report Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Total Records", f"{total:,}")
    col2.metric("📑 Total Columns", f"{len(data.columns):,}")
    col3.metric(
        "📝 Text Column",
        str(text_column) if text_column is not None else "Not detected",
    )

    st.info(f"**Report source:** {source}")

    # ------------------------------------------------------
    # SENTIMENT SUMMARY
    # ------------------------------------------------------

    positive = 0
    neutral = 0
    negative = 0
    unknown = 0
    dominant_sentiment = "Unavailable"

    normalized_sentiment = None

    if sentiment_column is not None:

        normalized_sentiment = (
            data[sentiment_column]
            .apply(normalize_sentiment)
        )

        positive = int((normalized_sentiment == "Positive").sum())
        neutral = int((normalized_sentiment == "Neutral").sum())
        negative = int((normalized_sentiment == "Negative").sum())
        unknown = int(
            (~normalized_sentiment.isin(
                ["Positive", "Neutral", "Negative"]
            )).sum()
        )

        known = normalized_sentiment[
            normalized_sentiment.isin(
                ["Positive", "Neutral", "Negative"]
            )
        ]

        if not known.empty:
            dominant_sentiment = known.value_counts().idxmax()

        st.divider()
        st.subheader("😊 Sentiment Summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Positive",
            f"{positive / total * 100:.1f}%" if total else "0%",
            f"{positive:,} records",
        )

        c2.metric(
            "Neutral",
            f"{neutral / total * 100:.1f}%" if total else "0%",
            f"{neutral:,} records",
        )

        c3.metric(
            "Negative",
            f"{negative / total * 100:.1f}%" if total else "0%",
            f"{negative:,} records",
        )

        c4.metric("Other / Unknown", f"{unknown:,}")

        sentiment_df = pd.DataFrame({
            "Sentiment": ["Positive", "Neutral", "Negative", "Other / Unknown"],
            "Records": [positive, neutral, negative, unknown],
        })

        left, right = st.columns(2)

        with left:
            st.markdown("#### Sentiment Distribution")

            nonzero = sentiment_df[sentiment_df["Records"] > 0]

            if not nonzero.empty:
                fig = px.pie(
                    nonzero,
                    names="Sentiment",
                    values="Records",
                    hole=0.45,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
            else:
                st.info("No sentiment records are available.")

        with right:
            st.markdown("#### Sentiment Comparison")

            fig = px.bar(
                sentiment_df,
                x="Sentiment",
                y="Records",
                text="Records",
            )

            fig.update_layout(showlegend=False)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    else:
        st.warning(
            "No recognized sentiment column was found. "
            "This report will still include dataset information and "
            "text-based topic analysis, but sentiment charts will be omitted."
        )

    # ------------------------------------------------------
    # EMOTION SUMMARY
    # ------------------------------------------------------

    dominant_emotion = "Unavailable"
    emotions = pd.Series(dtype="object")

    if emotion_column is not None:

        emotions = (
            data[emotion_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.title()
        )

        emotions = emotions[
            ~emotions.isin(
                ["", "Nan", "None", "Null", "Unknown", "N/A", "Na"]
            )
        ]

    st.divider()
    st.subheader("🎭 Emotion Summary")

    if not emotions.empty:

        emotion_counts = emotions.value_counts()
        dominant_emotion = str(emotion_counts.index[0])

        c1, c2 = st.columns(2)

        c1.metric("Dominant Emotion", dominant_emotion)
        c2.metric("Records with Emotion", f"{len(emotions):,}")

        emotion_df = (
            emotion_counts
            .head(10)
            .rename_axis("Emotion")
            .reset_index(name="Records")
        )

        fig = px.bar(
            emotion_df.sort_values("Records"),
            x="Records",
            y="Emotion",
            orientation="h",
            text="Records",
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info("No usable emotion column or emotion labels were found.")

    # ------------------------------------------------------
    # DISCUSSION TOPICS
    # ------------------------------------------------------

    st.divider()
    st.subheader("🔥 Top Discussion Topics")

    topics = get_topics(data, text_column)

    if topics:

        topics_df = pd.DataFrame(
            topics,
            columns=["Topic", "Mentions"],
        )

        fig = px.bar(
            topics_df.sort_values("Mentions"),
            x="Mentions",
            y="Topic",
            orientation="h",
            text="Mentions",
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        st.dataframe(
            topics_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "No meaningful discussion topics could be extracted "
            "from the detected text column."
        )

    # ------------------------------------------------------
    # MODEL EVALUATION
    # ------------------------------------------------------

    metrics = load_metrics()

    if metrics:

        st.divider()
        st.subheader("🧪 Model Evaluation")

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Accuracy", fmt(metric(metrics, "accuracy")))
        m2.metric("Precision", fmt(metric(metrics, "precision")))
        m3.metric("Recall", fmt(metric(metrics, "recall")))
        m4.metric("Weighted F1", fmt(metric(metrics, "f1")))

        st.caption(
            "These values are loaded from the project's saved evaluation "
            "metrics and may not describe the current uploaded dataset."
        )

    # ------------------------------------------------------
    # DATA PREVIEW
    # ------------------------------------------------------

    st.divider()
    st.subheader("📋 Analyzed Records")

    with st.expander("Preview analyzed records", expanded=False):

        st.dataframe(
            data.head(100),
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # DOWNLOAD CSV
    # ------------------------------------------------------

    st.divider()
    st.subheader("⬇️ Download Reports")

    csv_bytes = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📊 Download Full Analysis Data (CSV)",
        data=csv_bytes,
        file_name="social_media_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ------------------------------------------------------
    # DOWNLOAD SUMMARY
    # ------------------------------------------------------

    summary_rows = [
        {"Metric": "Source", "Value": source},
        {"Metric": "Total Records", "Value": total},
        {"Metric": "Total Columns", "Value": len(data.columns)},
        {"Metric": "Sentiment Column", "Value": str(sentiment_column or "Unavailable")},
        {"Metric": "Emotion Column", "Value": str(emotion_column or "Unavailable")},
        {"Metric": "Text Column", "Value": str(text_column or "Unavailable")},
        {"Metric": "Positive Records", "Value": positive},
        {"Metric": "Neutral Records", "Value": neutral},
        {"Metric": "Negative Records", "Value": negative},
        {"Metric": "Unknown Sentiment Records", "Value": unknown},
        {"Metric": "Dominant Sentiment", "Value": dominant_sentiment},
        {"Metric": "Dominant Emotion", "Value": dominant_emotion},
    ]

    summary_df = pd.DataFrame(summary_rows)

    st.download_button(
        "📝 Download Report Summary (CSV)",
        data=summary_df.to_csv(index=False).encode("utf-8"),
        file_name="analysis_report_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ------------------------------------------------------
    # PDF REPORT
    # ------------------------------------------------------

    pdf_bytes = build_pdf(
        data=data,
        source=source,
        total=total,
        positive=positive,
        neutral=neutral,
        negative=negative,
        dominant_sentiment=dominant_sentiment,
        dominant_emotion=dominant_emotion,
        topics=topics,
        metrics=metrics,
    )

    if pdf_bytes is not None:
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name="social_media_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.caption(
            "For PDF downloads, install ReportLab using: "
            "`pip install reportlab`"
        )


# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================

show_reports = show
