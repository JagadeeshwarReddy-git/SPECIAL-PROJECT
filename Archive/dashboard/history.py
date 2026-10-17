import streamlit as st
import pandas as pd

from database import get_history


def show():

    st.title("🕒 Analysis History")

    history = get_history()

    if len(history) == 0:
        st.info("No analysis available.")
        return

    df = pd.DataFrame(
        history,
        columns=[
            "ID",
            "Source",
            "Title",
            "Positive",
            "Neutral",
            "Negative",
            "Emotion",
            "Date"
        ]
    )

    st.dataframe(df, use_container_width=True)