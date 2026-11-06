
import streamlit as st
import pandas as pd

from services.ollama_service import ask_ai


def get_analysis_data():
    """
    Get the current analysis dataframe from Streamlit session state.
    """

    possible_keys = [
        "analysis_df",
        "universal_analysis_df",
        "df",
    ]

    for key in possible_keys:
        data = st.session_state.get(key)

        if isinstance(data, pd.DataFrame) and not data.empty:
            return data.copy()

    return None


def show():

    st.title("💡 AI Recommendations")

    st.markdown(
        """
        Get AI-powered suggestions based on your analyzed
        social media comments.

        Discover audience preferences, identify problems,
        and find ways to improve your content.
        """
    )

    st.divider()

    # Load current analysis
    df = get_analysis_data()

    if df is None:

        st.warning(
            "No analysis data found. Please analyze a YouTube "
            "video, text, or CSV file first."
        )

        return

    # Dataset overview
    st.subheader("📊 Analysis Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Comments",
            len(df)
        )

    with col2:
        st.metric(
            "Available Columns",
            len(df.columns)
        )

    # Display available data
    with st.expander("View Analysis Data"):

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Recommendation options
    st.subheader("🎯 Generate Recommendations")

    recommendation_type = st.selectbox(
        "Choose recommendation type",
        [
            "Overall Content Improvement",
            "Audience Preferences",
            "Negative Feedback Solutions",
            "Content Ideas",
            "Engagement Improvement",
        ],
    )

    questions = {
        "Overall Content Improvement":
            "Analyze the audience comments and recommend "
            "practical ways to improve the content.",

        "Audience Preferences":
            "Identify audience preferences and explain "
            "what viewers appear to appreciate.",

        "Negative Feedback Solutions":
            "Analyze negative feedback and suggest "
            "practical solutions to recurring problems.",

        "Content Ideas":
            "Suggest future content ideas based on "
            "the available audience comments.",

        "Engagement Improvement":
            "Suggest ways to improve audience engagement "
            "based on the available analysis.",
    }

    if st.button(
        "🤖 Generate AI Recommendations",
        use_container_width=True,
    ):

        question = questions[recommendation_type]

        with st.spinner(
            "AI is analyzing your audience comments..."
        ):

            result = ask_ai(
                question,
                df
            )

        st.session_state[
            "ai_recommendations_result"
        ] = result

        st.session_state[
            "ai_recommendations_type"
        ] = recommendation_type

    # Display generated recommendations
    result = st.session_state.get(
        "ai_recommendations_result"
    )

    if result:

        st.divider()

        st.subheader(
            "🧠 Generated Recommendations"
        )

        st.caption(
            st.session_state.get(
                "ai_recommendations_type",
                "AI Recommendations"
            )
        )

        st.markdown(result)

        st.info(
            "Recommendations are generated from the "
            "available analysis data. Review them before "
            "making content decisions."
        )
