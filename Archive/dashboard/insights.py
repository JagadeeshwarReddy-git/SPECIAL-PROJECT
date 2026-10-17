import streamlit as st

def show():

    st.title("🧠 AI Insight Engine")

    if "analysis_df" not in st.session_state:
        st.warning("Please analyze a YouTube video, CSV, or text first.")
        return

    df = st.session_state["analysis_df"]

    total = len(df)

    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    top_emotion = df["emotion"].mode()[0]

    st.subheader("📈 Business Insights")

    if positive > negative:
        st.success("Audience reaction is mostly positive.")
    else:
        st.error("Audience reaction needs improvement.")

    st.info(f"Total Comments Analyzed: {total}")
    st.info(f"Dominant Emotion: {top_emotion}")

    st.subheader("💡 Recommendations")

    recommendations = [
        "Create more content on topics receiving positive feedback.",
        "Monitor negative comments to identify recurring issues.",
        "Use the top keywords as hashtags or SEO terms.",
        "Respond to audience questions to increase engagement.",
        "Post similar content consistently."
    ]

    for rec in recommendations:
        st.write("✅", rec)