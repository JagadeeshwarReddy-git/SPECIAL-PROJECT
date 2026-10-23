
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ==========================================================
# CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / "evaluation" / "evaluation_metrics.csv"


# ==========================================================
# HELPERS
# ==========================================================

def normalize_sentiment(value):
    value = str(value).strip().lower()

    mapping = {
        "positive": "Positive",
        "pos": "Positive",
        "negative": "Negative",
        "neg": "Negative",
        "neutral": "Neutral",
        "neu": "Neutral",
        "unknown": "Unknown",
        "nan": "Unknown",
        "none": "Unknown",
    }

    return mapping.get(value, value.title())


def format_percent(value):
    try:
        value = float(value)
        if pd.isna(value):
            return "—"

        if 0 <= value <= 1:
            value *= 100

        return f"{value:.2f}%"
    except (TypeError, ValueError):
        return "—"


def load_model_metrics():
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


def find_metric(metrics, keyword):
    for key, value in metrics.items():
        if keyword in key:
            return value
    return None


def apply_dashboard_styles():
    st.markdown(
        """
        <style>
        .dashboard-heading {
            font-size: 32px;
            font-weight: 760;
            letter-spacing: -1px;
            margin-bottom: 4px;
        }

        .dashboard-subheading {
            opacity: .72;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 24px;
        }

        .dashboard-section {
            font-size: 21px;
            font-weight: 720;
            letter-spacing: -.3px;
            margin-top: 26px;
            margin-bottom: 12px;
        }

        .dashboard-card {
            border: 1px solid rgba(128,128,128,.24);
            border-radius: 15px;
            padding: 17px;
            background: var(--secondary-background-color);
            min-height: 116px;
            overflow-wrap: anywhere;
        }

        .dashboard-card-label {
            font-size: 12px;
            opacity: .72;
            margin-bottom: 10px;
        }

        .dashboard-card-value {
            font-size: 27px;
            font-weight: 750;
            letter-spacing: -.6px;
        }

        .dashboard-card-caption {
            font-size: 12px;
            opacity: .72;
            margin-top: 7px;
        }

        .dashboard-insight {
            border: 1px solid rgba(128,128,128,.24);
            border-radius: 13px;
            padding: 15px;
            background: var(--secondary-background-color);
            min-height: 95px;
        }

        .dashboard-insight-title {
            font-size: 12px;
            opacity: .7;
            margin-bottom: 7px;
        }

        .dashboard-insight-value {
            font-size: 18px;
            font-weight: 700;
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


def section(title, subtitle=None):
    st.markdown(
        f'<div class="dashboard-section">{title}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def style_chart(fig, height=330):
    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=55, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(size=16),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    return fig


def render_empty_state():
    st.markdown(
        '<div class="dashboard-heading">📊 Analytics Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dashboard-subheading">
            Your social media analytics, presented clearly.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "No analysis results are available yet. "
        "Run an analysis in YouTube Analyzer, Text Analyzer, "
        "or CSV Upload to populate your dashboard."
    )

    st.markdown("### Get started")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**▶️ YouTube Analyzer**")
        st.caption("Analyze comments from a YouTube video.")

    with col2:
        st.markdown("**📝 Text Analyzer**")
        st.caption("Analyze an individual text or comment.")

    with col3:
        st.markdown("**📂 CSV Upload**")
        st.caption("Analyze an entire dataset.")


# ==========================================================
# MAIN DASHBOARD
# ==========================================================


# BRICK_1_UNIFIED_PLATFORM_OVERVIEW
# BRICK_6_CLICKABLE_PLATFORM_CARDS
def render_platform_overview():
    """Show platform status and navigate to tools from available cards."""
    platforms = [
        ("YouTube", "Available", "Existing project integration",
         "📺 YouTube Analyzer"),
        ("Text Analysis", "Available", "Analyze text",
         "📝 Text Analyzer"),
        ("CSV Upload", "Available", "Analyze uploaded datasets",
         "📂 CSV Upload"),
        ("Instagram", "Planned", "Authorized API integration required", None),
        ("Facebook", "Planned", "Authorized API integration required", None),
        ("X", "Planned", "Authorized API integration required", None),
        ("Reddit", "Planned", "API integration required", None),
        ("LinkedIn", "Planned", "Authorized API integration required", None),
        ("TikTok", "Planned", "Authorized API integration required", None),
    ]

    st.markdown("---")
    st.markdown("# Social Media Command Center")
    st.caption(
        "A unified overview of current analysis tools and future integrations."
    )

    available = sum(status == "Available" for _, status, _, _ in platforms)
    metrics = st.columns(3)
    metrics[0].metric("Platforms listed", len(platforms))
    metrics[1].metric("Available tools", available)
    metrics[2].metric("Planned integrations", len(platforms) - available)

    st.markdown("## Explore platforms")

    for start in range(0, len(platforms), 3):
        columns = st.columns(3)
        for column, (name, status, description, destination) in zip(
            columns, platforms[start:start + 3]
        ):
            with column:
                with st.container(border=True):
                    st.markdown(f"### {name}")

                    if status == "Available":
                        st.success(status)
                    else:
                        st.info(status)

                    st.caption(description)

                    if destination:
                        if st.button(
                            f"Open {name}",
                            key=f"platform_open_{name.lower().replace(' ', '_')}",
                            use_container_width=True,
                        ):
                            st.session_state["navigation_page"] = destination
                            st.rerun()
                    else:
                        st.button(
                            "Not connected",
                            key=f"platform_unavailable_{name.lower()}",
                            disabled=True,
                            use_container_width=True,
                        )

    st.markdown("---")


# BRICK_5_PREMIUM_LIGHT_STYLE
def apply_premium_light_style():
    """Apply premium light styling without changing analytics."""
    st.markdown("""
    <style>
    .stApp {
        background: #f6f8fc;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8faff);
        border: 1px solid #e3e9f4;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(28, 48, 86, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: #66748b;
        font-size: 0.88rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #172b4d;
        font-weight: 750;
        letter-spacing: -0.035em;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e3e9f4;
        border-radius: 16px;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3 {
        color: #172b4d;
        letter-spacing: -0.025em;
    }

    .stMarkdown h2 {
        margin-top: 1.25rem;
        margin-bottom: 0.65rem;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #7796d8;
        box-shadow: 0 3px 12px rgba(55, 94, 170, 0.10);
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid #e3e9f4;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

def show():
    apply_dashboard_styles()
    apply_premium_light_style()
    render_platform_overview()

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    df = st.session_state.get("analysis_df")

    if (
        df is None
        or not isinstance(df, pd.DataFrame)
        or df.empty
    ):
        render_empty_state()
        return

    if "sentiment" not in df.columns:
        st.title("📊 Analytics Dashboard")
        st.error(
            "The current analysis does not contain a sentiment column. "
            "Run the analysis again and check its output."
        )
        return

    data = df.copy()

    # ------------------------------------------------------
    # PREPARE SENTIMENT DATA
    # ------------------------------------------------------

    data["dashboard_sentiment"] = (
        data["sentiment"].apply(normalize_sentiment)
    )

    total_records = len(data)

    sentiment_counts = (
        data["dashboard_sentiment"]
        .value_counts()
    )

    positive = int(sentiment_counts.get("Positive", 0))
    neutral = int(sentiment_counts.get("Neutral", 0))
    negative = int(sentiment_counts.get("Negative", 0))
    unknown = int(sentiment_counts.get("Unknown", 0))

    positive_pct = positive / total_records * 100
    neutral_pct = neutral / total_records * 100
    negative_pct = negative / total_records * 100

    valid_sentiments = data[
        data["dashboard_sentiment"].isin(
            ["Positive", "Neutral", "Negative"]
        )
    ]

    dominant_sentiment = (
        valid_sentiments["dashboard_sentiment"].mode().iloc[0]
        if not valid_sentiments.empty
        else "Unknown"
    )

    # ------------------------------------------------------
    # PREPARE EMOTION DATA
    # ------------------------------------------------------

    if "emotion" in data.columns:
        data["dashboard_emotion"] = (
            data["emotion"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.title()
        )

        emotion_data = data[
            ~data["dashboard_emotion"].isin(
                ["", "Nan", "None", "Unknown"]
            )
        ]

        emotion_counts = (
            emotion_data["dashboard_emotion"]
            .value_counts()
            .rename_axis("Emotion")
            .reset_index(name="Records")
        )

    else:
        emotion_data = pd.DataFrame()
        emotion_counts = pd.DataFrame(
            columns=["Emotion", "Records"]
        )

    dominant_emotion = (
        emotion_counts.iloc[0]["Emotion"]
        if not emotion_counts.empty
        else "N/A"
    )

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    header_left, header_right = st.columns([4, 1])

    with header_left:
        st.markdown(
            '<div class="dashboard-heading">'
            '📊 Analytics Dashboard</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="dashboard-subheading">
                Understand audience sentiment, discover emotions,
                and explore the results of your latest analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_right:
        st.metric("Records analyzed", f"{total_records:,}")

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    section("Audience overview")

    k1, k2, k3, k4 = st.columns(4, gap="medium")

    with k1:
        metric_card(
            "Positive sentiment",
            f"{positive_pct:.1f}%",
            f"{positive:,} records",
            "😊",
        )

    with k2:
        metric_card(
            "Neutral sentiment",
            f"{neutral_pct:.1f}%",
            f"{neutral:,} records",
            "😐",
        )

    with k3:
        metric_card(
            "Negative sentiment",
            f"{negative_pct:.1f}%",
            f"{negative:,} records",
            "😟",
        )

    with k4:
        metric_card(
            "Dominant emotion",
            dominant_emotion,
            f"{int(emotion_counts.iloc[0]['Records']):,} records"
            if not emotion_counts.empty
            else "No emotion data",
            "🎭",
        )

    # ------------------------------------------------------
    # PRIMARY CHARTS
    # ------------------------------------------------------

    section(
        "Sentiment and emotions",
        "Explore how audience reactions are distributed.",
    )

    left, right = st.columns(2, gap="large")

    with left:
        sentiment_chart_df = pd.DataFrame(
            {
                "Sentiment": ["Positive", "Neutral", "Negative"],
                "Records": [positive, neutral, negative],
            }
        )

        fig_sentiment = px.pie(
            sentiment_chart_df,
            names="Sentiment",
            values="Records",
            hole=0.62,
            title="Sentiment distribution",
            color="Sentiment",
            color_discrete_map={
                "Positive": "#22c55e",
                "Neutral": "#f59e0b",
                "Negative": "#ef4444",
            },
        )

        fig_sentiment.update_traces(
            textinfo="percent",
            textposition="inside",
            hovertemplate=(
                "%{label}<br>"
                "Records: %{value}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

        if positive + neutral + negative == 0:
            st.info("No valid sentiment predictions are available.")
        else:
            st.plotly_chart(
                style_chart(fig_sentiment),
                use_container_width=True,
                key="dashboard_sentiment_donut",
            )

    with right:
        if not emotion_counts.empty:
            displayed_emotions = (
                emotion_counts
                .head(8)
                .sort_values("Records", ascending=True)
            )

            fig_emotions = px.bar(
                displayed_emotions,
                x="Records",
                y="Emotion",
                orientation="h",
                text="Records",
                title="Most common emotions",
                color="Records",
                color_continuous_scale="Blues",
            )

            fig_emotions.update_traces(
                textposition="outside",
                cliponaxis=False,
            )

            fig_emotions.update_layout(
                coloraxis_showscale=False,
                xaxis_title="Number of records",
                yaxis_title="",
            )

            st.plotly_chart(
                style_chart(fig_emotions),
                use_container_width=True,
                key="dashboard_emotion_bar",
            )
        else:
            st.info(
                "Emotion results are not available for this analysis."
            )

    # ------------------------------------------------------
    # AUDIENCE INSIGHTS
    # ------------------------------------------------------

    section("Key insights")

    insight1, insight2, insight3 = st.columns(3, gap="medium")

    if positive > negative:
        mood = "Mostly positive"
        mood_description = "Positive reactions outnumber negative ones."
    elif negative > positive:
        mood = "Mostly negative"
        mood_description = "Negative reactions outnumber positive ones."
    else:
        mood = "Balanced or tied"
        mood_description = (
            "Positive and negative counts are equal."
        )

    with insight1:
        st.markdown(
            f"""
            <div class="dashboard-insight">
                <div class="dashboard-insight-title">
                    Overall audience mood
                </div>
                <div class="dashboard-insight-value">{mood}</div>
                <div class="dashboard-card-caption">
                    {mood_description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight2:
        st.markdown(
            f"""
            <div class="dashboard-insight">
                <div class="dashboard-insight-title">
                    Leading sentiment
                </div>
                <div class="dashboard-insight-value">
                    {dominant_sentiment}
                </div>
                <div class="dashboard-card-caption">
                    Most frequent valid sentiment label.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight3:
        st.markdown(
            f"""
            <div class="dashboard-insight">
                <div class="dashboard-insight-title">
                    Unclassified records
                </div>
                <div class="dashboard-insight-value">
                    {unknown:,}
                </div>
                <div class="dashboard-card-caption">
                    Records labelled unknown.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------

    
    # BRICK_4_SENTIMENT_ALERTS
    section(
        "Sentiment alerts & recommended actions",
        "Set a threshold to identify when negative audience reactions "
        "need closer attention."
    )

    alert_threshold = st.slider(
        "Alert when negative sentiment reaches (%)",
        min_value=5,
        max_value=80,
        value=30,
        step=5,
        key="brick4_negative_alert_threshold",
    )

    alert_col1, alert_col2 = st.columns(2, gap="medium")

    with alert_col1:
        st.metric("Current negative sentiment", f"{negative_pct:.1f}%")

    with alert_col2:
        st.metric("Alert threshold", f"{alert_threshold}%")

    if total_records == 0:
        st.info("Run an analysis with records to generate sentiment alerts.")
    elif negative_pct >= alert_threshold:
        st.error(
            f"Attention needed: negative sentiment is {negative_pct:.1f}%, "
            f"which meets or exceeds your {alert_threshold}% threshold."
        )
    else:
        st.success(
            f"Negative sentiment is below your {alert_threshold}% threshold."
        )

    st.markdown("#### Recommended next steps")

    if negative_pct >= alert_threshold:
        st.markdown(
            "- Review the negative records below and identify recurring "
            "complaints or concerns.\n"
            "- Group similar complaints into themes before deciding what "
            "action to take.\n"
            "- Recheck sentiment after addressing the main concerns."
        )
    elif negative > 0:
        st.markdown(
            "- Review a sample of negative records for recurring issues.\n"
            "- Monitor whether the negative share increases in your next "
            "analysis."
        )
    else:
        st.markdown(
            "- No negative records were detected in this dataset.\n"
            "- Continue monitoring future results; this does not guarantee "
            "that all audience feedback is positive."
        )

    if "dashboard_emotion" in data.columns:
        valid_emotions = (
            data["dashboard_emotion"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        valid_emotions = valid_emotions[
            ~valid_emotions.str.lower().isin(
                ["", "nan", "none", "unknown"]
            )
        ]

        if not valid_emotions.empty:
            emotion_counts = valid_emotions.value_counts()
            leading_emotion = emotion_counts.index[0]
            st.info(
                f"Most frequent detected emotion: **{leading_emotion}** "
                f"({int(emotion_counts.iloc[0]):,} records). "
                "Use this as a signal to investigate, not as proof of "
                "the audience's actual feelings."
            )

    # BRICK_2A_NEGATIVE_COMMENT_REVIEW
    # ------------------------------------------------------
    # NEGATIVE COMMENT REVIEW
    # ------------------------------------------------------

    section(
        "Comments to investigate",
        "Review records classified as negative by the current analysis."
    )

    negative_data = data[
        data["dashboard_sentiment"] == "Negative"
    ].copy()

    comment_column = next(
        (
            column for column in [
                "text", "comment", "comments", "content",
                "review", "message"
            ]
            if column in negative_data.columns
        ),
        None,
    )

    review_col1, review_col2 = st.columns(2)

    with review_col1:
        st.metric("Negative records", f"{len(negative_data):,}")

    with review_col2:
        negative_share = (
            len(negative_data) / total_records * 100
            if total_records else 0
        )
        st.metric("Share of all records", f"{negative_share:.1f}%")

    if negative_data.empty:
        st.success(
            "No records were classified as negative in this analysis."
        )
    elif comment_column is None:
        st.warning(
            "Negative records exist, but no recognized text column "
            "was found to display their content."
        )
        st.dataframe(
            negative_data.head(100),
            use_container_width=True,
            hide_index=True,
        )
    else:
        review_columns = [comment_column, "dashboard_sentiment"]

        if "dashboard_emotion" in negative_data.columns:
            review_columns.append("dashboard_emotion")

        if "sentiment_score" in negative_data.columns:
            review_columns.append("sentiment_score")

        review_data = negative_data[review_columns].copy()
        review_data = review_data.rename(
            columns={
                comment_column: "Comment / Content",
                "dashboard_sentiment": "Sentiment",
                "dashboard_emotion": "Emotion",
                "sentiment_score": "Sentiment Score",
            }
        )

        st.dataframe(
            review_data.head(100),
            use_container_width=True,
            hide_index=True,
        )

        if len(review_data) > 100:
            st.caption(
                "Showing the first 100 negative records. "
                "The count above includes all negative records."
            )


    # BRICK_3_SENTIMENT_CONFIDENCE
    st.markdown("### 🎯 Sentiment Confidence Analysis")
    st.caption(
        "Confidence indicates how strongly the model supports a prediction; "
        "it does not guarantee that the prediction is correct."
    )

    confidence_source = data.copy()

    if "sentiment_score" not in confidence_source.columns:
        st.info(
            "No sentiment_score field is available for this dataset. "
            "Run an analysis that provides confidence scores to use this section."
        )
    else:
        confidence_source["confidence_value"] = pd.to_numeric(
            confidence_source["sentiment_score"], errors="coerce"
        )

        confidence_source = confidence_source[
            confidence_source["confidence_value"].notna()
            & confidence_source["dashboard_sentiment"].isin(
                ["Positive", "Neutral", "Negative"]
            )
        ].copy()

        if confidence_source.empty:
            st.info("No valid sentiment confidence scores are available yet.")
        else:
            # Support either 0–1 probabilities or 0–100 percentages.
            score_max = float(confidence_source["confidence_value"].max())
            if score_max > 1 and score_max <= 100:
                confidence_source["confidence_pct"] = (
                    confidence_source["confidence_value"].clip(0, 100)
                )
            else:
                confidence_source["confidence_pct"] = (
                    confidence_source["confidence_value"].clip(0, 1) * 100
                )

            threshold = st.slider(
                "Low-confidence review threshold (%)",
                min_value=10,
                max_value=90,
                value=60,
                step=5,
                key="brick3_confidence_threshold",
            )

            average_confidence = float(
                confidence_source["confidence_pct"].mean()
            )
            low_confidence = confidence_source[
                confidence_source["confidence_pct"] < threshold
            ]

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric(
                "Average confidence", f"{average_confidence:.1f}%"
            )
            metric_col2.metric(
                "Predictions reviewed", f"{len(confidence_source):,}"
            )
            metric_col3.metric(
                f"Below {threshold}% threshold", f"{len(low_confidence):,}"
            )

            confidence_chart = px.histogram(
                confidence_source,
                x="confidence_pct",
                nbins=10,
                title="Distribution of sentiment confidence",
                labels={"confidence_pct": "Confidence (%)"},
            )
            confidence_chart.update_layout(
                xaxis_title="Confidence (%)",
                yaxis_title="Number of records",
                bargap=0.08,
            )
            st.plotly_chart(
                confidence_chart,
                use_container_width=True,
                key="brick3_confidence_histogram",
            )

            if not low_confidence.empty:
                st.markdown("#### Records needing review")
                text_column = next(
                    (
                        column for column in
                        ["text", "comment", "comments", "content",
                         "review", "message"]
                        if column in low_confidence.columns
                    ),
                    None,
                )

                display_columns = []
                if text_column:
                    display_columns.append(text_column)
                display_columns.extend(
                    ["dashboard_sentiment", "confidence_pct"]
                )

                review_table = low_confidence[display_columns].copy()
                review_table = review_table.rename(
                    columns={
                        "dashboard_sentiment": "Predicted sentiment",
                        "confidence_pct": "Confidence (%)",
                    }
                )
                review_table["Confidence (%)"] = review_table[
                    "Confidence (%)"
                ].round(1)

                st.dataframe(
                    review_table,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success(
                    "No valid predictions fall below the selected threshold."
                )

    # MODEL EVALUATION
    # ------------------------------------------------------

    section(
        "Model evaluation",
        "Metrics loaded from your project's evaluation_metrics.csv file.",
    )

    metrics = load_model_metrics()

    if metrics:
        accuracy = find_metric(metrics, "accuracy")
        precision = find_metric(metrics, "precision")
        recall = find_metric(metrics, "recall")
        f1 = find_metric(metrics, "f1")

        m1, m2, m3, m4 = st.columns(4, gap="medium")

        with m1:
            st.metric("Accuracy", format_percent(accuracy))

        with m2:
            st.metric("Precision", format_percent(precision))

        with m3:
            st.metric("Recall", format_percent(recall))

        with m4:
            st.metric("F1 score", format_percent(f1))

        st.caption(
            "These are evaluation-dataset metrics, not live accuracy "
            "measurements calculated from the current uploaded data."
        )
    else:
        st.info(
            "No evaluation metrics file was found. "
            "Add evaluation_metrics.csv to the evaluation folder "
            "to display model performance."
        )

    # ------------------------------------------------------
    # ANALYZED RECORDS
    # ------------------------------------------------------

    section("Explore analyzed records")

    searchable_columns = [
        column for column in [
            "text",
            "comment",
            "comments",
            "content",
            "review",
            "sentiment",
            "emotion",
        ]
        if column in data.columns
    ]

    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        search_text = st.text_input(
            "Search records",
            placeholder="Search comments, reviews, or text...",
            key="dashboard_record_search",
        )

    with filter_col2:
        sentiment_options = ["All"] + sorted(
            data["dashboard_sentiment"].dropna().unique().tolist()
        )

        selected_sentiment = st.selectbox(
            "Filter by sentiment",
            options=sentiment_options,
            key="dashboard_sentiment_filter",
        )

    filtered_data = data.copy()

    if selected_sentiment != "All":
        filtered_data = filtered_data[
            filtered_data["dashboard_sentiment"] == selected_sentiment
        ]

    if search_text.strip() and searchable_columns:
        search_mask = pd.Series(
            False,
            index=filtered_data.index,
        )

        for column in searchable_columns:
            search_mask |= (
                filtered_data[column]
                .fillna("")
                .astype(str)
                .str.contains(
                    search_text.strip(),
                    case=False,
                    regex=False,
                )
            )

        filtered_data = filtered_data[search_mask]

    st.caption(
        f"Showing {len(filtered_data):,} of {total_records:,} records."
    )

    preferred_columns = [
        "text",
        "comment",
        "comments",
        "content",
        "sentiment",
        "sentiment_score",
        "emotion",
        "emotion_score",
        "evidence_phrases",
        "sentiment_explanation",
        "emotion_explanation",
        "analysis_error",
    ]

    visible_columns = [
        column for column in preferred_columns
        if column in filtered_data.columns
    ]

    if not visible_columns:
        visible_columns = list(filtered_data.columns)

    with st.expander("View filtered results", expanded=False):
        st.dataframe(
            filtered_data[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    st.divider()

    download_df = filtered_data.drop(
        columns=["dashboard_sentiment", "dashboard_emotion"],
        errors="ignore",
    )

    download_csv = download_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "⬇️ Download dashboard results",
        data=download_csv,
        file_name="social_media_dashboard.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )


# ==========================================================
# COMPATIBILITY
# ==========================================================

show_dashboard = show
