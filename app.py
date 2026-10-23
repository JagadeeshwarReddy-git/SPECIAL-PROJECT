import streamlit as st

# ==========================================
# Configuration
# ==========================================

from config import APP_NAME, APP_VERSION

# ==========================================
# Load CSS
# ==========================================

def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except:
        pass


load_css()

# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Import Views
# ==========================================

from views import (
    home,
    youtube,
    text,
    csv_upload,
    analytics,
    reports,
    trend,
    assistant,
    insights,
    history,
    dashboard
)

# ==========================================
# Session State
# ==========================================

if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None

if "video_details" not in st.session_state:
    st.session_state.video_details = None

# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.title("🤖 AI Analytics")

    st.caption(f"Version {APP_VERSION}")

    st.divider()

    page_options = [
        "🏠 Home",
        "📺 YouTube Analyzer",
        "📝 Text Analyzer",
        "📂 CSV Upload",
        "📊 Analytics",
        "📈 Trend Analyzer",
        "🤖 AI Assistant",
        "🧠 AI Insights",
        "📄 Reports",
        "🕒 History",
        "📉 Dashboard",
    ]

    if "navigation_page" in st.session_state:
        requested_page = st.session_state.pop("navigation_page")
        if requested_page in page_options:
            st.session_state["Navigation"] = requested_page

    page = st.radio(
        "Navigation",
        page_options,
        key="Navigation",
    )

    st.divider()

    st.success("System Ready")

# ==========================================
# Navigation
# ==========================================

pages = {
    "🏠 Home": home.show,
    "📺 YouTube Analyzer": youtube.show,
    "📝 Text Analyzer": text.show,
    "📂 CSV Upload": csv_upload.show,
    "📊 Analytics": analytics.show,
    "📈 Trend Analyzer": trend.show,
    "🤖 AI Assistant": assistant.show,
    "🧠 AI Insights": insights.show,
    "📄 Reports": reports.show,
    "🕒 History": history.show,
    "📉 Dashboard": dashboard.show,
}

pages[page]()