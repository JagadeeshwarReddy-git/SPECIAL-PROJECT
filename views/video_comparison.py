
import streamlit as st
import pandas as pd
import plotly.express as px

from services.youtube_api import YouTubeAPI
from services.analyzer import analyze_text

from services.video_summary import (
    fetch_video_transcript,
    generate_video_summary,
)


# ==========================================================
# VIDEO COMPARISON SETTINGS
# ==========================================================

MAX_COMMENTS = 100


# ==========================================================
# FETCH AND ANALYZE VIDEO COMMENTS
# ==========================================================

def analyze_video(url, api):

    details = api.get_video_details(url)

    if not details:

        raise ValueError(
            "Video not found. Please check the YouTube URL."
        )

    video_id = details["video_id"]

    comments = api.get_comments(
        video_id,
        max_comments=MAX_COMMENTS,
    )

    if not comments:

        raise ValueError(
            "No comments available for this video."
        )

    analyzed_comments = []

    progress = st.progress(0)

    for index, comment in enumerate(comments):

        comment_text = comment.get(
            "text",
            ""
        ).strip()

        if not comment_text:
            continue

        result = analyze_text(comment_text)

        sentiment = str(
            result.get(
                "sentiment",
                "neutral"
            )
        ).lower()

        emotion = str(
            result.get(
                "emotion",
                "neutral"
            )
        ).lower()

        analyzed_comments.append({

            "comment": comment_text,

            "author": comment.get(
                "author",
                "Unknown"
            ),

            "sentiment": sentiment,

            "emotion": emotion,

            "sentiment_score": result.get(
                "sentiment_score",
                0.0
            ),

            "emotion_score": result.get(
                "emotion_score",
                0.0
            ),

            "likes": comment.get(
                "likes",
                0
            ),

            "published": comment.get(
                "published",
                ""
            ),

        })

        progress.progress(
            min(
                (index + 1) / len(comments),
                1.0,
            )
        )

    progress.empty()

    if not analyzed_comments:

        raise ValueError(
            "No valid comments could be analyzed."
        )

    df = pd.DataFrame(
        analyzed_comments
    )

    return details, df


# ==========================================================
# SENTIMENT SUMMARY
# ==========================================================

def sentiment_summary(df):

    total = len(df)

    counts = (
        df["sentiment"]
        .value_counts()
    )

    positive = counts.get(
        "positive",
        0
    )

    negative = counts.get(
        "negative",
        0
    )

    neutral = counts.get(
        "neutral",
        0
    )

    return {

        "total": total,

        "positive": positive,

        "negative": negative,

        "neutral": neutral,

        "positive_percentage": (
            positive / total * 100
            if total else 0
        ),

        "negative_percentage": (
            negative / total * 100
            if total else 0
        ),

        "neutral_percentage": (
            neutral / total * 100
            if total else 0
        ),

    }


# ==========================================================
# VIDEO INFORMATION
# ==========================================================

def display_video(details, df, label):

    st.subheader(label)

    # ------------------------------------------------------
    # THUMBNAIL
    # ------------------------------------------------------

    thumbnail = details.get(
        "thumbnail"
    )

    if thumbnail:

        st.image(
            thumbnail,
            use_container_width=True,
        )

    # ------------------------------------------------------
    # TITLE
    # ------------------------------------------------------

    st.markdown(
        f"### {details.get('title', 'Unknown Video')}"
    )

    # ------------------------------------------------------
    # CHANNEL
    # ------------------------------------------------------

    st.write(
        "**Channel:**",
        details.get(
            "channel",
            "Unknown Channel"
        ),
    )

    # ------------------------------------------------------
    # VIDEO DESCRIPTION
    # ------------------------------------------------------

    description = details.get(
        "description",
        ""
    )

    with st.expander(
        "📝 Original Video Description"
    ):

        if description:

            st.write(description)

        else:

            st.info(
                "No video description available."
            )

    # ------------------------------------------------------
    # VIDEO STATISTICS
    # ------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Views",
            f"{details.get('views', 0):,}",
        )

    with col2:

        st.metric(
            "Likes",
            f"{details.get('likes', 0):,}",
        )

    # ------------------------------------------------------
    # SENTIMENT
    # ------------------------------------------------------

    summary = sentiment_summary(df)

    st.markdown(
        "#### 📊 Audience Sentiment"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Positive",
            f"{summary['positive_percentage']:.1f}%",
        )

    with col2:

        st.metric(
            "Negative",
            f"{summary['negative_percentage']:.1f}%",
        )

    with col3:

        st.metric(
            "Neutral",
            f"{summary['neutral_percentage']:.1f}%",
        )

    return summary


# ==========================================================
# AI VIDEO CONTENT SUMMARY
# SAME SERVICE AS YOUTUBE ANALYZER
# ==========================================================

def generate_video_content_explanation(
    details,
    video_label,
):

    video_id = details.get(
        "video_id",
        ""
    )

    title = details.get(
        "title",
        "Unknown Title"
    )

    description = details.get(
        "description",
        ""
    )

    if not video_id:

        st.warning(
            f"{video_label}: Video ID is unavailable."
        )

        return

    # ------------------------------------------------------
    # SESSION CACHE
    # ------------------------------------------------------

    summary_key = (
        f"comparison_video_summary_{video_id}"
    )

    # ------------------------------------------------------
    # GENERATE SUMMARY
    # ------------------------------------------------------

    if summary_key not in st.session_state:

        with st.spinner(
            f"Generating AI explanation for {video_label}..."
        ):

            transcript = fetch_video_transcript(
                video_id
            )

            result = generate_video_summary(

                title=title,

                description=description,

                transcript=transcript,

            )

        st.session_state[summary_key] = {

            "summary": result.get(
                "summary",
                "No summary generated."
            ),

            "source": result.get(
                "source",
                "Unknown"
            ),

            "transcript_available": bool(
                transcript
            ),

        }

    # ------------------------------------------------------
    # DISPLAY SUMMARY
    # ------------------------------------------------------

    saved_summary = st.session_state[
        summary_key
    ]

    st.markdown(
        "#### 🧠 AI Video Content Explanation"
    )

    if saved_summary[
        "transcript_available"
    ]:

        st.success(
            "AI explanation generated using available video captions."
        )

    else:

        st.warning(
            "Video captions were unavailable. "
            "The AI explanation uses the title and description only."
        )

    st.markdown(
        saved_summary["summary"]
    )

    st.caption(
        "Information source: "
        + saved_summary["source"]
    )

    # ------------------------------------------------------
    # REGENERATE SUMMARY
    # ------------------------------------------------------

    if st.button(
        f"🔄 Regenerate {video_label} Summary",
        key=f"regenerate_summary_{video_id}",
    ):

        st.session_state.pop(
            summary_key,
            None,
        )

        st.rerun()


# ==========================================================
# SENTIMENT COMPARISON CHART
# ==========================================================

def show_sentiment_comparison(
    summary1,
    summary2,
):

    chart_data = pd.DataFrame({

        "Video": [

            "Video 1",
            "Video 1",
            "Video 1",

            "Video 2",
            "Video 2",
            "Video 2",

        ],

        "Sentiment": [

            "Positive",
            "Negative",
            "Neutral",

            "Positive",
            "Negative",
            "Neutral",

        ],

        "Percentage": [

            summary1["positive_percentage"],
            summary1["negative_percentage"],
            summary1["neutral_percentage"],

            summary2["positive_percentage"],
            summary2["negative_percentage"],
            summary2["neutral_percentage"],

        ],

    })

    fig = px.bar(

        chart_data,

        x="Sentiment",

        y="Percentage",

        color="Video",

        barmode="group",

        title="Audience Sentiment Comparison",

        text_auto=".1f",

    )

    fig.update_layout(

        yaxis_title="Comments (%)",

        xaxis_title="Sentiment",

        legend_title="Video",

    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ==========================================================
# EMOTION COMPARISON
# ==========================================================

def show_emotion_comparison(
    df1,
    df2,
):

    emotion1 = (
        df1["emotion"]
        .value_counts()
        .rename("Video 1")
    )

    emotion2 = (
        df2["emotion"]
        .value_counts()
        .rename("Video 2")
    )

    emotion_data = pd.concat(

        [
            emotion1,
            emotion2,
        ],

        axis=1,

    ).fillna(0)

    emotion_data.index.name = "Emotion"

    emotion_data = (
        emotion_data
        .reset_index()
        .melt(

            id_vars="Emotion",

            var_name="Video",

            value_name="Comments",

        )
    )

    fig = px.bar(

        emotion_data,

        x="Emotion",

        y="Comments",

        color="Video",

        barmode="group",

        title="Audience Emotion Comparison",

    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ==========================================================
# COMPARISON SUMMARY
# ==========================================================

def show_comparison_summary(
    summary1,
    summary2,
):

    st.subheader(
        "🏆 Comparison Summary"
    )

    # ------------------------------------------------------
    # POSITIVE SENTIMENT
    # ------------------------------------------------------

    if (
        summary1["positive_percentage"]
        >
        summary2["positive_percentage"]
    ):

        st.success(
            "Video 1 has a higher positive sentiment "
            "percentage among the analyzed comments."
        )

    elif (
        summary2["positive_percentage"]
        >
        summary1["positive_percentage"]
    ):

        st.success(
            "Video 2 has a higher positive sentiment "
            "percentage among the analyzed comments."
        )

    else:

        st.info(
            "Both videos have the same positive sentiment percentage."
        )

    # ------------------------------------------------------
    # NEGATIVE SENTIMENT
    # ------------------------------------------------------

    if (
        summary1["negative_percentage"]
        >
        summary2["negative_percentage"]
    ):

        st.warning(
            "Video 1 has a higher negative sentiment "
            "percentage among the analyzed comments."
        )

    elif (
        summary2["negative_percentage"]
        >
        summary1["negative_percentage"]
    ):

        st.warning(
            "Video 2 has a higher negative sentiment "
            "percentage among the analyzed comments."
        )

    else:

        st.info(
            "Both videos have the same negative sentiment percentage."
        )


# ==========================================================
# DOWNLOAD COMPARISON
# ==========================================================

def show_download_comparison(
    df1,
    df2,
):

    st.subheader(
        "📥 Download Comparison"
    )

    export1 = df1.copy()

    export1["video"] = "Video 1"

    export2 = df2.copy()

    export2["video"] = "Video 2"

    combined_df = pd.concat(

        [
            export1,
            export2,
        ],

        ignore_index=True,

    )

    csv_data = combined_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="Download Comparison CSV",

        data=csv_data,

        file_name="youtube_video_comparison.csv",

        mime="text/csv",

        use_container_width=True,

    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show():

    st.title(
        "⚖️ YouTube Video Comparison"
    )

    st.markdown(
        """
        Compare two YouTube videos using:

        - AI video content explanations
        - Audience sentiment analysis
        - Emotion analysis
        - Video statistics
        - Comparison charts
        """
    )

    st.info(
        "This page analyzes up to 100 comments per video. "
        "Results represent the fetched comments, not the entire audience."
    )

    st.divider()

    # ------------------------------------------------------
    # VIDEO INPUTS
    # ------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        url1 = st.text_input(

            "📺 First YouTube Video",

            placeholder="Paste first YouTube URL",

            key="comparison_url_1",

        )

    with col2:

        url2 = st.text_input(

            "📺 Second YouTube Video",

            placeholder="Paste second YouTube URL",

            key="comparison_url_2",

        )

    # ------------------------------------------------------
    # ANALYZE BUTTON
    # ------------------------------------------------------

    if st.button(

        "🔍 Compare Videos",

        type="primary",

        use_container_width=True,

    ):

        if not url1.strip() or not url2.strip():

            st.warning(
                "Please enter both YouTube video URLs."
            )

            return

        try:

            api = YouTubeAPI()

            # ----------------------------------------------
            # FIRST VIDEO
            # ----------------------------------------------

            with st.spinner(
                "Analyzing Video 1 comments..."
            ):

                details1, df1 = analyze_video(
                    url1,
                    api,
                )

            # ----------------------------------------------
            # SECOND VIDEO
            # ----------------------------------------------

            with st.spinner(
                "Analyzing Video 2 comments..."
            ):

                details2, df2 = analyze_video(
                    url2,
                    api,
                )

            # ----------------------------------------------
            # SAVE RESULTS
            # ----------------------------------------------

            st.session_state[
                "comparison_video_1"
            ] = {

                "details": details1,

                "data": df1,

            }

            st.session_state[
                "comparison_video_2"
            ] = {

                "details": details2,

                "data": df2,

            }

            st.success(
                "Both videos analyzed successfully."
            )

        except Exception as error:

            st.error(
                f"Comparison failed: {error}"
            )

            return

    # ------------------------------------------------------
    # LOAD SAVED RESULTS
    # ------------------------------------------------------

    video1 = st.session_state.get(
        "comparison_video_1"
    )

    video2 = st.session_state.get(
        "comparison_video_2"
    )

    if not video1 or not video2:

        st.info(
            "Enter two YouTube URLs and click Compare Videos."
        )

        return

    # ------------------------------------------------------
    # VIDEO DATA
    # ------------------------------------------------------

    details1 = video1["details"]

    df1 = video1["data"]

    details2 = video2["details"]

    df2 = video2["data"]

    # ------------------------------------------------------
    # VIDEO OVERVIEW
    # ------------------------------------------------------

    st.divider()

    st.header(
        "🎬 Video Overview"
    )

    left, right = st.columns(2)

    with left:

        summary1 = display_video(

            details1,

            df1,

            "Video 1",

        )

        st.divider()

        generate_video_content_explanation(

            details1,

            "Video 1",

        )

    with right:

        summary2 = display_video(

            details2,

            df2,

            "Video 2",

        )

        st.divider()

        generate_video_content_explanation(

            details2,

            "Video 2",

        )

    # ------------------------------------------------------
    # SENTIMENT COMPARISON
    # ------------------------------------------------------

    st.divider()

    st.header(
        "📊 Sentiment Comparison"
    )

    show_sentiment_comparison(

        summary1,

        summary2,

    )

    # ------------------------------------------------------
    # EMOTION COMPARISON
    # ------------------------------------------------------

    st.divider()

    st.header(
        "😊 Emotion Comparison"
    )

    show_emotion_comparison(

        df1,

        df2,

    )

    # ------------------------------------------------------
    # COMPARISON SUMMARY
    # ------------------------------------------------------

    st.divider()

    show_comparison_summary(

        summary1,

        summary2,

    )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    st.divider()

    show_download_comparison(

        df1,

        df2,

    )
