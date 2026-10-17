import streamlit as st
from analytics.sentiment import predict_sentiment
from analytics.emotions import predict_emotion
from preprocessing.clean_text import clean_text
def show():

    st.title("📝 AI Text Analyzer")

    st.write("Paste any social media post or comment.")

    text = st.text_area(
        "Enter text",
        height=200
    )

    if st.button("Analyze Text"):

        if text == "":
            st.warning("Please enter some text.")
            return

        cleaned = clean_text(text)

        sentiment = predict_sentiment(cleaned)

        emotion = predict_emotion(cleaned)

        st.success("Analysis Completed")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Sentiment",
                sentiment["sentiment"]
            )

            st.metric(
                "Confidence",
                f"{sentiment['score']:.2f}"
            )

        with col2:
            st.metric(
                "Emotion",
                emotion["emotion"]
            )

            st.metric(
                "Emotion Score",
                f"{emotion['score']:.2f}"
            )

        st.subheader("Cleaned Text")

        st.write(cleaned)