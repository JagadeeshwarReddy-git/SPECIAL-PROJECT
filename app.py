
import streamlit as st

from config import APP_NAME, APP_VERSION


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# LOAD CSS
# --------------------------------------------------

def load_css():

    try:

        with open(
            "assets/style.css",
            encoding="utf-8"
        ) as css_file:

            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )

    except FileNotFoundError:

        pass


load_css()


# --------------------------------------------------
# IMPORT EXISTING PAGES
# --------------------------------------------------

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


# --------------------------------------------------
# IMPORT NEW PAGES
# --------------------------------------------------

# AI Recommendations
try:

    from views import ai_recommendations

except ImportError:

    ai_recommendations = None


# YouTube Video Comparison
try:

    from views import video_comparison

except ImportError:

    video_comparison = None


# --------------------------------------------------
# SHARED SESSION STATE
# --------------------------------------------------

if "analysis_df" not in st.session_state:

    st.session_state["analysis_df"] = None


if "video_details" not in st.session_state:

    st.session_state["video_details"] = None


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page_options = [

    "🏠 Home",

    "📺 YouTube Analyzer",

    "📝 Text Analyzer",

    "📂 File Analyzer",

    "📊 Analytics",

    "📈 Trend Analyzer",

    "🤖 AI Assistant",

    "💡 AI Recommendations",

    "⚖️ Video Comparison",

    "📄 Reports",

    "🕒 History",

    "📉 Dashboard",

]


with st.sidebar:

    st.title("🤖 AI Analytics")

    st.caption(
        f"Version {APP_VERSION}"
    )

    st.divider()


    # Preserve navigation requests
    # from existing pages.

    if "navigation_page" in st.session_state:

        requested_page = st.session_state.pop(
            "navigation_page"
        )

        if requested_page in page_options:

            st.session_state["Navigation"] = (
                requested_page
            )


    # Migrate old navigation label.

    if (
        st.session_state.get("Navigation")
        == "📂 CSV Upload"
    ):

        st.session_state["Navigation"] = (
            "📂 File Analyzer"
        )


    # Sidebar navigation.

    page = st.radio(

        "Navigation",

        page_options,

        key="Navigation",

    )


    st.divider()

    st.success("System Ready")


# --------------------------------------------------
# PAGE ROUTING
# --------------------------------------------------

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


# --------------------------------------------------
# NEW PAGE ROUTING
# --------------------------------------------------

if ai_recommendations is not None:

    pages["💡 AI Recommendations"] = (
        ai_recommendations.show
    )


if video_comparison is not None:

    pages["⚖️ Video Comparison"] = (
        video_comparison.show
    )


# --------------------------------------------------
# DISPLAY SELECTED PAGE
# --------------------------------------------------

if page in pages:

    pages[page]()

elif page == "💡 AI Recommendations":

    st.title("💡 AI Recommendations")

    st.warning(
        "Create views/ai_recommendations.py "
        "to enable this page."
    )

elif page == "⚖️ Video Comparison":

    st.title("⚖️ YouTube Video Comparison")

    st.warning(
        "Create views/video_comparison.py "
        "to enable this page."
    )

else:

    st.error(
        "Page not found. Please select another page."
    )
