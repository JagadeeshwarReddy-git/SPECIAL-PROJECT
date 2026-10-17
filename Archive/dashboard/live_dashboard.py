import streamlit as st
import pandas as pd

def show():

    st.title("📈 Live Analytics Dashboard")

    if "analysis_df" not in st.session_state:
        st.warning("Analyze some data first.")
        return

    df = st.session_state["analysis_df"]

    total = len(df)
    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📄 Total", total)
    col2.metric("😊 Positive", positive)
    col3.metric("😐 Neutral", neutral)
    col4.metric("😡 Negative", negative)

    st.divider()

    st.subheader("📊 Sentiment")

    st.bar_chart(df["sentiment"].value_counts())

    st.subheader("😊 Emotion")

    st.bar_chart(df["emotion"].value_counts())

    st.subheader("📋 Latest Records")

    st.dataframe(df.tail(20), use_container_width=True)