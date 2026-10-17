import streamlit as st
import pandas as pd

from preprocessing.clean_text import clean_text
from analytics.sentiment import predict_sentiment
from analytics.emotions import predict_emotion
save_analysis(
    source="CSV",
    title="Uploaded CSV",
    positive=positive,
    neutral=neutral,
    negative=negative,
    emotion=df["emotion"].mode()[0]
)


def show():

    st.title("📂 CSV Upload & Analysis")

    st.write("Upload a CSV file containing comments or text.")

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("Please upload a CSV file.")
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return

    st.subheader("Preview")

    st.dataframe(df.head())

    columns = list(df.columns)

    text_column = st.selectbox(
        "Select Text Column",
        columns
    )

    if st.button("Analyze CSV"):

        st.info("Cleaning text...")

        df["clean_text"] = df[text_column].astype(str).apply(clean_text)

        st.info("Running Sentiment Analysis...")

        sentiments = df["clean_text"].apply(predict_sentiment)

        df["sentiment"] = sentiments.apply(lambda x: x["sentiment"])
        df["confidence"] = sentiments.apply(lambda x: x["score"])

        st.info("Running Emotion Detection...")

        emotions = df["clean_text"].apply(predict_emotion)

        df["emotion"] = emotions.apply(lambda x: x["emotion"])
        df["emotion_score"] = emotions.apply(lambda x: x["score"])
        st.session_state["analysis_df"] = df
        st.success("Analysis Completed!")

        st.subheader("Results")

        st.dataframe(df)

        st.subheader("Sentiment Distribution")

        st.bar_chart(df["sentiment"].value_counts())

        st.subheader("Emotion Distribution")

        st.bar_chart(df["emotion"].value_counts())

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Results",
            data=csv,
            file_name="analysis_results.csv",
            mime="text/csv"
        )