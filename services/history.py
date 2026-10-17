import streamlit as st
import json
import os
from datetime import datetime

# ==========================================
# History File
# ==========================================

HISTORY_FILE = "analysis_history.json"


# ==========================================
# Load History
# ==========================================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


# ==========================================
# Save History
# ==========================================

def save_history(
    analysis_type,
    records_count,
    sentiment,
    emotion,
    source_name="Analysis"
):
    history = load_history()

    # Create new history entry
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "type": analysis_type,
        "source": source_name,
        "records": int(records_count),
        "sentiment": sentiment,
        "emotion": emotion
    }

    history.insert(0, entry)

    # Keep latest 50 analyses
    history = history[:50]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)

    except Exception as e:
        print("History save error:", e)


# ==========================================
# Delete History
# ==========================================

def clear_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

        return True

    except Exception as e:
        print("History delete error:", e)
        return False


# ==========================================
# History Page
# ==========================================

def show():

    st.title("🕒 Analysis History")

    st.caption(
        "View your previous social media analysis sessions."
    )

    st.divider()

    history = load_history()

    # ==========================================
    # Empty History
    # ==========================================

    if not history:

        st.info(
            "📭 No analysis history available yet."
        )

        st.markdown(
            """
            ### How History Works

            1. Analyze YouTube comments, text, or CSV data.
            2. The analysis is automatically saved.
            3. Return here to view your previous analyses.
            """
        )

        return

    # ==========================================
    # Header
    # ==========================================

    col1, col2 = st.columns([4, 1])

    with col1:
        st.subheader(
            f"📚 {len(history)} Analysis Session(s)"
        )

    with col2:

        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):

            if clear_history():

                st.success("History cleared.")

                st.rerun()

    # ==========================================
    # History Cards
    # ==========================================

    for item in history:

        analysis_type = item.get(
            "type",
            "Analysis"
        )

        source = item.get(
            "source",
            "Unknown"
        )

        date = item.get(
            "date",
            "Unknown date"
        )

        records = item.get(
            "records",
            0
        )

        sentiment = item.get(
            "sentiment",
            "N/A"
        )

        emotion = item.get(
            "emotion",
            "N/A"
        )

        with st.container(border=True):

            top1, top2 = st.columns(
                [4, 1]
            )

            with top1:

                if analysis_type == "YouTube":
                    st.markdown(
                        "### 📺 YouTube Analysis"
                    )

                elif analysis_type == "Text":
                    st.markdown(
                        "### 📝 Text Analysis"
                    )

                elif analysis_type == "CSV":
                    st.markdown(
                        "### 📂 CSV Analysis"
                    )

                else:
                    st.markdown(
                        f"### 📊 {analysis_type}"
                    )

                st.caption(
                    f"📅 {date}"
                )

            with top2:

                st.metric(
                    "Records",
                    records
                )

            st.write(
                f"**Source:** {source}"
            )

            c1, c2 = st.columns(2)

            with c1:
                st.write(
                    f"**Sentiment:** {sentiment}"
                )

            with c2:
                st.write(
                    f"**Emotion:** {emotion}"
                )

        st.write("")
        

# ==========================================
# Compatibility
# ==========================================

show_history = show