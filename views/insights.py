
import streamlit as st
import pandas as pd


# ==========================================================
# SHARED DATA LOADER
# ==========================================================

def get_shared_analysis_data():
    """
    Load analysis data shared by CSV Upload, YouTube analysis,
    text analysis, Analytics, and Trend Analyzer.
    """

    data_keys = (
        "analysis_df",
        "universal_analysis_df",
        "df",
    )

    for key in data_keys:
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


# ==========================================================
# COLUMN HELPERS
# ==========================================================

def find_column(df, possible_names):
    """
    Find a column regardless of capitalization or extra spaces.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        actual_column = normalized_columns.get(name.lower())

        if actual_column is not None:
            return actual_column

    return None


def normalize_sentiment_values(series):
    """
    Normalize common sentiment labels into positive, negative,
    neutral, or unknown.
    """

    positive_labels = {
        "positive",
        "pos",
        "good",
        "favorable",
        "favourable",
        "satisfied",
        "supportive",
        "happy",
    }

    negative_labels = {
        "negative",
        "neg",
        "bad",
        "unfavorable",
        "unfavourable",
        "unsatisfied",
        "angry",
        "hate",
    }

    neutral_labels = {
        "neutral",
        "neu",
        "mixed-neutral",
        "neither",
    }

    values = series.fillna("").astype(str).str.strip().str.lower()

    def classify(value):
        if value in positive_labels:
            return "positive"

        if value in negative_labels:
            return "negative"

        if value in neutral_labels:
            return "neutral"

        return "unknown"

    return values.map(classify)


# ==========================================================
# MAIN PAGE
# ==========================================================

def show():

    st.title("🧠 AI Insights")

    st.markdown(
        "Understand audience reactions, identify patterns, "
        "and get actionable recommendations from your analyzed data."
    )

    # ------------------------------------------------------
    # Load shared data
    # ------------------------------------------------------

    df = get_shared_analysis_data()

    if df is None:
        st.info(
            "📂 No analysis data is available yet.\n\n"
            "Please analyze a YouTube video, analyze text, "
            "or upload a CSV file first."
        )

        if st.button("📂 Go to CSV Upload", key="insights_go_upload"):
            st.session_state["page"] = "📂 CSV Upload"
            st.rerun()

        return

    if df.empty:
        st.info(
            "The analysis dataset is empty. Please upload or analyze data first."
        )
        return

    # ------------------------------------------------------
    # Identify sentiment column
    # ------------------------------------------------------

    sentiment_column = find_column(
        df,
        [
            "sentiment",
            "predicted_sentiment",
            "sentiment_label",
            "polarity",
            "sentiment_result",
        ],
    )

    # ------------------------------------------------------
    # Display dataset overview
    # ------------------------------------------------------

    with st.expander("📋 View dataset", expanded=False):
        st.write(f"**Rows:** {len(df):,}")
        st.write(f"**Columns:** {len(df.columns):,}")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # Handle datasets without sentiment labels
    # ------------------------------------------------------

    if sentiment_column is None:
        st.warning(
            "⚠️ This dataset does not contain a recognized sentiment column. "
            "Dataset details are available above, but sentiment-based insights "
            "cannot be calculated until sentiment labels are generated."
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

        if text_column is not None:
            st.subheader("📝 Text data preview")
            st.caption(f"Detected text column: {text_column}")

            preview = df[text_column].dropna().astype(str).head(10)

            if not preview.empty:
                for index, value in enumerate(preview, start=1):
                    st.write(f"**{index}.** {value}")
            else:
                st.info("The detected text column has no usable values.")

        st.info(
            "If this is a raw CSV, run sentiment analysis on its text column "
            "first. Uploading a CSV does not automatically guarantee that "
            "sentiment labels exist."
        )
        return

    # ------------------------------------------------------
    # Normalize sentiment values
    # ------------------------------------------------------

    sentiment = normalize_sentiment_values(df[sentiment_column])

    total = len(df)

    positive = int((sentiment == "positive").sum())
    negative = int((sentiment == "negative").sum())
    neutral = int((sentiment == "neutral").sum())
    unknown = int((sentiment == "unknown").sum())

    positive_percent = round(positive / total * 100, 2) if total else 0
    negative_percent = round(negative / total * 100, 2) if total else 0
    neutral_percent = round(neutral / total * 100, 2) if total else 0
    unknown_percent = round(unknown / total * 100, 2) if total else 0

    # ------------------------------------------------------
    # Overall statistics
    # ------------------------------------------------------

    st.subheader("📊 Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("😊 Positive", f"{positive_percent}%")

    with col2:
        st.metric("😐 Neutral", f"{neutral_percent}%")

    with col3:
        st.metric("😡 Negative", f"{negative_percent}%")

    with col4:
        st.metric("📄 Total Records", f"{total:,}")

    if unknown > 0:
        st.caption(
            f"{unknown:,} record(s) ({unknown_percent}%) have missing "
            "or unrecognized sentiment labels."
        )

    # ------------------------------------------------------
    # Sentiment distribution
    # ------------------------------------------------------

    st.divider()
    st.subheader("📈 Sentiment Distribution")

    sentiment_counts = pd.DataFrame(
        {
            "Sentiment": ["Positive", "Neutral", "Negative", "Unknown"],
            "Count": [positive, neutral, negative, unknown],
        }
    )

    st.bar_chart(
        sentiment_counts.set_index("Sentiment"),
        y="Count",
    )

    # ------------------------------------------------------
    # Audience reaction
    # ------------------------------------------------------

    st.divider()
    st.subheader("🎯 Audience Reaction")

    known_sentiment_count = positive + negative + neutral

    if known_sentiment_count == 0:
        st.warning(
            "No recognized positive, neutral, or negative sentiment labels "
            "were found. Check the values in the sentiment column."
        )

    elif positive_percent >= 70:
        st.success(
            "**Audience reaction is highly positive.**\n\n"
            "Most records with recognized sentiment are positive. "
            "Continue examining the topics, features, or content that "
            "audiences appreciate."
        )

    elif negative_percent >= 50:
        st.error(
            "**Audience reaction is mostly negative.**\n\n"
            "A large proportion of records express negative sentiment. "
            "Review negative feedback and identify recurring issues "
            "before deciding what to improve."
        )

    elif negative > positive:
        st.warning(
            "**Negative reactions are more common than positive reactions.**\n\n"
            "Inspect negative records for recurring complaints and compare "
            "them with positive feedback."
        )

    elif positive > negative:
        st.info(
            "**Audience reaction leans positive.**\n\n"
            "Positive reactions outnumber negative ones. Continue monitoring "
            "neutral and negative feedback to identify opportunities."
        )

    else:
        st.info(
            "**Audience reaction is balanced.**\n\n"
            "Positive and negative reactions are similar. Explore individual "
            "records to understand what drives each type of reaction."
        )

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    st.divider()
    st.subheader("💡 Recommendations")

    recommendations = []

    if positive_percent >= 70:
        recommendations.append(
            "Identify the topics and characteristics associated with positive "
            "feedback and consider building on those strengths."
        )
    elif positive_percent >= 50:
        recommendations.append(
            "Preserve the elements receiving positive feedback while "
            "investigating areas that could be improved."
        )

    if negative_percent >= 30:
        recommendations.append(
            "Review negative records and group recurring complaints into "
            "themes before prioritizing improvements."
        )

    if negative_percent >= 50:
        recommendations.append(
            "Prioritize the most frequent and impactful problems reported "
            "in negative feedback."
        )

    if neutral_percent >= 40:
        recommendations.append(
            "Look for ways to make the content or experience more useful, "
            "specific, or engaging to audiences currently expressing neutral reactions."
        )

    if unknown > 0:
        recommendations.append(
            f"Review {unknown:,} record(s) with missing or unrecognized "
            "sentiment labels. Correct or classify them if appropriate."
        )

    if not recommendations:
        recommendations.append(
            "Continue monitoring sentiment and compare feedback across "
            "different topics, time periods, or content categories."
        )

    for recommendation in recommendations:
        st.markdown(f"- ✅ {recommendation}")

    # ------------------------------------------------------
    # Emotion insights
    # ------------------------------------------------------

    emotion_column = find_column(
        df,
        [
            "emotion",
            "predicted_emotion",
            "emotion_label",
            "dominant_emotion",
        ],
    )

    if emotion_column is not None:
        st.divider()
        st.subheader("🎭 Emotion Insights")

        emotions = (
            df[emotion_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        excluded_emotions = {
            "",
            "unknown",
            "nan",
            "none",
            "null",
            "n/a",
            "na",
        }

        emotions = emotions[~emotions.isin(excluded_emotions)]
        emotion_counts = emotions.value_counts()

        if not emotion_counts.empty:
            dominant_emotion = emotion_counts.index[0]
            dominant_count = int(emotion_counts.iloc[0])

            emotion_percent = round(
                dominant_count / total * 100,
                2,
            ) if total else 0

            emotion_col1, emotion_col2 = st.columns(2)

            with emotion_col1:
                st.metric(
                    "🎭 Most Common Emotion",
                    dominant_emotion.title(),
                )

            with emotion_col2:
                st.metric(
                    "📊 Records with this emotion",
                    f"{dominant_count:,} ({emotion_percent}%)",
                )

            emotion_chart = emotion_counts.rename_axis("Emotion").reset_index()
            emotion_chart.columns = ["Emotion", "Count"]

            st.bar_chart(
                emotion_chart.set_index("Emotion"),
                y="Count",
            )
        else:
            st.info("No usable emotion labels are available in this dataset.")

    # ------------------------------------------------------
    # Summary table
    # ------------------------------------------------------

    st.divider()
    st.subheader("📋 Summary")

    if positive > negative:
        overall_mood = "Positive"
    elif negative > positive:
        overall_mood = "Negative"
    else:
        overall_mood = "Balanced"

    summary_df = pd.DataFrame(
        {
            "Metric": [
                "Total Records",
                "Positive Records",
                "Neutral Records",
                "Negative Records",
                "Unknown Sentiment Records",
                "Positive Percentage",
                "Neutral Percentage",
                "Negative Percentage",
                "Overall Audience Mood",
                "Sentiment Column Used",
            ],
            "Value": [
                total,
                positive,
                neutral,
                negative,
                unknown,
                f"{positive_percent}%",
                f"{neutral_percent}%",
                f"{negative_percent}%",
                overall_mood,
                str(sentiment_column),
            ],
        }
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------
    # Download summary
    # ------------------------------------------------------

    st.download_button(
        label="⬇️ Download Insights Summary (CSV)",
        data=summary_df.to_csv(index=False).encode("utf-8"),
        file_name="ai_insights_summary.csv",
        mime="text/csv",
        key="download_ai_insights_summary",
    )
