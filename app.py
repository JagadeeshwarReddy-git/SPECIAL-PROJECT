import streamlit as st

from config import APP_NAME, APP_VERSION


def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as css_file:
            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )
    except FileNotFoundError:
        pass


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

from views import (
    home,
    youtube,
    text,
    csv_upload,
    analytics,
    reports,
    trend,
    assistant,
    history,
    dashboard,
)

# Shared state used by the existing pages.
# Do not overwrite existing analysis data on every Streamlit rerun.
if "analysis_df" not in st.session_state:
    st.session_state["analysis_df"] = None

if "video_details" not in st.session_state:
    st.session_state["video_details"] = None


# Sidebar navigation
page_options = [
    "🏠 Home",
    "📺 YouTube Analyzer",
    "📝 Text Analyzer",
    "📂 File Analyzer",
    "📊 Analytics",
    "📈 Trend Analyzer",
    "🤖 AI Assistant",
    "📄 Reports",
    "🕒 History",
    "📉 Dashboard",
]


with st.sidebar:
    st.title("🤖 AI Analytics")
    st.caption(f"Version {APP_VERSION}")
    st.divider()

    # Preserve navigation requests made by other pages.
    if "navigation_page" in st.session_state:
        requested_page = st.session_state.pop("navigation_page")

        if requested_page in page_options:
            st.session_state["Navigation"] = requested_page

    # Migrate the old CSV Upload label.
    if st.session_state.get("Navigation") == "📂 CSV Upload":
        st.session_state["Navigation"] = "📂 File Analyzer"

    page = st.radio(
        "Navigation",
        page_options,
        key="Navigation",
    )

    st.divider()
    st.success("System Ready")


# Page routing
pages = {
    "🏠 Home": home.show,
    "📺 YouTube Analyzer": youtube.show,
    "📝 Text Analyzer": text.show,
    "📂 File Analyzer": csv_upload.show,
    "📊 Analytics": analytics.show,
    "📈 Trend Analyzer": trend.show,
    "🤖 AI Assistant": assistant.show,
    "📄 Reports": reports.show,
    "🕒 History": history.show,
    "📉 Dashboard": dashboard.show,
}


# Display the selected page
pages[page]()