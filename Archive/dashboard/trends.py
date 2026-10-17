import streamlit as st
import pandas as pd

from analytics.keywords import get_top_keywords
from analytics.summary import generate_summary


def show():

    st.title("📈 Trend Analyzer")

    if "analysis_df" not in st.session_state:
        st.warning("Please analyze some data first.")
        return

    df = st.session_state["analysis_df"]

    st.subheader("🔥 Trending Keywords")

    keywords = get_top_keywords(df["clean_comment"])

    keyword_df = pd.DataFrame(
        keywords,
        columns=["Keyword", "Frequency"]
    )

    st.dataframe(keyword_df, use_container_width=True)

    st.subheader("🤖 AI Insight")

    st.markdown(generate_summary(df))