import streamlit as st
import pandas as pd

from services.youtube_api import (
    YouTubeAPI,
    MAX_COMMENTS
)

from services.analyzer import analyze_text
from views.history import save_history


# ==========================================================
# YOUTUBE ANALYZER
# ==========================================================

def show():

    # ======================================================
    # PAGE HEADER
    # ======================================================

    st.title("📺 YouTube Analyzer")

    st.caption(
        "Analyze a YouTube video and understand "
        "what viewers are saying."
    )

    # ======================================================
    # URL INPUT
    # ======================================================

    url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="Paste a YouTube video URL here..."
    )

    analyze_button = st.button(
        "🔍 Analyze Video",
        use_container_width=True,
        type="primary"
    )

    # ======================================================
    # BEFORE ANALYSIS
    # ======================================================

    if not analyze_button:

        st.info(
            "Paste a public YouTube video URL to analyze "
            "available audience comments."
        )

        return

    # ======================================================
    # VALIDATE URL
    # ======================================================

    if not url.strip():

        st.warning(
            "Please enter a YouTube video URL."
        )

        return

    try:

        # ==================================================
        # CREATE API
        # ==================================================

        api = YouTubeAPI()

        # ==================================================
        # VIDEO DETAILS
        # ==================================================

        with st.spinner(
            "Fetching YouTube video details..."
        ):

            details = api.get_video_details(url)

        if details is None:

            st.error(
                "❌ Could not find the YouTube video.\n\n"
                "Please check the URL and try again."
            )

            return

        st.session_state.youtube_details = details
        st.session_state.video_details = details

        # ==================================================
        # VIDEO OVERVIEW
        # ==================================================

        st.subheader(
            "🎬 Video Overview"
        )

        left, right = st.columns(
            [1, 2]
        )

        with left:

            if details.get("thumbnail"):

                st.image(
                    details["thumbnail"],
                    use_container_width=True
                )

        with right:

            st.markdown(
                f"### {details.get('title', 'Unknown Title')}"
            )

            st.write(
                f"**Channel:** "
                f"{details.get('channel', 'Unknown')}"
            )

            st.write(
                f"**Views:** "
                f"{details.get('views', 0):,}"
            )

            st.write(
                f"**Likes:** "
                f"{details.get('likes', 0):,}"
            )

            st.write(
                f"**YouTube Comments:** "
                f"{details.get('comments', 0):,}"
            )

            st.write(
                f"**Published:** "
                f"{details.get('published', 'Unknown')}"
            )

        st.divider()

        # ==================================================
        # FETCH COMMENTS
        # ==================================================

        st.subheader(
            "💬 Audience Comments"
        )

        try:

            with st.spinner(
                "Fetching audience comments..."
            ):

                comments = api.get_comments(
                    details["video_id"],
                    MAX_COMMENTS
                )

        except Exception as e:

            error_message = str(e)

            if (
                "commentsDisabled" in error_message
                or
                "disabled comments" in error_message.lower()
            ):

                st.warning(
                    "⚠️ Comments are disabled for this video."
                )

                st.info(
                    "The video information was fetched "
                    "successfully, but YouTube does not allow "
                    "this application to retrieve comments "
                    "for this video."
                )

            else:

                st.error(
                    "❌ Unable to fetch comments.\n\n"
                    f"{error_message}"
                )

            return

        # ==================================================
        # NO COMMENTS
        # ==================================================

        if not comments:

            st.warning(
                "No comments were available for this video."
            )

            return

        # ==================================================
        # FETCHED COUNT
        # ==================================================

        fetched_count = len(comments)

        st.success(
            f"✅ {fetched_count:,} comments fetched successfully."
        )

        if fetched_count < MAX_COMMENTS:

            st.caption(
                f"YouTube returned {fetched_count:,} available "
                "top-level comments."
            )

        else:

            st.caption(
                "All available comments within the analysis limit "
                "were retrieved."
            )

        # ==================================================
        # ANALYSIS
        # ==================================================

        st.subheader(
            "🧠 Comment Analysis"
        )

        st.write(
            f"Analyzing all **{fetched_count:,} fetched comments** "
            "for sentiment and emotion."
        )

        analyzed_comments = []

        progress = st.progress(0)
        status = st.empty()

        total_comments = len(comments)

        # ==================================================
        # ANALYZE EACH COMMENT
        # ==================================================

        for number, comment in enumerate(
            comments,
            start=1
        ):

            text = str(
                comment.get(
                    "text",
                    ""
                )
            ).strip()

            # Skip empty comments
            if not text:

                progress.progress(
                    number / total_comments
                )

                continue

            try:

                result = analyze_text(text)

                analyzed_comments.append({

                    "author":
                        comment.get(
                            "author",
                            "Unknown"
                        ),

                    "text":
                        text,

                    "likes":
                        comment.get(
                            "likes",
                            0
                        ),

                    "published":
                        comment.get(
                            "published",
                            ""
                        ),

                    "sentiment":
                        result.get(
                            "sentiment",
                            "unknown"
                        ),

                    "sentiment_score":
                        result.get(
                            "sentiment_score",
                            0.0
                        ),

                    "emotion":
                        result.get(
                            "emotion",
                            "unknown"
                        ),

                    "emotion_score":
                        result.get(
                            "emotion_score",
                            0.0
                        )
                })

            except Exception:

                # Keep the comment even if model
                # analysis fails
                analyzed_comments.append({

                    "author":
                        comment.get(
                            "author",
                            "Unknown"
                        ),

                    "text":
                        text,

                    "likes":
                        comment.get(
                            "likes",
                            0
                        ),

                    "published":
                        comment.get(
                            "published",
                            ""
                        ),

                    "sentiment":
                        "unknown",

                    "sentiment_score":
                        0.0,

                    "emotion":
                        "unknown",

                    "emotion_score":
                        0.0
                })

            # Progress
            progress.progress(
                number / total_comments
            )

            # Update progress text every 100 comments
            if (
                number == 1
                or number % 100 == 0
                or number == total_comments
            ):

                status.caption(
                    f"Analyzing "
                    f"{number:,} / "
                    f"{total_comments:,} comments"
                )

        progress.empty()
        status.empty()

        # ==================================================
        # DATAFRAME
        # ==================================================

        df = pd.DataFrame(
            analyzed_comments
        )

        if df.empty:

            st.error(
                "No comments could be analyzed."
            )

            return

        # ==================================================
        # SAVE TO SESSION
        # ==================================================

        st.session_state.analysis_df = df
        st.session_state.youtube_comments = comments

        # ==================================================
        # SENTIMENT
        # ==================================================

        sentiments = (
            df["sentiment"]
            .astype(str)
            .str.lower()
        )

        positive = int(
            sentiments
            .eq("positive")
            .sum()
        )

        neutral = int(
            sentiments
            .eq("neutral")
            .sum()
        )

        negative = int(
            sentiments
            .eq("negative")
            .sum()
        )

        # ==================================================
        # DOMINANT SENTIMENT
        # ==================================================

        valid_sentiments = (
            sentiments[
                sentiments.isin(
                    [
                        "positive",
                        "neutral",
                        "negative"
                    ]
                )
            ]
        )

        if not valid_sentiments.empty:

            dominant_sentiment = (
                valid_sentiments
                .mode()
                .iloc[0]
            )

        else:

            dominant_sentiment = "unknown"

        # ==================================================
        # DOMINANT EMOTION
        # ==================================================

        emotions = (
            df["emotion"]
            .astype(str)
            .str.lower()
        )

        emotions = emotions[
            emotions != "unknown"
        ]

        if not emotions.empty:

            dominant_emotion = (
                emotions
                .mode()
                .iloc[0]
            )

        else:

            dominant_emotion = "unknown"

        # ==================================================
        # SUMMARY
        # ==================================================

        st.subheader(
            "📊 Audience Summary"
        )

        c1, c2, c3, c4 = st.columns(
            4
        )

        c1.metric(
            "💬 Analyzed",
            f"{len(df):,}"
        )

        c2.metric(
            "😊 Positive",
            f"{positive:,}"
        )

        c3.metric(
            "😐 Neutral",
            f"{neutral:,}"
        )

        c4.metric(
            "😟 Negative",
            f"{negative:,}"
        )

        st.info(
            f"**Dominant Sentiment:** "
            f"{dominant_sentiment.capitalize()}"
            "   •   "
            f"**Dominant Emotion:** "
            f"{dominant_emotion.capitalize()}"
        )

        # ==================================================
        # CHARTS
        # ==================================================

        st.subheader(
            "📈 Audience Reaction"
        )

        chart1, chart2 = st.columns(
            2
        )

        with chart1:

            st.markdown(
                "**Sentiment Distribution**"
            )

            sentiment_counts = (
                sentiments
                .value_counts()
                .reindex(
                    [
                        "positive",
                        "neutral",
                        "negative"
                    ]
                )
                .fillna(0)
            )

            st.bar_chart(
                sentiment_counts
            )

        with chart2:

            st.markdown(
                "**Top Emotions**"
            )

            emotion_counts = (
                emotions
                .value_counts()
                .head(8)
            )

            st.bar_chart(
                emotion_counts
            )

        # ==================================================
        # MOST LIKED COMMENTS
        # ==================================================

        st.subheader(
            "⭐ Most-Liked Comments"
        )

        liked = pd.to_numeric(
            df["likes"],
            errors="coerce"
        ).fillna(0)

        top_comments = (
            df.assign(
                _likes=liked
            )
            .sort_values(
                "_likes",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_comments[
                [
                    "author",
                    "text",
                    "likes",
                    "sentiment",
                    "emotion"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        # ==================================================
        # ALL COMMENTS
        # ==================================================

        st.subheader(
            "💬 All Analyzed Comments"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # ==================================================
        # DOWNLOAD
        # ==================================================

        csv = df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇️ Download Analysis",
            data=csv,
            file_name="youtube_comment_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

        # ==================================================
        # HISTORY
        # ==================================================

        save_history(
            analysis_type="YouTube",
            records_count=len(df),
            sentiment=dominant_sentiment.capitalize(),
            emotion=dominant_emotion.capitalize(),
            source_name=details.get(
                "title",
                "YouTube Video"
            )
        )

        st.success(
            f"🎉 YouTube analysis completed for "
            f"{len(df):,} comments and saved to History."
        )

    except Exception as e:

        st.error(
            "❌ Error while analyzing the YouTube video:\n\n"
            f"{e}"
        )


show_youtube = show
