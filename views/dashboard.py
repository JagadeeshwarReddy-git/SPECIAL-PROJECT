
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================================
# CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / "evaluation" / "evaluation_metrics.csv"


# ==========================================================
# SHARED DATA
# ==========================================================

def get_shared_analysis_data():
    """Load the dataset shared by the application's analysis pages."""

    for key in ("analysis_df", "universal_analysis_df", "df"):
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


def find_column(df, names):
    """Find a column without depending on capitalization or spaces."""

    columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in names:
        if name.lower() in columns:
            return columns[name.lower()]

    return None


# ==========================================================
# SENTIMENT HELPERS
# ==========================================================

def normalize_sentiment(value):
    value = str(value).strip().lower()

    mapping = {
        "positive": "Positive",
        "pos": "Positive",
        "good": "Positive",
        "happy": "Positive",
        "favorable": "Positive",
        "favourable": "Positive",
        "negative": "Negative",
        "neg": "Negative",
        "bad": "Negative",
        "angry": "Negative",
        "unfavorable": "Negative",
        "unfavourable": "Negative",
        "neutral": "Neutral",
        "neu": "Neutral",
        "unknown": "Unknown",
        "nan": "Unknown",
        "none": "Unknown",
        "null": "Unknown",
        "": "Unknown",
    }

    return mapping.get(value, value.title())


def format_percent(value):
    try:
        value = float(value)

        if pd.isna(value):
            return "—"

        return f"{value:.2f}%"

    except (TypeError, ValueError):
        return "—"


# ==========================================================
# OPTIONAL MODEL METRICS
# ==========================================================

def load_model_metrics():
    """Read evaluation metrics if the project has an exported CSV."""

    if not METRICS_FILE.exists():
        return {}

    try:
        metrics_df = pd.read_csv(METRICS_FILE)
        metrics = {}

        for _, row in metrics_df.iterrows():
            if len(row) < 2:
                continue

            key = str(row.iloc[0]).strip().lower()

            try:
                value = float(row.iloc[1])
            except (TypeError, ValueError):
                continue

            if pd.notna(value):
                metrics[key] = value

        return metrics

    except Exception:
        return {}


# ==========================================================
# STYLING
# ==========================================================

def apply_dashboard_styles():
    st.markdown(
        """
        <style>
        .dashboard-heading {
            font-size: 32px;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .dashboard-subheading {
            opacity: 0.75;
            font-size: 14px;
            margin-bottom: 20px;
        }

        .dashboard-card {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 14px;
            padding: 18px;
            background: var(--secondary-background-color);
            min-height: 115px;
        }

        .dashboard-card-label {
            font-size: 13px;
            opacity: .75;
            margin-bottom: 8px;
        }

        .dashboard-card-value {
            font-size: 27px;
            font-weight: 750;
            overflow-wrap: anywhere;
        }

        .dashboard-card-caption {
            font-size: 12px;
            opacity: .75;
            margin-top: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, caption="", emoji=""):
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-card-label">
                {emoji} {label}
            </div>
            <div class="dashboard-card-value">{value}</div>
            <div class="dashboard-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# EMPTY STATE
# ==========================================================

def render_empty_state():
    st.title("📊 Analytics Dashboard")

    st.info(
        "No analysis dataset is available yet. "
        "Upload a CSV file or analyze text first."
    )

    if st.button("📂 Go to CSV Upload"):
        st.session_state["page"] = "📂 CSV Upload"
        st.rerun()


# ==========================================================
# MAIN DASHBOARD
# ==========================================================

def show():

    apply_dashboard_styles()

    st.markdown(
        '<div class="dashboard-heading">📊 Analytics Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dashboard-subheading">
            Explore your uploaded data, sentiment distribution,
            emotions, and audience feedback.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    df = get_shared_analysis_data()

    if df is None:
        render_empty_state()
        return

    total_records = len(df)
    total_columns = len(df.columns)

    # ------------------------------------------------------
    # DETECT COLUMNS
    # ------------------------------------------------------

    sentiment_column = find_column(
        df,
        [
            "sentiment",
            "predicted_sentiment",
            "sentiment_label",
            "sentiment_result",
            "polarity",
        ],
    )

    emotion_column = find_column(
        df,
        [
            "emotion",
            "predicted_emotion",
            "emotion_label",
            "dominant_emotion",
        ],
    )

    text_column = find_column(
        df,
        [
            "text",
            "comment",
            "comments",
            "review",
            "reviews",
            "message",
            "content",
            "description",
            "feedback",
        ],
    )

    # ------------------------------------------------------
    # GLOBAL FILTERS
    # ------------------------------------------------------

    with st.expander("🔎 Filter Dashboard Data", expanded=False):

        filtered_df = df.copy()

        if sentiment_column:
            sentiment_options = sorted(
                filtered_df[sentiment_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_sentiments = st.multiselect(
                "Filter by sentiment",
                options=sentiment_options,
                default=sentiment_options,
                key="dashboard_sentiment_filter",
            )

            filtered_df = filtered_df[
                filtered_df[sentiment_column]
                .fillna("")
                .astype(str)
                .isin(selected_sentiments)
            ]

        if text_column:
            search_text = st.text_input(
                "Search comments or text",
                placeholder="Enter a word or phrase...",
                key="dashboard_text_search",
            )

            if search_text.strip():
                filtered_df = filtered_df[
                    filtered_df[text_column]
                    .fillna("")
                    .astype(str)
                    .str.contains(
                        search_text.strip(),
                        case=False,
                        regex=False,
                    )
                ]

    data = filtered_df.copy()
    displayed_records = len(data)

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    st.subheader("📌 Dataset Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Records",
            f"{total_records:,}",
            "All uploaded records",
            "📄",
        )

    with c2:
        metric_card(
            "Filtered Records",
            f"{displayed_records:,}",
            "Records matching filters",
            "🔎",
        )

    with c3:
        metric_card(
            "Columns",
            f"{total_columns:,}",
            "Dataset features",
            "📊",
        )

    with c4:
        metric_card(
            "Sentiment Analysis",
            "Available" if sentiment_column else "Not Available",
            sentiment_column or "No sentiment column detected",
            "😊",
        )

    st.divider()

    # ------------------------------------------------------
    # SENTIMENT ANALYSIS
    # ------------------------------------------------------

    if sentiment_column:

        st.subheader("😊 Sentiment Analysis")

        data["dashboard_sentiment"] = (
            data[sentiment_column].apply(normalize_sentiment)
        )

        sentiment_counts = (
            data["dashboard_sentiment"]
            .value_counts()
            .reindex(
                ["Positive", "Neutral", "Negative", "Unknown"],
                fill_value=0,
            )
        )

        known_count = int(
            sentiment_counts[["Positive", "Neutral", "Negative"]].sum()
        )

        positive = int(sentiment_counts["Positive"])
        neutral = int(sentiment_counts["Neutral"])
        negative = int(sentiment_counts["Negative"])
        unknown = int(sentiment_counts["Unknown"])

        positive_pct = positive / displayed_records * 100 if displayed_records else 0
        neutral_pct = neutral / displayed_records * 100 if displayed_records else 0
        negative_pct = negative / displayed_records * 100 if displayed_records else 0

        s1, s2, s3, s4 = st.columns(4)

        s1.metric("😊 Positive", f"{positive_pct:.1f}%", f"{positive:,} records")
        s2.metric("😐 Neutral", f"{neutral_pct:.1f}%", f"{neutral:,} records")
        s3.metric("😟 Negative", f"{negative_pct:.1f}%", f"{negative:,} records")
        s4.metric("❔ Unknown", f"{unknown:,}")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### Sentiment Distribution")

            sentiment_chart = sentiment_counts[
                sentiment_counts > 0
            ].rename_axis("Sentiment").reset_index(name="Records")

            if not sentiment_chart.empty:
                fig = px.pie(
                    sentiment_chart,
                    names="Sentiment",
                    values="Records",
                    hole=0.48,
                )

                fig.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend_title_text="Sentiment",
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("No sentiment values are available for the selected filters.")

        with chart_col2:
            st.markdown("#### Sentiment Comparison")

            sentiment_bar = sentiment_counts.rename_axis(
                "Sentiment"
            ).reset_index(name="Records")

            fig = px.bar(
                sentiment_bar,
                x="Sentiment",
                y="Records",
                text="Records",
            )

            fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=30, b=10),
            )

            st.plotly_chart(fig, use_container_width=True)

        valid_sentiments = sentiment_counts[
            ["Positive", "Neutral", "Negative"]
        ]

        if known_count > 0:
            dominant_sentiment = valid_sentiments.idxmax()

            st.info(
                f"**Dominant sentiment:** {dominant_sentiment}. "
                f"There are {known_count:,} records with recognized "
                "sentiment labels in the filtered dataset."
            )
        else:
            st.warning(
                "No recognized positive, neutral, or negative sentiment "
                "labels were found in the filtered dataset."
            )

    else:
        st.warning(
            "This dataset does not contain a recognized sentiment column. "
            "General dataset analysis is available, but sentiment charts "
            "require sentiment labels."
        )

    st.divider()

    # ------------------------------------------------------
    # EMOTION ANALYSIS
    # ------------------------------------------------------

    if emotion_column:

        st.subheader("🎭 Emotion Analysis")

        emotion_values = (
            data[emotion_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.title()
        )

        emotion_values = emotion_values[
            ~emotion_values.isin(
                ["", "Unknown", "Nan", "None", "Null", "N/A", "Na"]
            )
        ]

        emotion_counts = emotion_values.value_counts()

        if not emotion_counts.empty:

            emotion_col1, emotion_col2 = st.columns(2)

            with emotion_col1:
                st.metric(
                    "Dominant Emotion",
                    emotion_counts.index[0],
                )

            with emotion_col2:
                st.metric(
                    "Records with Emotion",
                    f"{int(emotion_counts.sum()):,}",
                )

            emotion_chart = emotion_counts.rename_axis(
                "Emotion"
            ).reset_index(name="Records")

            fig = px.bar(
                emotion_chart,
                x="Emotion",
                y="Records",
                text="Records",
                title="Emotion Distribution",
            )

            fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=45, b=10),
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No usable emotion values were found.")

    # ------------------------------------------------------
    # TEXT ANALYSIS
    # ------------------------------------------------------

    if text_column:

        st.divider()
        st.subheader("📝 Text Analysis")

        text_values = (
            data[text_column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        text_values = text_values[text_values != ""]

        t1, t2, t3 = st.columns(3)

        t1.metric("Text Records", f"{len(text_values):,}")

        average_length = (
            text_values.str.len().mean()
            if not text_values.empty
            else 0
        )

        t2.metric("Average Text Length", f"{average_length:.1f} characters")

        total_characters = int(text_values.str.len().sum())
        t3.metric("Total Characters", f"{total_characters:,}")

        with st.expander("Preview Text Records"):
            preview_df = data[[text_column]].copy()

            if sentiment_column and sentiment_column != text_column:
                preview_df[sentiment_column] = data[sentiment_column]

            st.dataframe(
                preview_df.head(100),
                use_container_width=True,
                hide_index=True,
            )

    # ------------------------------------------------------
    # FULL DATASET
    # ------------------------------------------------------

    st.divider()
    st.subheader("📋 Dataset Records")

    st.caption(
        f"Displaying {displayed_records:,} filtered records "
        f"out of {total_records:,} total records."
    )

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇️ Download Filtered Dataset",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="dashboard_filtered_data.csv",
        mime="text/csv",
        key="dashboard_download_filtered",
    )

    # ------------------------------------------------------
    # MODEL EVALUATION METRICS
    # ------------------------------------------------------

    metrics = load_model_metrics()

    if metrics:
        st.divider()
        st.subheader("🤖 Model Evaluation Metrics")

        metrics_df = pd.DataFrame(
            [
                {
                    "Metric": key.replace("_", " ").title(),
                    "Value": value,
                }
                for key, value in metrics.items()
            ]
        )

        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # EXPORT SUMMARY
    # ------------------------------------------------------

    st.divider()
    st.subheader("⬇️ Download Dashboard Summary")

    summary = {
        "total_records": total_records,
        "filtered_records": displayed_records,
        "total_columns": total_columns,
        "sentiment_column": str(sentiment_column or "Not available"),
        "emotion_column": str(emotion_column or "Not available"),
        "text_column": str(text_column or "Not available"),
    }

    if sentiment_column:
        summary.update(
            {
                "positive_records": positive,
                "neutral_records": neutral,
                "negative_records": negative,
                "unknown_records": unknown,
                "positive_percentage": round(positive_pct, 2),
                "neutral_percentage": round(neutral_pct, 2),
                "negative_percentage": round(negative_pct, 2),
            }
        )

    summary_df = pd.DataFrame(
        [{"Metric": key, "Value": value} for key, value in summary.items()]
    )

    st.download_button(
        "⬇️ Download Summary (CSV)",
        data=summary_df.to_csv(index=False).encode("utf-8"),
        file_name="dashboard_summary.csv",
        mime="text/csv",
        key="dashboard_download_summary",
    )


# ==========================================================
# COMPATIBILITY ALIAS
# ==========================================================

show_dashboard = show
