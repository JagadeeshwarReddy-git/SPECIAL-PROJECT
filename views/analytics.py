import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# HELPERS
# =========================================================

def find_column(df, names):
    columns = {str(c).strip().lower(): c for c in df.columns}
    for name in names:
        if name.lower() in columns:
            return columns[name.lower()]
    return None


def get_analysis_data():
    """Read the latest results from the existing analyzers."""
    for key in (
        "analysis_df",
        "universal_analysis_df",
        "df",
        "youtube_analysis_df",
        "text_analysis_df",
    ):
        value = st.session_state.get(key)
        if isinstance(value, pd.DataFrame) and not value.empty:
            return value.copy()
    return None


def get_words(text):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", str(text).lower())

    stop_words = {
        "the", "and", "for", "are", "was", "were", "with",
        "this", "that", "from", "have", "has", "you", "your",
        "they", "their", "them", "our", "not", "but", "all",
        "can", "could", "would", "should", "will", "just",
        "about", "what", "when", "where", "which", "who",
        "how", "why", "there", "here", "then", "than", "into",
        "been", "being", "also", "very", "more", "most", "some",
        "only", "because", "after", "before", "over", "under",
        "other", "get", "got", "make", "made", "know", "think",
        "really", "one", "two", "www", "http", "https", "com",
    }

    return [word for word in words if word not in stop_words]


def show():
    st.title("📊 Analytics")
    st.caption(
        "Understand your analyzed content, discover patterns, "
        "and identify useful actions."
    )

    # -----------------------------------------------------
    # LOAD THE LATEST ANALYZER RESULTS
    # -----------------------------------------------------

    df = get_analysis_data()

    if df is None:
        st.info(
            "No results yet. Run Text Analyzer, YouTube Analyzer, "
            "or File Analyzer first, then return here."
        )
        return

    df.columns = [str(c).strip() for c in df.columns]

    source = (
        st.session_state.get("analysis_source")
        or st.session_state.get("current_analysis_source")
        or st.session_state.get("youtube_title")
        or st.session_state.get("csv_filename")
        or st.session_state.get("universal_analysis_filename")
        or "Latest analysis"
    )

    st.caption(f"Source: {source}")

    # -----------------------------------------------------
    # DETECT AVAILABLE FIELDS
    # -----------------------------------------------------

    text_col = find_column(df, [
        "text", "comment", "comments", "review", "content",
        "message", "feedback", "tweet", "post", "caption",
        "description", "title", "transcript",
    ])

    sentiment_col = find_column(df, [
        "sentiment", "predicted_sentiment", "sentiment_label",
    ])

    emotion_col = find_column(df, [
        "emotion", "predicted_emotion", "emotion_label",
    ])

    date_col = find_column(df, [
        "date", "datetime", "timestamp", "created_at",
        "published_at", "published", "upload_date", "post_date",
    ])

    views_col = find_column(df, [
        "views", "view_count", "video_views",
    ])

    likes_col = find_column(df, [
        "likes", "like_count", "likes_count",
    ])

    shares_col = find_column(df, [
        "shares", "share_count", "shares_count",
    ])

    comments_col = find_column(df, [
        "comments_count", "comment_count", "num_comments",
        "total_comments",
    ])

    # -----------------------------------------------------
    # SIMPLE OVERVIEW
    # -----------------------------------------------------

    st.subheader("Overview")

    total = len(df)
    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Records", f"{total:,}")
    c2.metric("Columns", f"{len(df.columns):,}")
    c3.metric("Missing values", f"{missing:,}")
    c4.metric("Duplicates", f"{duplicates:,}")

    # -----------------------------------------------------
    # SENTIMENT — ONLY IF PROVIDED BY THE ANALYZER
    # -----------------------------------------------------

    sentiment_labels = None

    if sentiment_col:
        st.subheader("Audience Sentiment")

        raw = df[sentiment_col].fillna("").astype(str).str.lower()

        sentiment_labels = raw.replace({
            "pos": "positive",
            "neg": "negative",
            "neu": "neutral",
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive",
        })

        counts = sentiment_labels.value_counts()

        positive = int(counts.get("positive", 0))
        negative = int(counts.get("negative", 0))
        neutral = int(counts.get("neutral", 0))

        a, b, c = st.columns(3)

        a.metric("Positive", f"{positive:,}")
        b.metric("Negative", f"{negative:,}")
        c.metric("Neutral", f"{neutral:,}")

        chart_data = counts.rename_axis(
            "Sentiment"
        ).reset_index(name="Records")

        if not chart_data.empty:
            fig = px.pie(
                chart_data,
                names="Sentiment",
                values="Records",
                hole=0.45,
                title="Audience Feedback",
            )
            st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # KEY INSIGHTS
    # -----------------------------------------------------

    st.subheader("Key Insights")

    insights = []

    if text_col:
        texts = df[text_col].dropna().astype(str)
        texts = texts[texts.str.strip() != ""]

        if not texts.empty:
            lengths = texts.str.len()

            insights.append(
                f"Your analysis contains {len(texts):,} readable "
                f"text records, averaging {lengths.mean():.0f} characters."
            )

            words = Counter()

            for text in texts:
                words.update(get_words(text))

            if words:
                popular = ", ".join(
                    word for word, _ in words.most_common(5)
                )
                insights.append(
                    f"The most frequently mentioned terms are: {popular}."
                )

            if sentiment_labels is not None:
                sentiment_counts = sentiment_labels.value_counts()

                if not sentiment_counts.empty:
                    main_sentiment = sentiment_counts.idxmax()
                    share = (
                        sentiment_counts.max()
                        / len(sentiment_labels)
                        * 100
                    )

                    insights.append(
                        f"The most common sentiment is "
                        f"{main_sentiment} ({share:.1f}% of records)."
                    )
    else:
        insights.append(
            "This dataset has no recognized text column. "
            "Other available metrics and fields can still be analyzed."
        )

    if missing:
        insights.append(
            f"{missing:,} data cells are missing and may need attention."
        )

    if duplicates:
        insights.append(
            f"{duplicates:,} duplicate records were detected."
        )

    for insight in insights:
        st.markdown(f"- {insight}")

    # -----------------------------------------------------
    # WHAT PEOPLE ARE TALKING ABOUT
    # -----------------------------------------------------

    if text_col:
        st.subheader("Popular Topics")

        all_words = Counter()

        for text in df[text_col].dropna().astype(str):
            all_words.update(get_words(text))

        if all_words:
            topics = pd.DataFrame(
                all_words.most_common(10),
                columns=["Topic", "Mentions"],
            )

            fig = px.bar(
                topics.sort_values("Mentions"),
                x="Mentions",
                y="Topic",
                orientation="h",
                title="Most Discussed Terms",
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough text to identify recurring terms.")

    # -----------------------------------------------------
    # ENGAGEMENT — WHEN THE DATA CONTAINS THESE METRICS
    # -----------------------------------------------------

    engagement_columns = {
        "Views": views_col,
        "Likes": likes_col,
        "Shares": shares_col,
        "Comments": comments_col,
    }

    engagement_columns = {
        name: col
        for name, col in engagement_columns.items()
        if col is not None
    }

    if engagement_columns:
        st.subheader("Content Performance")

        metrics = st.columns(len(engagement_columns))

        for metric, (name, column) in zip(
            metrics, engagement_columns.items()
        ):
            values = pd.to_numeric(
                df[column], errors="coerce"
            ).dropna()

            metric.metric(
                f"Total {name}",
                f"{values.sum():,.0f}",
            )

        ranking_col = likes_col or views_col

        if text_col and ranking_col:
            ranked = df.copy()

            ranked[ranking_col] = pd.to_numeric(
                ranked[ranking_col], errors="coerce"
            )

            ranked = ranked.dropna(
                subset=[ranking_col]
            ).nlargest(10, ranking_col)

            if not ranked.empty:
                ranked["Content"] = (
                    ranked[text_col].fillna("").astype(str).str[:70]
                )

                fig = px.bar(
                    ranked,
                    x=ranking_col,
                    y="Content",
                    orientation="h",
                    title=f"Top Content by {ranking_col}",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

    # -----------------------------------------------------
    # TRENDS — WHEN DATES ARE AVAILABLE
    # -----------------------------------------------------

    if date_col:
        dates = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )

        valid = dates.notna()

        if valid.sum() > 1:
            trend = pd.DataFrame({
                "Date": dates[valid].dt.date,
            })

            trend = (
                trend.groupby("Date")
                .size()
                .reset_index(name="Records")
            )

            if len(trend) > 1:
                st.subheader("Activity Trends")

                fig = px.line(
                    trend,
                    x="Date",
                    y="Records",
                    markers=True,
                    title="Records Over Time",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

    # -----------------------------------------------------
    # EMOTIONS — ONLY IF PROVIDED BY THE ANALYZER
    # -----------------------------------------------------

    if emotion_col:
        st.subheader("Common Emotions")

        emotions = (
            df[emotion_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(8)
            .rename_axis("Emotion")
            .reset_index(name="Records")
        )

        fig = px.bar(
            emotions,
            x="Emotion",
            y="Records",
            title="Emotion Breakdown",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    st.subheader("Recommended Actions")

    if text_col:
        st.markdown(
            "- Review popular topics to understand recurring audience interests."
        )

    if sentiment_col:
        if sentiment_labels is not None:
            negative_count = int(
                (sentiment_labels == "negative").sum()
            )

            if negative_count:
                st.markdown(
                    f"- Review the {negative_count:,} negative records "
                    "to identify common complaints or issues."
                )

    if engagement_columns:
        st.markdown(
            "- Compare high-performing content to identify what attracts attention."
        )

    if date_col:
        st.markdown(
            "- Review changes over time to identify periods of increased activity."
        )

    st.markdown(
        "- Use these findings alongside the original content before making decisions."
    )

    # -----------------------------------------------------
    # DATA AND DOWNLOAD
    # -----------------------------------------------------

    with st.expander("View analyzed data"):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.download_button(
        "⬇️ Download Analytics",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="social_media_analytics.csv",
        mime="text/csv",
        use_container_width=True,
    )


if __name__ == "__main__":
    show()