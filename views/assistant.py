
import streamlit as st
import pandas as pd

from services.ollama_service import ask_ai


# ==========================================================
# SHARED DATA LOADER
# ==========================================================

def get_shared_analysis_data():
    """
    Get the dataset shared by CSV Upload or another analysis page.
    """

    data_keys = (
        "analysis_df",
        "universal_analysis_df",
        "df",
    )

    for key in data_keys:
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


# ==========================================================
# AI SOCIAL MEDIA ASSISTANT
# ==========================================================

def show():

    st.title("🤖 AI Social Media Assistant")

    st.markdown(
        "Ask questions about your YouTube comments, text analysis, "
        "or uploaded CSV dataset."
    )

    # ======================================================
    # LOAD SHARED DATASET
    # ======================================================

    df = get_shared_analysis_data()

    if df is None:

        st.warning(
            "⚠️ No analysis data is available yet. "
            "Please analyze some text, analyze YouTube comments, "
            "or upload a CSV file first."
        )

        if st.button(
            "📂 Go to CSV Upload",
            key="assistant_go_upload",
        ):
            st.session_state["page"] = "📂 CSV Upload"
            st.rerun()

        return

    # ======================================================
    # DATASET OVERVIEW
    # ======================================================

    with st.expander("📊 Current Dataset", expanded=False):

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Records", f"{len(df):,}")

        with col2:
            st.metric("Total Columns", f"{len(df.columns):,}")

        st.write("**Available columns:**")
        st.write(", ".join(str(column) for column in df.columns))

        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True,
        )

    # ======================================================
    # CHAT HISTORY
    # ======================================================

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display previous messages

    for message in st.session_state["messages"]:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ======================================================
    # USER INPUT
    # ======================================================

    prompt = st.chat_input(
        "Ask anything about your analysis..."
    )

    if prompt:

        # Save and display the user message

        st.session_state["messages"].append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        # ==================================================
        # ASK AI ASSISTANT
        # ==================================================

        with st.chat_message("assistant"):

            with st.spinner("🤖 AI is analyzing your data..."):

                try:
                    answer = ask_ai(prompt, df)

                    if answer is None:
                        answer = (
                            "The AI service did not return a response. "
                            "Please try again."
                        )
                    else:
                        answer = str(answer)

                except Exception as error:
                    answer = (
                        "⚠️ I couldn't generate an answer right now.\n\n"
                        "Please check whether your AI service is running "
                        "and configured correctly, then try again.\n\n"
                        f"**Error details:** `{error}`"
                    )

                st.markdown(answer)

        # Save the assistant response

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    # ======================================================
    # SUGGESTED QUESTIONS
    # ======================================================

    st.divider()

    st.subheader("💡 Suggested Questions")

    suggested_questions = [
        "Summarize the dataset.",
        "What is the overall audience sentiment?",
        "Why are people unhappy?",
        "Which emotion is dominant?",
        "What are the main topics in these comments?",
        "Give me marketing ideas.",
        "Suggest improvements based on the feedback.",
        "What should the creator do next?",
        "What are the most common complaints?",
        "Recommend future content ideas.",
    ]

    col1, col2 = st.columns(2)

    for index, question in enumerate(suggested_questions):

        target_column = col1 if index % 2 == 0 else col2

        with target_column:

            if st.button(
                question,
                key=f"suggested_question_{index}",
                use_container_width=True,
            ):
                st.session_state["assistant_pending_prompt"] = question
                st.rerun()

    # ======================================================
    # PROCESS A SUGGESTED QUESTION
    # ======================================================

    pending_prompt = st.session_state.pop(
        "assistant_pending_prompt",
        None,
    )

    if pending_prompt:

        st.session_state["messages"].append(
            {
                "role": "user",
                "content": pending_prompt,
            }
        )

        with st.chat_message("user"):
            st.markdown(pending_prompt)

        with st.chat_message("assistant"):

            with st.spinner("🤖 AI is analyzing your data..."):

                try:
                    answer = ask_ai(pending_prompt, df)

                    if answer is None:
                        answer = (
                            "The AI service did not return a response. "
                            "Please try again."
                        )
                    else:
                        answer = str(answer)

                except Exception as error:
                    answer = (
                        "⚠️ I couldn't generate an answer right now.\n\n"
                        "Check whether your AI service is running and "
                        "configured correctly, then try again.\n\n"
                        f"**Error details:** `{error}`"
                    )

                st.markdown(answer)

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    # ======================================================
    # CLEAR CONVERSATION
    # ======================================================

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        key="clear_assistant_conversation",
        use_container_width=False,
    ):

        st.session_state["messages"] = []
        st.session_state.pop("assistant_pending_prompt", None)

        st.rerun()
