from dashboard.reports import show as reports
from dashboard.live_dashboard import show as live_dashboard
from dashboard.history import show as history
from dashboard.insights import show as insights
from dashboard.ai_assistant import show as ai_assistant
from dashboard.trends import show as trends
from dashboard.video_compare import show as compare
from dashboard.about import show as about
from dashboard.text_analysis import show as text_analysis
from dashboard.youtube import show as youtube
import streamlit as st

from dashboard.home import show as home

st.set_page_config(
    page_title="AI-Based Social Media Analytics",
    page_icon="📊",
    layout="wide"
)
def load_css():
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

st.sidebar.title("📊 Social Media Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📺 YouTube Analyzer",
        "📝 Text Analyzer",
        "📂 CSV Upload",
        "📊 Analytics",
        "📄 Reports",
        "ℹ About"
        "⚖️ Compare Videos",
        "📈 Trend Analyzer",
        "🤖 AI Assistant",
        "🧠 AI Insights",
        "🕒 History",
        "📈 Live Dashboard"
    ]
)

if page == "🏠 Home":
    home()

elif page == "📺 YouTube Analyzer":
    youtube()

elif page == "📝 Text Analyzer":
    text_analysis()

elif page == "📂 CSV Upload":
    st.title("📂 CSV Upload")
    st.info("Coming Soon")

elif page == "📊 Analytics":
    st.title("📊 Analytics")
    st.info("Coming Soon")

elif page == "📄 Reports":
    reports()

elif page == "ℹ About":
    about()
elif page == "⚖️ Compare Videos":
    compare()
elif page == "📈 Trend Analyzer":
    trends()
elif page == "🤖 AI Assistant":
    ai_assistant()

elif page == "🧠 AI Insights":
    insights()
elif page == "📈 Live Dashboard":
    live_dashboard()