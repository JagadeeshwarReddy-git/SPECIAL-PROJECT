import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from api.youtube_api import extract_video_id
from api.video_details import get_video_details
from api.comments_api import get_comments

from preprocessing.clean_text import clean_text
from analytics.sentiment import predict_sentiment
from analytics.emotions import predict_emotion


def show():

    st.title("📺 YouTube Analyzer")
    st.write("Paste a YouTube video URL and analyze its comments.")

    url = st.text_input("YouTube URL")

    if st.button("Analyze"):

        # -----------------------
        # Validate URL
        # -----------------------
        if url.strip() == "":
            st.warning("Please enter a YouTube URL.")
            return

        # -----------------------
        # Extract Video ID
        # -----------------------
        video_id = extract_video_id(url)

        if not video_id:
            st.error("Invalid YouTube URL.")
            return

        # -----------------------
        # Get Video Details
        # -----------------------
        details = get_video_details(video_id)

        if details is None:
            st.error("Unable to fetch video details.")
            return

        st.success("Video Found!")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(details["thumbnail"], width=300)

        with col2:
            st.subheader(details["title"])
            st.write("📺 Channel:", details["channel"])
            st.write("👀 Views:", details["views"])
            st.write("👍 Likes:", details["likes"])
            st.write("💬 Comments:", details["comments"])

        # -----------------------
        # Download Comments
        # -----------------------
        with st.spinner("Downloading comments..."):

            comments = get_comments(video_id)

        if comments is None or len(comments) == 0:
            st.error("No comments found.")
            return

        df = pd.DataFrame(comments, columns=["comment"])

        # -----------------------
        # Clean Comments
        # -----------------------
        df["clean_comment"] = df["comment"].apply(clean_text)

        # -----------------------
        # Sentiment Analysis
        # -----------------------
        sentiments = df["clean_comment"].apply(predict_sentiment)

        df["sentiment"] = sentiments.apply(lambda x: x["sentiment"])
        df["confidence"] = sentiments.apply(lambda x: x["score"])

        # -----------------------
        # Emotion Detection
        # -----------------------
        emotions = df["clean_comment"].apply(predict_emotion)

        df["emotion"] = emotions.apply(lambda x: x["emotion"])
        df["emotion_score"] = emotions.apply(lambda x: x["score"])

        st.success("Analysis Completed!")

        # -----------------------
        # Summary
        # -----------------------
        st.header("📊 Analysis Summary")

        positive = len(df[df["sentiment"] == "positive"])
        neutral = len(df[df["sentiment"] == "neutral"])
        negative = len(df[df["sentiment"] == "negative"])

        c1, c2, c3 = st.columns(3)

        c1.metric("😊 Positive", positive)
        c2.metric("😐 Neutral", neutral)
        c3.metric("😡 Negative", negative)

        # -----------------------
        # Pie Chart
        # -----------------------
        st.subheader("Sentiment Distribution")

        fig, ax = plt.subplots(figsize=(5, 5))

        df["sentiment"].value_counts().plot.pie(
            autopct="%1.1f%%",
            startangle=90,
            ax=ax
        )

        ax.set_ylabel("")

        st.pyplot(fig)

        # -----------------------
        # Emotion Chart
        # -----------------------
        st.subheader("Emotion Distribution")

        st.bar_chart(df["emotion"].value_counts())

        # -----------------------
        # Top Comments
        # -----------------------
        st.subheader("Comments")

        st.dataframe(df)

        # -----------------------
        # Download
        # -----------------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            data=csv,
           