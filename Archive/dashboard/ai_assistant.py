import streamlit as st

def show():

    st.title("🤖 AI Assistant")

    if "analysis_df" not in st.session_state:
        st.warning("Analyze a YouTube video, CSV, or text first.")
        return

    df = st.session_state["analysis_df"]

    question = st.text_input("Ask about your analysis")

    if st.button("Ask AI"):

        positive = len(df[df["sentiment"] == "positive"])
        negative = len(df[df["sentiment"] == "negative"])
        neutral = len(df[df["sentiment"] == "neutral"])

        top_emotion = df["emotion"].mode()[0]

        answer = ""

        q = question.lower()

        if "mood" in q or "sentiment" in q:
            if positive >= neutral and positive >= negative:
                answer = "😊 Overall audience sentiment is Positive."
            elif negative >= positive:
                answer = "😡 Overall audience sentiment is Negative."
            else:
                answer = "😐 Overall audience sentiment is Neutral."

        elif "emotion" in q:
            answer = f"😊 Dominant emotion is {top_emotion}."

        elif "recommend" in q:
            answer = (
                "📈 Recommendation: Continue creating content "
                "similar to the videos receiving the highest positive engagement."
            )

        else:
            answer = (
                "I can answer questions about sentiment, emotions, "
                "recommendations, and audience mood."
            )

        st.success(answer)