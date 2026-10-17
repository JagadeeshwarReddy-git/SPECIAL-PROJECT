import streamlit as st
import pandas as pd


def show():

    st.title("🧠 AI Insights")

    st.markdown(
        "Understand your audience reaction and get "
        "actionable recommendations from the analyzed data."
    )

    # ==========================================================
    # Get Analysis Data
    # ==========================================================

    df = st.session_state.get("analysis_df")

    # ----------------------------------------------------------
    # No Data
    # ----------------------------------------------------------

    if df is None:

        st.info(
            "📂 No analysis data available yet.\n\n"
            "Please analyze a YouTube video, analyze text, "
            "or upload a CSV file first."
        )

        return

    # ----------------------------------------------------------
    # Check DataFrame
    # ----------------------------------------------------------

    if not isinstance(df, pd.DataFrame):

        st.error(
            "❌ Analysis data is not in the correct format."
        )

        return

    # ----------------------------------------------------------
    # Empty DataFrame
    # ----------------------------------------------------------

    if df.empty:

        st.info(
            "📂 The analysis dataset is empty.\n\n"
            "Please analyze some data first."
        )

        return

    # ==========================================================
    # Check Sentiment Column
    # ==========================================================

    if "sentiment" not in df.columns:

        st.warning(
            "⚠️ Sentiment analysis is not available "
            "for the current dataset."
        )

        st.subheader("📋 Available Dataset")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        return

    # ==========================================================
    # Normalize Sentiment
    # ==========================================================

    sentiment = (
        df["sentiment"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ==========================================================
    # Calculate Statistics
    # ==========================================================

    total = len(df)

    positive = int(
        (sentiment == "positive").sum()
    )

    negative = int(
        (sentiment == "negative").sum()
    )

    neutral = int(
        (sentiment == "neutral").sum()
    )

    # Unknown values
    unknown = total - (
        positive +
        negative +
        neutral
    )

    # ==========================================================
    # Calculate Percentages
    # ==========================================================

    if total > 0:

        positive_percent = round(
            (positive / total) * 100,
            2
        )

        negative_percent = round(
            (negative / total) * 100,
            2
        )

        neutral_percent = round(
            (neutral / total) * 100,
            2
        )

    else:

        positive_percent = 0
        negative_percent = 0
        neutral_percent = 0

    # ==========================================================
    # Overall Statistics
    # ==========================================================

    st.subheader("📊 Overall Statistics")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "😊 Positive",
            f"{positive_percent}%"
        )

    with c2:

        st.metric(
            "😐 Neutral",
            f"{neutral_percent}%"
        )

    with c3:

        st.metric(
            "😡 Negative",
            f"{negative_percent}%"
        )

    with c4:

        st.metric(
            "📄 Total",
            total
        )

    # ==========================================================
    # Audience Reaction
    # ==========================================================

    st.divider()

    st.subheader("📈 Audience Reaction")

    # ----------------------------------------------------------
    # Highly Positive
    # ----------------------------------------------------------

    if positive_percent >= 70:

        st.success(
            """
            **Audience reaction is highly positive.**

            Most analyzed comments show a positive reaction
            to the content.

            **Recommendation:** Continue producing content
            with similar themes, topics, and presentation.
            """
        )

    # ----------------------------------------------------------
    # Mostly Negative
    # ----------------------------------------------------------

    elif negative_percent >= 50:

        st.error(
            """
            **Audience reaction is mostly negative.**

            A large proportion of analyzed comments express
            negative sentiment.

            **Recommendation:** Review negative comments,
            identify recurring complaints, and improve the
            areas that viewers are dissatisfied with.
            """
        )

    # ----------------------------------------------------------
    # Mixed
    # ----------------------------------------------------------

    else:

        st.info(
            """
            **Audience reaction is mixed.**

            The audience contains a combination of positive,
            neutral, and negative reactions.

            **Recommendation:** Examine the comments and
            identify the specific topics that produce positive
            or negative reactions.
            """
        )

    # ==========================================================
    # AI-style Recommendations
    # ==========================================================

    st.divider()

    st.subheader("💡 Recommendations")

    recommendations = []

    # ----------------------------------------------------------
    # Positive
    # ----------------------------------------------------------

    if positive_percent >= 70:

        recommendations.append(
            "Continue producing content similar to the content "
            "that generated positive audience reactions."
        )

    elif positive_percent >= 50:

        recommendations.append(
            "Maintain the elements that viewers appreciate "
            "while improving weaker areas."
        )

    # ----------------------------------------------------------
    # Negative
    # ----------------------------------------------------------

    if negative_percent >= 30:

        recommendations.append(
            "Investigate recurring negative comments to "
            "identify specific audience complaints."
        )

    if negative_percent >= 50:

        recommendations.append(
            "Prioritize improving the issues mentioned in "
            "negative comments before producing similar content."
        )

    # ----------------------------------------------------------
    # Neutral
    # ----------------------------------------------------------

    if neutral_percent >= 40:

        recommendations.append(
            "Improve audience engagement by encouraging "
            "questions, discussions, and stronger calls to action."
        )

    # ----------------------------------------------------------
    # Unknown
    # ----------------------------------------------------------

    if unknown > 0:

        recommendations.append(
            f"{unknown} records could not be assigned a standard "
            "sentiment category."
        )

    # ----------------------------------------------------------
    # Default
    # ----------------------------------------------------------

    if not recommendations:

        recommendations.append(
            "Audience engagement appears reasonably balanced. "
            "Continue monitoring sentiment and audience feedback."
        )

    # ----------------------------------------------------------
    # Display Recommendations
    # ----------------------------------------------------------

    for recommendation in recommendations:

        st.write(
            "✅",
            recommendation
        )

    # ==========================================================
    # Emotion Insight
    # ==========================================================

    if "emotion" in df.columns:

        st.divider()

        st.subheader("🎭 Dominant Emotion")

        emotions = (
            df["emotion"]
            .astype(str)
            .str.strip()
            .str.lower()
            .value_counts()
        )

        # Remove unknown/empty values

        emotions = emotions[
            ~emotions.index.isin(
                ["unknown", "nan", ""]
            )
        ]

        if not emotions.empty:

            dominant_emotion = emotions.index[0]

            dominant_count = int(
                emotions.iloc[0]
            )

            dominant_percentage = round(
                (dominant_count / total) * 100,
                2
            )

            st.metric(
                "🎭 Most Common Emotion",
                dominant_emotion.title()
            )

            st.write(
                f"The dominant emotion is **{dominant_emotion.title()}**, "
                f"appearing in approximately "
                f"**{dominant_percentage}%** of analyzed records."
            )

        else:

            st.info(
                "No usable emotion data is available."
            )

    # ==========================================================
    # Summary
    # ==========================================================

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
                "Positive",
                "Neutral",
                "Negative",
                "Overall Audience Mood"
            ],

            "Value": [
                total,
                positive,
                neutral,
                negative,
                overall_mood
            ]
        }
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )