import streamlit as st

from services.ollama_service import ask_ai


# ==========================================================
# AI SOCIAL MEDIA ASSISTANT
# ==========================================================

def show():

    st.title("🤖 AI Social Media Assistant")

    st.markdown(
        "Ask anything about your YouTube, Text, or CSV analysis."
    )

    # ======================================================
    # Check Dataset
    # ======================================================

    if "analysis_df" not in st.session_state:

        st.warning(
            "⚠️ Please analyze YouTube, Text, or CSV data first."
        )

        return

    df = st.session_state.analysis_df

    # ======================================================
    # Chat History
    # ======================================================

    if "messages" not in st.session_state:

        st.session_state.messages = []

    # Display previous messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )

    # ======================================================
    # User Input
    # ======================================================

    prompt = st.chat_input(
        "Ask anything about your analysis..."
    )

    if prompt:

        # --------------------------------------------------
        # Add user message
        # --------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):

            st.markdown(prompt)

        # --------------------------------------------------
        # Ask AI Assistant
        # --------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 AI is analyzing your data..."
            ):

                answer = ask_ai(
                    prompt,
                    df
                )

            st.markdown(answer)

        # --------------------------------------------------
        # Save assistant response
        # --------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    # ======================================================
    # Suggested Questions
    # ======================================================

    st.divider()

    st.subheader("💡 Suggested Questions")

    col1, col2 = st.columns(2)

    # ------------------------------------------------------
    # Column 1
    # ------------------------------------------------------

    with col1:

        st.markdown(
            """
            - Summarize the comments.
            - Why are people unhappy?
            - Which emotion is dominant?
            - Explain audience sentiment.
            - Is this content successful?
            """
        )

    # ------------------------------------------------------
    # Column 2
    # ------------------------------------------------------

    with col2:

        st.markdown(
            """
            - Give marketing ideas.
            - Suggest improvements.
            - Predict engagement.
            - What should the creator do next?
            - Recommend future content.
            """
        )

    # ======================================================
    # Clear Conversation
    # ======================================================

    st.divider()

    if st.button(
        "🗑️ Clear Conversation"
    ):

        st.session_state.messages = []

        st.rerun()