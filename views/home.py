import streamlit as st
import pandas as pd


def _card(title, description, icon):
    st.markdown(
        f"""
        <div class="home-card">
            <div class="home-card-icon">{icon}</div>
            <div class="home-card-title">{title}</div>
            <div class="home-card-text">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show():
    st.markdown(
        """
        <style>
        /* ---------- HOME: clean application-style UI ---------- */

        .home-title {
            font-size: 32px;
            font-weight: 700;
            margin: 8px 0 4px;
            letter-spacing: -0.5px;
        }

        .home-subtitle {
            font-size: 15px;
            color: #64748b;
            margin-bottom: 26px;
        }

        .home-welcome {
            padding: 26px 28px;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            background: #ffffff;
            margin-bottom: 26px;
        }

        .home-welcome-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .home-welcome-text {
            color: #64748b;
            font-size: 14px;
            line-height: 1.55;
            max-width: 760px;
        }

        .home-section {
            font-size: 20px;
            font-weight: 700;
            margin: 28px 0 14px;
        }

        .home-card {
            min-height: 150px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #ffffff;
            margin-bottom: 14px;
            transition: 0.15s ease;
        }

        .home-card:hover {
            border-color: #94a3b8;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.07);
        }

        .home-card-icon {
            font-size: 25px;
            margin-bottom: 12px;
        }

        .home-card-title {
            font-size: 17px;
            font-weight: 650;
            margin-bottom: 7px;
        }

        .home-card-text {
            color: #64748b;
            font-size: 13px;
            line-height: 1.5;
        }

        .home-flow {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #ffffff;
            padding: 20px 22px;
            margin-top: 8px;
        }

        .flow-item {
            text-align: center;
            font-size: 13px;
            font-weight: 600;
        }

        .flow-caption {
            color: #64748b;
            font-size: 11px;
            font-weight: 400;
            margin-top: 4px;
        }

        .home-stat {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            background: #ffffff;
            padding: 17px;
            text-align: center;
        }

        .home-stat-value {
            font-size: 22px;
            font-weight: 700;
        }

        .home-stat-label {
            color: #64748b;
            font-size: 11px;
            margin-top: 4px;
        }

        .home-note {
            border-left: 3px solid #3b82f6;
            background: #f8fafc;
            padding: 14px 17px;
            border-radius: 6px;
            color: #475569;
            font-size: 13px;
            line-height: 1.5;
        }

        @media (prefers-color-scheme: dark) {
            .home-welcome,
            .home-card,
            .home-flow,
            .home-stat {
                background: #111827;
                border-color: #334155;
            }

            .home-subtitle,
            .home-card-text,
            .flow-caption,
            .home-stat-label {
                color: #94a3b8;
            }

            .home-note {
                background: #111827;
                color: #cbd5e1;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Header — deliberately simple, like a normal application
    # ---------------------------------------------------------
    st.markdown(
        '<div class="home-title">AI-Based Social Media Analytics</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="home-subtitle">'
        'Analyze social-media content, understand audience reaction, and explore the results.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Welcome panel
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="home-welcome">
            <div class="home-welcome-title">Welcome 👋</div>
            <div class="home-welcome-text">
                Start by choosing a data source from the sidebar.
                You can analyze YouTube comments, individual text, or a CSV dataset.
                After analysis, the results are available across Analytics, Trends,
                AI Insights, Reports, History and the AI Assistant.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Quick start
    # ---------------------------------------------------------
    st.markdown(
        '<div class="home-section">Quick Start</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        _card(
            "YouTube Analyzer",
            "Enter a YouTube video URL and analyze its available comments.",
            "▶️",
        )

    with c2:
        _card(
            "Text Analyzer",
            "Enter text directly to check its sentiment and emotion.",
            "✍️",
        )

    with c3:
        _card(
            "CSV Upload",
            "Upload a dataset containing comments or other text records.",
            "📄",
        )

    # ---------------------------------------------------------
    # Application workflow
    # ---------------------------------------------------------
    st.markdown(
        '<div class="home-section">How it works</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-flow">
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4, f5 = st.columns(5)

    steps = [
        (f1, "📥", "Input", "YouTube / Text / CSV"),
        (f2, "🧹", "Prepare", "Clean & validate"),
        (f3, "🧠", "Analyze", "Sentiment + emotion"),
        (f4, "📊", "Explore", "Charts + trends"),
        (f5, "💡", "Understand", "Insights + AI"),
    ]

    for col, icon, title, caption in steps:
        with col:
            st.markdown(
                f"""
                <div class="flow-item">
                    <div style="font-size:23px;">{icon}</div>
                    <div>{title}</div>
                    <div class="flow-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # What is available
    # ---------------------------------------------------------
    st.markdown(
        '<div class="home-section">Available tools</div>',
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns(3)

    with a1:
        _card(
            "Analytics",
            "View sentiment distribution, emotions, audience mood and key statistics.",
            "📊",
        )
        _card(
            "AI Insights",
            "Get rule-based observations and recommendations from the analyzed data.",
            "💡",
        )

    with a2:
        _card(
            "Trend Analyzer",
            "Explore frequently occurring keywords and discussion patterns.",
            "📈",
        )
        _card(
            "AI Assistant",
            "Ask questions about the current dataset using Ollama and Llama 3.2.",
            "🤖",
        )

    with a3:
        _card(
            "Reports",
            "Create a downloadable summary of the analysis.",
            "📄",
        )
        _card(
            "History",
            "Review previous analyses and their main results.",
            "🕘",
        )

    # ---------------------------------------------------------
    # Current analysis status
    # ---------------------------------------------------------
    df = st.session_state.get("analysis_df")

    st.markdown(
        '<div class="home-section">Current session</div>',
        unsafe_allow_html=True,
    )

    if isinstance(df, pd.DataFrame) and not df.empty:
        total = len(df)

        if "sentiment" in df.columns:
            sentiments = df["sentiment"].astype(str).str.lower()
            positive = int((sentiments == "positive").sum())
            neutral = int((sentiments == "neutral").sum())
            negative = int((sentiments == "negative").sum())
        else:
            positive = neutral = negative = 0

        s1, s2, s3, s4 = st.columns(4)

        stats = [
            (s1, f"{total:,}", "Records analyzed"),
            (s2, f"{positive:,}", "Positive"),
            (s3, f"{neutral:,}", "Neutral"),
            (s4, f"{negative:,}", "Negative"),
        ]

        for col, value, label in stats:
            with col:
                st.markdown(
                    f"""
                    <div class="home-stat">
                        <div class="home-stat-value">{value}</div>
                        <div class="home-stat-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.markdown(
            """
            <div class="home-note">
                No analysis is loaded in the current session yet.
                Choose <strong>YouTube Analyzer</strong>, <strong>Text Analyzer</strong>,
                or <strong>CSV Upload</strong> from the sidebar to begin.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#94a3b8;
            font-size:11px;
            padding:32px 0 8px;
        ">
            AI-Based Social Media Analytics • Python • Streamlit • NLP • Local AI
        </div>
        """,
        unsafe_allow_html=True,
    )


show_home = show
show = show