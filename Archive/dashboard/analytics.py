from wordcloud import WordCloud
from analytics.summary import generate_summary
from analytics.keywords import get_top_keywords
from analytics.recommendation import generate_recommendation
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show():

    st.title("📊 Analytics Dashboard")

    st.write("Overall sentiment and emotion analysis.")

    if "analysis_df" not in st.session_state:
        st.warning("No analysis available. Please analyze a YouTube video or upload a CSV first.")
        return

    df = st.session_state["analysis_df"]

    # ==========================
    # KPI Cards
    # ==========================

    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    c1, c2, c3 = st.columns(3)

    c1.metric("😊 Positive", positive)
    c2.metric("😐 Neutral", neutral)
    c3.metric("😡 Negative", negative)

    st.divider()

    # ==========================
    # Sentiment Pie Chart
    # ==========================

    st.subheader("Sentiment Distribution")

    fig, ax = plt.subplots(figsize=(5, 5))

    df["sentiment"].value_counts().plot.pie(
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    st.pyplot(fig)

    # ==========================
    # Emotion Chart
    # ==========================

    st.subheader("Emotion Distribution")

    st.bar_chart(df["emotion"].value_counts())

    # ==========================
    # Top Emotions
    # ==========================

    st.subheader("Top Emotions")

    st.dataframe(df["emotion"].value_counts())

    # ==========================
    # Top Sentiments
    # ==========================

    st.subheader("Sentiment Counts")

    st.dataframe(df["sentiment"].value_counts())

    # ==========================
    # Full Data
    # ==========================

    st.subheader("Analyzed Data")

    st.dataframe(df)
    st.divider()

st.subheader("🤖 AI Marketing Recommendation")

recommendations = generate_recommendation(df)

for item in recommendations:
    st.success(item)
    # ----------------------------------
# Word Cloud
# ----------------------------------

st.subheader("☁️ Word Cloud")

text = " ".join(df["clean_comment"].astype(str))

wordcloud = WordCloud(
    width=1200,
    height=500,
    background_color="white"
).generate(text)

fig, ax = plt.subplots(figsize=(14,6))

ax.imshow(wordcloud)

ax.axis("off")

st.pyplot(fig)
# ----------------------------------
# Top Keywords
# ----------------------------------

st.subheader("🔥 Top Keywords")

keywords = get_top_keywords(df["clean_comment"])

keyword_df = pd.DataFrame(
    keywords,
    columns=["Keyword","Frequency"]
)

st.dataframe(
    keyword_df,
    use_container_width=True
)
st.divider()

st.subheader("🤖 AI Executive Summary")

summary = generate_summary(df)

st.markdown(summary)