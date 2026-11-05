
import pandas as pd
import streamlit as st

from services.youtube_api import YouTubeAPI, MAX_COMMENTS
from services.analyzer import analyze_text
from services.video_summary import (
    fetch_video_transcript,
    generate_video_summary,
)
from views.history import save_history


def show():
    st.title("📺 YouTube Analyzer")
    st.caption(
        "Understand the video content with AI and analyze "
        "audience reactions separately."
    )

    # ------------------------------------------------------
    # INPUT
    # ------------------------------------------------------
    url = st.text_input(
        "YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_video_url",
    )

    if not st.button(
        "🔍 Analyze Video",
        type="primary",
        use_container_width=True,
    ):
        st.info(
            "Enter a public YouTube video URL to get a content "
            "explanation and analyze its comments."
        )
        return

    if not url.strip():
        st.warning("Please enter a YouTube video URL.")
        return

    # ------------------------------------------------------
    # FETCH VIDEO DETAILS
    # ------------------------------------------------------
    try:
        api = YouTubeAPI()

        with st.spinner("Fetching video information..."):
            details = api.get_video_details(url)

        if not details:
            st.error("Could not find the video. Check the URL.")
            return

    except Exception as exc:
        st.error(f"Could not fetch video information: {exc}")
        return

    video_id = details.get("video_id", "")
    title = details.get("title", "Unknown title")
    description = details.get("description", "")
    channel = details.get("channel", "Unknown channel")

    st.session_state.youtube_details = details
    st.session_state.video_details = details

    # ------------------------------------------------------
    # VIDEO OVERVIEW
    # ------------------------------------------------------
    st.header("🎬 Video Overview")

    left, right = st.columns([1, 2])

    with left:
        if details.get("thumbnail"):
            st.image(
                details["thumbnail"],
                use_container_width=True,
            )

    with right:
        st.subheader(title)
        st.write(f"**Channel:** {channel}")
        st.write(f"**Views:** {details.get('views', 0):,}")
        st.write(f"**Likes:** {details.get('likes', 0):,}")
        st.write(f"**Published:** {details.get('published', 'Unknown')}")
        st.write(f"**Duration:** {details.get('duration', 'Unknown')}")

    with st.expander("📄 Original video description"):
        if description.strip():
            st.write(description)
        else:
            st.info("The video does not have an available description.")

    st.divider()

    # ------------------------------------------------------
    # VIDEO CONTENT SUMMARY — NOT COMMENT SUMMARY
    # ------------------------------------------------------
    st.header("🧠 AI Video Content Explanation")

    st.write(
        "This section explains what the video itself is about. "
        "It does not use viewer comments to generate the explanation."
    )

    summary_key = f"video_content_summary_{video_id}"

    if summary_key not in st.session_state:
        with st.spinner(
            "Retrieving captions and generating the video explanation..."
        ):
            transcript = fetch_video_transcript(video_id)

            result = generate_video_summary(
                title=title,
                description=description,
                transcript=transcript,
            )

        st.session_state[summary_key] = {
            "result": result,
            "transcript_available": bool(transcript),
        }

    saved_summary = st.session_state[summary_key]
    summary_result = saved_summary["result"]

    if saved_summary["transcript_available"]:
        st.success("Video explanation generated from available captions.")
    else:
        st.warning(
            "A transcript was unavailable. The explanation below uses "
            "the title and description only, so it may not cover the "
            "full video."
        )

    st.markdown(summary_result.get("summary", "No explanation generated."))

    st.caption(
        f"Information source: {summary_result.get('source', 'Unknown')}"
    )

    if st.button(
        "🔄 Regenerate Video Explanation",
        key=f"regenerate_summary_{video_id}",
    ):
        st.session_state.pop(summary_key, None)
        st.rerun()

    st.divider()

    # ------------------------------------------------------
    # COMMENT ANALYSIS — SEPARATE FEATURE
    # ------------------------------------------------------
    st.header("💬 Audience Comment Analysis")

    st.write(
        "The following results describe viewer reactions, not "
        "the actual contents of the video."
    )

    try:
        with st.spinner("Fetching YouTube comments..."):
            comments = api.get_comments(video_id, MAX_COMMENTS)

    except Exception as exc:
        st.warning(f"Could not retrieve comments: {exc}")
        return

    if not comments:
        st.info(
            "No comments were available. The video explanation above "
            "can still be used independently."
        )
        return

    st.write(f"Fetched **{len(comments):,}** comments.")

    analyzed_comments = []
    progress = st.progress(0)
    status = st.empty()
    total = len(comments)

    for index, comment in enumerate(comments, start=1):
        comment_text = str(comment.get("text", "")).strip()

        if comment_text:
            try:
                prediction = analyze_text(comment_text)

                analyzed_comments.append({
                    "author": comment.get("author", "Unknown"),
                    "text": comment_text,
                    "likes": comment.get("likes", 0),
                    "published": comment.get("published", ""),
                    "sentiment": prediction.get("sentiment", "unknown"),
                    "sentiment_score": prediction.get(
                        "sentiment_score", 0.0
                    ),
                    "emotion": prediction.get("emotion", "unknown"),
                    "emotion_score": prediction.get(
                        "emotion_score", 0.0
                    ),
                })

            except Exception:
                analyzed_comments.append({
                    "author": comment.get("author", "Unknown"),
                    "text": comment_text,
                    "likes": comment.get("likes", 0),
                    "published": comment.get("published", ""),
                    "sentiment": "unknown",
                    "sentiment_score": 0.0,
                    "emotion": "unknown",
                    "emotion_score": 0.0,
                })

        progress.progress(index / total)

        if index % 100 == 0 or index == total:
            status.caption(f"Analyzed {index:,} / {total:,} comments")

    progress.empty()
    status.empty()

    df = pd.DataFrame(analyzed_comments)

    if df.empty:
        st.warning("No comments could be analyzed.")
        return

    st.session_state.analysis_df = df
    st.session_state.youtube_comments = comments

    # ------------------------------------------------------
    # SENTIMENT METRICS
    # ------------------------------------------------------
    sentiments = df["sentiment"].astype(str).str.lower()

    valid_sentiments = sentiments[
        sentiments.isin(["positive", "neutral", "negative"])
    ]

    counts = valid_sentiments.value_counts()

    positive = int(counts.get("positive", 0))
    neutral = int(counts.get("neutral", 0))
    negative = int(counts.get("negative", 0))

    if not valid_sentiments.empty:
        dominant_sentiment = valid_sentiments.mode().iloc[0]
    else:
        dominant_sentiment = "unknown"

    emotions = df["emotion"].astype(str).str.lower()
    valid_emotions = emotions[emotions != "unknown"]

    if not valid_emotions.empty:
        dominant_emotion = valid_emotions.mode().iloc[0]
    else:
        dominant_emotion = "unknown"

    st.subheader("📊 Audience Sentiment")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Analyzed comments", f"{len(df):,}")
    c2.metric("😊 Positive", f"{positive:,}")
    c3.metric("😐 Neutral", f"{neutral:,}")
    c4.metric("😟 Negative", f"{negative:,}")

    st.info(
        f"**Dominant sentiment:** {dominant_sentiment.capitalize()}  \n"
        f"**Dominant emotion:** {dominant_emotion.capitalize()}"
    )

    # ------------------------------------------------------
    # CHARTS
    # ------------------------------------------------------
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("**Sentiment distribution**")
        st.bar_chart(
            counts.reindex(
                ["positive", "neutral", "negative"],
                fill_value=0,
            )
        )

    with chart2:
        st.markdown("**Most common emotions**")
        if not valid_emotions.empty:
            st.bar_chart(valid_emotions.value_counts().head(8))
        else:
            st.info("No valid emotion predictions were available.")

    # ------------------------------------------------------
    # MOST-LIKED COMMENTS
    # ------------------------------------------------------
    st.subheader("⭐ Most-Liked Comments")

    df["likes"] = pd.to_numeric(
        df["likes"],
        errors="coerce",
    ).fillna(0)

    top_comments = df.nlargest(10, "likes")

    st.dataframe(
        top_comments[
            ["author", "text", "likes", "sentiment", "emotion"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------
    # ALL COMMENTS
    # ------------------------------------------------------
    with st.expander("View all analyzed comments"):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------
    st.download_button(
        "⬇️ Download Comment Analysis CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="youtube_comment_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------
    try:
        save_history(
            analysis_type="YouTube",
            records_count=len(df),
            sentiment=dominant_sentiment.capitalize(),
            emotion=dominant_emotion.capitalize(),
            source_name=title,
        )
    except Exception as exc:
        st.warning(f"Comments were analyzed, but History could not be saved: {exc}")

    st.success("YouTube content explanation and comment analysis completed.")


show_youtube = show
