import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.youtube_helper import extract_video_id
from api.video_details import get_video_details
from api.comments_api import get_comments

from preprocessing.clean_text import clean_text
from analytics.sentiment import predict_sentiment
from analytics.emotions import predict_emotion

from database import save_analysis


def show():

    st.title("📺 YouTube Analyzer")
    st.write("Paste a YouTube video URL to analyze comments.")

    url = st.text_input("YouTube URL")

    if st.button("Analyze"):

        # Check URL
        if not url:
            st.warning("Please enter a YouTube URL.")
            return

        # Extract Video ID
        video_id = extract_video_id(url)

        if video_id is None:
            st.error("Invalid YouTube URL.")
            return

        st.success("Video ID Extracted Successfully!")
        st.code(video_id)

        # Get Video Details
        details = get_video_details(video_id)

        if details is None:
            st.error("Could not fetch video details.")
            return

        # Display Video Details
        st.subheader("🎬 Video Information")

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(details["thumbnail"], width=220)

        with col2:
            st.write("###", details["title"])
            st.write("**Channel:**", details["channel"])
            st.write("**Views:**", f"{int(details['views']):,}")
            st.write("**Likes:**", f"{int(details['likes']):,}")
            st.write("**Comments:**", f"{int(details['comments']):,}")
            st.write("**Published:**", details["published"][:10])

        # Download Comments
        st.info("Downloading comments...")

        comments = get_comments(video_id)

        if comments is None or len(comments) == 0:
            st.error("No comments found.")
            return

        df = pd.DataFrame(comments, columns=["comment"])

        # Clean Comments
        df["clean_comment"] = df["comment"].apply(clean_text)

        # Sentiment Analysis
        sentiments = df["clean_comment"].apply(predict_sentiment)

        df["sentiment"] = sentiments.apply(lambda x: x["sentiment"])
        df["confidence"] = sentiments.apply(lambda x: x["score"])

        # Emotion Analysis
        emotions = df["clean_comment"].apply(predict_emotion)

        df["emotion"] = emotions.apply(lambda x: x["emotion"])
        df["emotion_score"] = emotions.apply(lambda x: x["score"])

        # Store dataframe for other pages
        st.session_state["analysis_df"] = df

        st.success("Analysis Completed Successfully!")

        # Summary
        st.header("📊 Summary")

        positive = len(df[df["sentiment"] == "positive"])
        neutral = len(df[df["sentiment"] == "neutral"])
        negative = len(df[df["sentiment"] == "negative"])

        # Save to Database
        save_analysis(
            source="YouTube",
            title=details["title"],
            positive=positive,
            neutral=neutral,
            negative=negative,
            emotion=df["emotion"].mode()[0]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("😊 Positive", positive)
        c2.metric("😐 Neutral", neutral)
        c3.metric("😡 Negative", negative)

        # Pie Chart
        st.subheader("Sentiment Distribution")

        fig, ax = plt.subplots(figsize=(5, 5))

        df["sentiment"].value_counts().plot.pie(
            autopct="%1.1f%%",
            ax=ax
        )

        ax.set_ylabel("")

        st.pyplot(fig)

        # Emotion Chart
        st.subheader("Emotion Distribution")

        st.bar_chart(df["emotion"].value_counts())

        # Comments Table
        st.subheader("Comments")

        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name="youtube_analysis.csv",
            mime="text/csv"
        )