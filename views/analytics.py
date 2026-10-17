
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from services.explanation_service import (
    add_row_explanations,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(dataframe, possible_names):
    lookup = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }

    for name in possible_names:
        if name in lookup:
            return lookup[name]

    return None


def find_text_column(dataframe):
    preferred = [
        "text", "comment", "comments", "review",
        "feedback", "message", "content", "tweet",
        "post", "description",
    ]

    column = find_column(dataframe, preferred)

    if column is not None:
        return column

    for name in dataframe.columns:
        if dataframe[name].dtype == "object":
            return name

    return None


def safe_text(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def normalize_sentiment(value):
    value = safe_text(value).lower()

    if value in {"positive", "pos", "label_2"}:
        return "Positive"

    if value in {"negative", "neg", "label_0"}:
        return "Negative"

    if value in {"neutral", "neu", "label_1"}:
        return "Neutral"

    return "Unknown"


def safe_percentage(value):
    try:
        value = float(value)

        if pd.isna(value):
            return None

        if 0 <= value <= 1:
            value *= 100

        return value

    except (TypeError, ValueError):
        return None


def count_evidence(dataframe, sentiment):
    counts = {}

    rows = dataframe[
        dataframe["analytics_sentiment"] == sentiment
    ]

    for evidence in rows["evidence_phrases"].fillna(""):
        for phrase in str(evidence).split(","):
            phrase = phrase.strip().lower()

            if phrase:
                counts[phrase] = counts.get(phrase, 0) + 1

    return sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )


# ============================================================
# ANALYTICS PAGE
# ============================================================

def show():
    st.title("📊 Social Media Analytics")
    st.caption(
        "Understand what people feel, why they feel it, "
        "and which comments need attention."
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    analysis_df = st.session_state.get("analysis_df")

    if analysis_df is None:
        st.info(
            "No analysis data is available yet. "
            "Analyze comments in YouTube Analyzer, "
            "Text Analyzer, or CSV Upload first."
        )
        return

    if not isinstance(analysis_df, pd.DataFrame):
        st.error(
            "The saved analysis data is not a valid DataFrame. "
            "Please run the analysis again."
        )
        return

    if analysis_df.empty:
        st.info(
            "The analysis dataset is empty. "
            "Run an analysis first, then return here."
        )
        return

    original_df = analysis_df.copy()

    sentiment_col = find_column(
        original_df,
        [
            "sentiment",
            "predicted_sentiment",
            "sentiment_label",
        ],
    )

    text_col = find_text_column(original_df)

    emotion_col = find_column(
        original_df,
        ["emotion", "predicted_emotion"],
    )

    sentiment_score_col = find_column(
        original_df,
        [
            "sentiment_score",
            "sentiment_confidence",
            "confidence",
            "sentiment_probability",
        ],
    )

    emotion_score_col = find_column(
        original_df,
        ["emotion_score", "emotion_confidence"],
    )

    if sentiment_col is None:
        st.error(
            "No sentiment column was found in the analysis data. "
            f"Available columns: {', '.join(map(str, original_df.columns))}"
        )
        return

    if text_col is None:
        st.error(
            "No text/comment column was found. "
            f"Available columns: {', '.join(map(str, original_df.columns))}"
        )
        return

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    data = original_df.copy()

    data["analytics_text"] = data[text_col].apply(safe_text)

    data["analytics_sentiment"] = data[
        sentiment_col
    ].apply(normalize_sentiment)

    if emotion_col:
        data["analytics_emotion"] = data[
            emotion_col
        ].apply(
            lambda value: safe_text(value).title() or "Unknown"
        )
    else:
        data["analytics_emotion"] = "Unknown"

    # Generate explanations if they are missing.
    if (
        "sentiment_explanation" not in data.columns
        or "evidence_phrases" not in data.columns
    ):
        data = add_row_explanations(
            data,
            text_col=text_col,
            sentiment_col=sentiment_col,
            sentiment_score_col=(
                sentiment_score_col or "sentiment_score"
            ),
            emotion_col=emotion_col or "emotion",
            emotion_score_col=(
                emotion_score_col or "emotion_score"
            ),
        )

    for column in [
        "sentiment_explanation",
        "evidence_phrases",
        "emotion_explanation",
    ]:
        if column not in data.columns:
            data[column] = ""

    source_name = (
        st.session_state.get("youtube_title")
        or st.session_state.get("csv_filename")
        or "Current analysis"
    )

    st.caption(f"Analysis source: {source_name}")

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    st.subheader("Overall Sentiment")

    total = len(data)

    positive = int(
        (data["analytics_sentiment"] == "Positive").sum()
    )
    negative = int(
        (data["analytics_sentiment"] == "Negative").sum()
    )
    neutral = int(
        (data["analytics_sentiment"] == "Neutral").sum()
    )
    unknown = total - positive - negative - neutral

    def pct(count):
        return count / total * 100 if total else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Comments", f"{total:,}")
    c2.metric("😊 Positive", f"{positive:,}", f"{pct(positive):.1f}%")
    c3.metric("😠 Negative", f"{negative:,}", f"{pct(negative):.1f}%")
    c4.metric("😐 Neutral", f"{neutral:,}", f"{pct(neutral):.1f}%")

    if unknown:
        st.caption(
            f"{unknown:,} records have unknown sentiment labels."
        )

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    st.divider()
    st.subheader("Sentiment Distribution")

    chart_df = pd.DataFrame({
        "Sentiment": ["Positive", "Negative", "Neutral"],
        "Count": [positive, negative, neutral],
    })

    chart_df = chart_df[chart_df["Count"] > 0]

    if not chart_df.empty:
        left, right = st.columns(2)

        colors = {
            "Positive": "#16A34A",
            "Negative": "#DC2626",
            "Neutral": "#CA8A04",
        }

        with left:
            fig = px.pie(
                chart_df,
                names="Sentiment",
                values="Count",
                hole=0.5,
                color="Sentiment",
                color_discrete_map=colors,
                title="Sentiment Share",
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                chart_df,
                x="Sentiment",
                y="Count",
                color="Sentiment",
                color_discrete_map=colors,
                text="Count",
                title="Comments by Sentiment",
            )
            fig.update_layout(
                height=350,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # WHY EACH SENTIMENT?
    # --------------------------------------------------------

    st.divider()
    st.subheader("Why Are People Feeling This Way?")

    st.caption(
        "These explanations use phrases found in the comments. "
        "They are supporting clues, not proof of the model's "
        "internal reasoning."
    )

    reason_columns = st.columns(3)

    for column, label, emoji, count in zip(
        reason_columns,
        ["Positive", "Negative", "Neutral"],
        ["😊", "😠", "😐"],
        [positive, negative, neutral],
    ):
        with column:
            st.markdown(f"### {emoji} {label}")
            st.metric("Comments", count)

            reasons = count_evidence(data, label)[:5]

            if reasons:
                st.markdown("**Common evidence phrases**")

                for phrase, frequency in reasons:
                    st.write(
                        f'• "{phrase}" — {frequency} comment(s)'
                    )

            elif label == "Neutral":
                st.write(
                    "Neutral feedback may be factual, ambiguous, "
                    "or mixed. Inspect individual comments "
                    "to understand their context."
                )
            else:
                st.write(
                    "No matching evidence phrases were detected. "
                    "Review the original comments for context."
                )

    # --------------------------------------------------------
    # COMMENT EXPLORER
    # --------------------------------------------------------

    st.divider()
    st.subheader("Inspect Individual Comments")

    filter_col, search_col = st.columns([1, 2])

    with filter_col:
        selected_sentiment = st.selectbox(
            "Filter sentiment",
            ["All", "Negative", "Positive", "Neutral", "Unknown"],
        )

    with search_col:
        search_query = st.text_input(
            "Search comments",
            placeholder="Enter a word or phrase...",
        )

    filtered = data.copy()

    if selected_sentiment != "All":
        filtered = filtered[
            filtered["analytics_sentiment"] == selected_sentiment
        ]

    if search_query.strip():
        filtered = filtered[
            filtered["analytics_text"].str.contains(
                search_query.strip(),
                case=False,
                regex=False,
                na=False,
            )
        ]

    st.caption(f"{len(filtered):,} matching comments")

    if filtered.empty:
        st.info("No comments match the selected filters.")
    else:
        page_size = 10
        page_count = max(
            1,
            (len(filtered) + page_size - 1) // page_size,
        )

        page = st.number_input(
            "Page",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
            key="analytics_page_number",
        )

        start = (page - 1) * page_size
        current_page = filtered.iloc[start:start + page_size]

        for _, row in current_page.iterrows():
            sentiment = row["analytics_sentiment"]
            comment = row["analytics_text"]

            emoji = {
                "Positive": "😊",
                "Negative": "😠",
                "Neutral": "😐",
            }.get(sentiment, "❔")

            heading = f"{emoji} {sentiment} — {comment[:80]}"

            with st.expander(heading):
                st.markdown("**Original Comment**")
                st.write(comment or "(No text available)")

                st.markdown("**Predicted Sentiment**")
                st.write(sentiment)

                st.markdown("**Why this sentiment?**")
                explanation = safe_text(
                    row.get("sentiment_explanation", "")
                )

                st.write(
                    explanation
                    or "No explanation is available for this record."
                )

                st.markdown("**Evidence Phrases**")
                evidence = safe_text(
                    row.get("evidence_phrases", "")
                )

                if evidence:
                    for phrase in evidence.split(","):
                        phrase = phrase.strip()
                        if phrase:
                            st.markdown(f"- `{phrase}`")
                else:
                    st.write(
                        "No matching evidence phrase was detected."
                    )

                if sentiment_score_col:
                    score = safe_percentage(
                        row.get(sentiment_score_col)
                    )

                    if score is not None:
                        st.caption(
                            f"Model-reported score: {score:.1f}%"
                        )

                st.markdown("**Predicted Emotion**")
                st.write(
                    safe_text(
                        row.get("analytics_emotion", "Unknown")
                    ) or "Unknown"
                )

                emotion_explanation = safe_text(
                    row.get("emotion_explanation", "")
                )

                if emotion_explanation:
                    st.markdown("**Emotion Explanation**")
                    st.write(emotion_explanation)

                if emotion_score_col:
                    score = safe_percentage(
                        row.get(emotion_score_col)
                    )

                    if score is not None:
                        st.caption(
                            f"Emotion model-reported score: {score:.1f}%"
                        )

    # --------------------------------------------------------
    # EMOTION DISTRIBUTION
    # --------------------------------------------------------

    st.divider()
    st.subheader("Emotion Distribution")

    emotion_data = data[
        data["analytics_emotion"].str.lower() != "unknown"
    ]

    if emotion_data.empty:
        st.info(
            "No emotion labels are available for this analysis."
        )
    else:
        emotion_counts = (
            emotion_data["analytics_emotion"]
            .value_counts()
            .rename_axis("Emotion")
            .reset_index(name="Count")
        )

        fig = px.bar(
            emotion_counts,
            x="Emotion",
            y="Count",
            color="Emotion",
            text="Count",
            title="Detected Emotions",
        )
        fig.update_layout(height=370, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # MODEL SCORE OVERVIEW
    # --------------------------------------------------------

    if sentiment_score_col:
        st.divider()
        st.subheader("Model Score Overview")

        scores = data[sentiment_score_col].apply(safe_percentage)
        scores = scores.dropna()

        if not scores.empty:
            c1, c2 = st.columns(2)
            c1.metric("Average Score", f"{scores.mean():.1f}%")
            c2.metric("Median Score", f"{scores.median():.1f}%")

            st.caption(
                "A model score is not necessarily a calibrated "
                "probability that the prediction is correct."
            )

    # --------------------------------------------------------
    # MODEL EVALUATION METRICS
    # --------------------------------------------------------

    with st.expander("Model Evaluation Metrics"):
        metrics_path = (
            Path(__file__).resolve().parents[1]
            / "evaluation"
            / "evaluation_metrics.csv"
        )

        if metrics_path.exists():
            try:
                metrics_df = pd.read_csv(metrics_path)
                st.dataframe(
                    metrics_df,
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception as error:
                st.warning(f"Could not load metrics: {error}")
        else:
            st.info(
                "No evaluation_metrics.csv file was found "
                "in the evaluation folder."
            )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.divider()
    st.subheader("Download Analysis")

    download_df = filtered.copy()

    download_df["Analyzed Text"] = download_df["analytics_text"]
    download_df["Analyzed Sentiment"] = (
        download_df["analytics_sentiment"]
    )
    download_df["Analyzed Emotion"] = (
        download_df["analytics_emotion"]
    )

    st.download_button(
        "⬇️ Download filtered results with explanations",
        data=download_df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="social_media_sentiment_explanations.csv",
        mime="text/csv",
        use_container_width=True,
    )

    all_download_df = data.copy()

    all_download_df["Analyzed Text"] = (
        all_download_df["analytics_text"]
    )
    all_download_df["Analyzed Sentiment"] = (
        all_download_df["analytics_sentiment"]
    )
    all_download_df["Analyzed Emotion"] = (
        all_download_df["analytics_emotion"]
    )

    st.download_button(
        "⬇️ Download complete analysis",
        data=all_download_df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="complete_social_media_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )
