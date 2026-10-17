import re
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# COLORFUL TREND ANALYZER
# ==========================================================

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "have",
    "has", "had", "was", "were", "are", "you", "your", "they",
    "their", "them", "but", "not", "all", "too", "very", "just",
    "about", "what", "when", "where", "which", "who", "why",
    "how", "can", "could", "would", "should", "will", "been",
    "being", "into", "than", "then", "there", "here", "its",
    "our", "out", "get", "got", "getting", "also", "more",
    "most", "some", "such", "only", "really", "still", "much",
    "many", "one", "two", "three", "like", "make", "made",
    "did", "does", "is", "it", "in", "on", "of", "to", "a",
    "an", "as", "at", "by", "be", "or", "if", "so", "we", "i",
    "me", "my", "he", "she", "his", "her", "our", "us",
    "im", "ive", "youre", "theyre", "dont", "didnt", "doesnt",
    "wasnt", "wont", "yeah", "yes", "no", "okay", "ok"
}

GENERIC_WORDS = {
    "video", "videos", "comment", "comments", "channel",
    "youtube", "watch", "watched", "watching", "people",
    "person", "thing", "things", "time", "day", "days",
    "content", "thanks", "thank", "hello", "hey", "guys",
    "guy", "everyone", "someone", "something"
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "love",
    "loved", "like", "liked", "best", "beautiful", "helpful",
    "perfect", "fantastic", "wonderful", "interesting", "enjoy",
    "enjoyed", "useful", "impressive", "brilliant", "happy"
}

NEGATIVE_WORDS = {
    "bad", "worst", "hate", "hated", "boring", "poor", "terrible",
    "awful", "disappointing", "disappointed", "waste", "wrong",
    "problem", "problems", "issue", "issues", "expensive", "slow",
    "fake", "confusing", "useless", "annoying", "sad"
}


def find_text_column(df):
    candidates = [
        "comment", "comments", "text", "content", "review",
        "reviews", "message", "feedback", "clean_comment"
    ]

    for col in candidates:
        if col in df.columns:
            return col

    # Fallback: choose the object/string column with the most text.
    object_cols = df.select_dtypes(include=["object", "string"]).columns

    best_col = None
    best_length = 0

    for col in object_cols:
        length = (
            df[col]
            .fillna("")
            .astype(str)
            .str.len()
            .sum()
        )

        if length > best_length:
            best_col = col
            best_length = length

    return best_col


def clean_words(text, strict=True):
    text = str(text).lower()

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    text = re.sub(r"[@#]", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    words = text.split()

    result = []

    for word in words:

        if len(word) < 3:
            continue

        if word.isdigit():
            continue

        if word in STOPWORDS:
            continue

        if strict and word in GENERIC_WORDS:
            continue

        result.append(word)

    # Important fallback:
    # if aggressive filtering removed everything,
    # use less-filtered words.
    if not result and strict:
        return clean_words(text, strict=False)

    return result


def get_words_by_record(df, text_col):
    records = []

    for text in df[text_col]:
        records.append(
            clean_words(text)
        )

    return records


def count_words(records):
    counter = Counter()

    for words in records:
        # A topic is counted once per record.
        counter.update(set(words))

    return counter


def count_phrases(records, n=2):
    counter = Counter()

    for words in records:

        phrases = [
            " ".join(words[i:i+n])
            for i in range(
                len(words) - n + 1
            )
        ]

        counter.update(set(phrases))

    return counter


def sentiment_label(value):
    value = str(value).strip().lower()

    if value in ["positive", "pos"]:
        return "Positive"

    if value in ["negative", "neg"]:
        return "Negative"

    if value in ["neutral", "neu"]:
        return "Neutral"

    return value.title()


def topic_sentiment_data(
    df,
    text_col,
    top_topics
):

    if "sentiment" not in df.columns:
        return pd.DataFrame()

    rows = []

    for _, row in df.iterrows():

        words = set(
            clean_words(
                row[text_col]
            )
        )

        sentiment = sentiment_label(
            row["sentiment"]
        )

        for word in words:

            if word in top_topics:

                rows.append(
                    {
                        "Topic": word,
                        "Sentiment": sentiment
                    }
                )

    if not rows:
        return pd.DataFrame()

    temp = pd.DataFrame(rows)

    result = (
        temp
        .groupby(
            ["Topic", "Sentiment"]
        )
        .size()
        .reset_index(
            name="Mentions"
        )
    )

    return result


def topic_emotion_data(
    df,
    text_col,
    top_topics
):

    if "emotion" not in df.columns:
        return pd.DataFrame()

    rows = []

    for _, row in df.iterrows():

        words = set(
            clean_words(
                row[text_col]
            )
        )

        emotion = str(
            row["emotion"]
        ).strip().title()

        if emotion.lower() in [
            "", "nan", "unknown"
        ]:
            continue

        for word in words:

            if word in top_topics:

                rows.append(
                    {
                        "Topic": word,
                        "Emotion": emotion
                    }
                )

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .groupby(
            ["Topic", "Emotion"]
        )
        .size()
        .reset_index(
            name="Mentions"
        )
    )


def card(title, value, subtitle, emoji):
    st.markdown(
        f"""
        <div class="trend-card">
            <div class="trend-card-icon">{emoji}</div>
            <div class="trend-card-title">{title}</div>
            <div class="trend-card-value">{value}</div>
            <div class="trend-card-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def chart_style(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(
            l=25,
            r=25,
            t=65,
            b=30
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            x=0.02,
            font=dict(size=19)
        ),
        font=dict(size=12)
    )

    return fig


def show():

    # ======================================================
    # COLORFUL APPLICATION STYLE
    # ======================================================

    st.markdown(
        """
        <style>

        .trend-header {
            padding: 24px 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                #667eea 0%,
                #764ba2 50%,
                #f093fb 100%
            );
            color: white;
        }

        .trend-header h1 {
            color: white;
            margin: 0;
            font-size: 2.2rem;
        }

        .trend-header p {
            color: rgba(255,255,255,.90);
            margin: 7px 0 0 0;
            font-size: 1rem;
        }

        .trend-card {
            border-radius: 18px;
            padding: 18px;
            min-height: 145px;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,.10);
            background: linear-gradient(
                135deg,
                #667eea,
                #764ba2
            );
        }

        .trend-card-icon {
            font-size: 25px;
        }

        .trend-card-title {
            margin-top: 7px;
            font-size: 13px;
            opacity: .88;
            text-transform: uppercase;
            letter-spacing: .5px;
        }

        .trend-card-value {
            margin-top: 4px;
            font-size: 29px;
            font-weight: 800;
        }

        .trend-card-sub {
            margin-top: 4px;
            font-size: 12px;
            opacity: .80;
        }

        .topic-pill {
            display: inline-block;
            padding: 8px 13px;
            margin: 4px;
            border-radius: 20px;
            background: linear-gradient(
                135deg,
                #667eea,
                #f093fb
            );
            color: white;
            font-weight: 650;
        }

        .trend-section {
            padding: 12px 0 2px 0;
        }

        .summary-box {
            border-radius: 17px;
            padding: 20px;
            background: linear-gradient(
                135deg,
                rgba(102,126,234,.12),
                rgba(240,147,251,.12)
            );
            border: 1px solid rgba(118,75,162,.18);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # HEADER
    # ======================================================

    st.markdown(
        """
        <div class="trend-header">
            <h1>📈 Trend Analyzer</h1>
            <p>
                Automatically discover what your audience is talking about,
                which topics are popular, how people react, and what emotions
                are connected to those topics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # DATA
    # ======================================================

    df = st.session_state.get(
        "analysis_df"
    )

    if df is None:

        st.info(
            "📂 Analyze a YouTube video, text, or CSV first. "
            "Your trends will automatically appear here."
        )

        return

    if not isinstance(
        df,
        pd.DataFrame
    ) or df.empty:

        st.info(
            "📂 No analyzed records are available."
        )

        return

    data = df.copy()

    text_col = find_text_column(
        data
    )

    if text_col is None:

        st.error(
            "❌ No text column was found."
        )

        return

    data[text_col] = (
        data[text_col]
        .fillna("")
        .astype(str)
    )

    data = data[
        data[text_col]
        .str.strip()
        != ""
    ]

    if data.empty:

        st.warning(
            "No usable text was found."
        )

        return

    # ======================================================
    # AUTOMATIC ANALYSIS
    # ======================================================

    records = get_words_by_record(
        data,
        text_col
    )

    word_counter = count_words(
        records
    )

    phrase_counter = count_phrases(
        records,
        2
    )

    triple_counter = count_phrases(
        records,
        3
    )

    # Ensure single-record text still has topics.
    if not word_counter:

        fallback_records = [
            clean_words(
                text,
                strict=False
            )
            for text in data[text_col]
        ]

        word_counter = count_words(
            fallback_records
        )

    top_words = word_counter.most_common(
        20
    )

    top_phrases = [
        item
        for item in phrase_counter.most_common(15)
        if item[1] >= 1
    ]

    top_triples = [
        item
        for item in triple_counter.most_common(15)
        if item[1] >= 1
    ]

    # ======================================================
    # SUMMARY VALUES
    # ======================================================

    total_records = len(data)
    unique_words = len(word_counter)

    total_mentions = sum(
        word_counter.values()
    )

    if "sentiment" in data.columns:

        sentiments = (
            data["sentiment"]
            .map(sentiment_label)
        )

        dominant_sentiment = (
            sentiments
            .value_counts()
            .idxmax()
        )

    else:

        dominant_sentiment = "N/A"

    if "emotion" in data.columns:

        emotions = (
            data["emotion"]
            .astype(str)
            .str.title()
        )

        dominant_emotion = (
            emotions
            .value_counts()
            .idxmax()
        )

    else:

        dominant_emotion = "N/A"

    # ======================================================
    # COLORFUL KPI ROW
    # ======================================================

    st.markdown(
        '<div class="trend-section"></div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        card(
            "Records",
            f"{total_records:,}",
            "Analyzed records",
            "📊"
        )

    with k2:
        card(
            "Topics",
            f"{unique_words:,}",
            "Meaningful topics found",
            "🔥"
        )

    with k3:
        card(
            "Mentions",
            f"{total_mentions:,}",
            "Topic mentions",
            "💬"
        )

    with k4:
        card(
            "Mood",
            dominant_sentiment,
            f"Emotion: {dominant_emotion}",
            "😊"
        )

    # ======================================================
    # TOP TOPICS
    # ======================================================

    st.markdown("### 🔥 What People Are Talking About")

    if top_words:

        word_df = pd.DataFrame(
            top_words,
            columns=[
                "Topic",
                "Mentions"
            ]
        )

        left, right = st.columns(
            [1.45, 1]
        )

        with left:

            fig = px.bar(
                word_df.sort_values(
                    "Mentions"
                ),

                x="Mentions",
                y="Topic",

                orientation="h",

                text="Mentions",

                title="🔥 Top Discussion Topics",

                color="Mentions",

                color_continuous_scale="Turbo"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                chart_style(
                    fig,
                    570
                ),
                use_container_width=True
            )

        with right:

            # Bubble-style topic map.
            bubble = word_df.copy()

            bubble["Rank"] = range(
                len(bubble),
                0,
                -1
            )

            fig = px.scatter(
                bubble,

                x="Rank",
                y="Mentions",

                size="Mentions",

                text="Topic",

                color="Mentions",

                color_continuous_scale="Turbo",

                size_max=70,

                title="🌈 Topic Bubble Map"
            )

            fig.update_traces(
                textposition="middle center"
            )

            fig.update_xaxes(
                visible=False
            )

            fig.update_yaxes(
                title="Mentions"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                chart_style(
                    fig,
                    570
                ),
                use_container_width=True
            )

    else:

        st.warning(
            "No topics could be extracted from the current text."
        )

    # ======================================================
    # TOPIC CLOUD / PILLS
    # ======================================================

    st.markdown(
        "### ☁️ Trending Words"
    )

    if top_words:

        html = ""

        for word, count in top_words:

            html += (
                f'<span class="topic-pill">'
                f'{word} · {count}'
                f'</span>'
            )

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    # ======================================================
    # COMMON PHRASES
    # ======================================================

    st.markdown(
        "### 💬 Trending Phrases"
    )

    phrase_left, phrase_right = st.columns(
        2
    )

    with phrase_left:

        if top_phrases:

            phrase_df = pd.DataFrame(
                top_phrases[:10],
                columns=[
                    "Phrase",
                    "Mentions"
                ]
            )

            fig = px.bar(
                phrase_df.sort_values(
                    "Mentions"
                ),

                x="Mentions",
                y="Phrase",

                orientation="h",

                text="Mentions",

                title="💬 Common Phrases",

                color="Mentions",

                color_continuous_scale="Viridis"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                chart_style(fig, 450),
                use_container_width=True
            )

        else:

            st.info(
                "No phrases available."
            )

    with phrase_right:

        if top_triples:

            triple_df = pd.DataFrame(
                top_triples[:10],
                columns=[
                    "Phrase",
                    "Mentions"
                ]
            )

            fig = px.bar(
                triple_df.sort_values(
                    "Mentions"
                ),

                x="Mentions",
                y="Phrase",

                orientation="h",

                text="Mentions",

                title="🗣️ Common 3-Word Phrases",

                color="Mentions",

                color_continuous_scale="Plasma"
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                coloraxis_showscale=False
            )

            st.plotly_chart(
                chart_style(fig, 450),
                use_container_width=True
            )

        else:

            st.info(
                "No three-word phrases available."
            )

    # ======================================================
    # SENTIMENT BY TOPIC
    # ======================================================

    topic_sentiment = topic_sentiment_data(
        data,
        text_col,
        set(
            word
            for word, _ in top_words[:12]
        )
    )

    if not topic_sentiment.empty:

        st.markdown(
            "### 😊 How People Feel About Each Topic"
        )

        fig = px.bar(
            topic_sentiment,

            x="Topic",
            y="Mentions",

            color="Sentiment",

            barmode="group",

            text="Mentions",

            title="Sentiment Across Trending Topics"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_xaxes(
            tickangle=-35
        )

        st.plotly_chart(
            chart_style(
                fig,
                520
            ),
            use_container_width=True
        )

        # --------------------------------------------------
        # Sentiment topic table
        # --------------------------------------------------

        pivot = (
            topic_sentiment
            .pivot(
                index="Topic",
                columns="Sentiment",
                values="Mentions"
            )
            .fillna(0)
        )

        for col in [
            "Positive",
            "Neutral",
            "Negative"
        ]:

            if col not in pivot.columns:
                pivot[col] = 0

        pivot["Total"] = (
            pivot["Positive"]
            + pivot["Neutral"]
            + pivot["Negative"]
        )

        pivot["Positive %"] = (
            pivot["Positive"]
            / pivot["Total"]
            * 100
        ).round(1)

        pivot["Neutral %"] = (
            pivot["Neutral"]
            / pivot["Total"]
            * 100
        ).round(1)

        pivot["Negative %"] = (
            pivot["Negative"]
            / pivot["Total"]
            * 100
        ).round(1)

        st.dataframe(
            pivot.reset_index(),
            use_container_width=True,
            hide_index=True
        )

    # ======================================================
    # EMOTION ANALYSIS
    # ======================================================

    topic_emotion = topic_emotion_data(
        data,
        text_col,
        set(
            word
            for word, _ in top_words[:10]
        )
    )

    if not topic_emotion.empty:

        st.markdown(
            "### 🎭 Emotions Connected to Trending Topics"
        )

        fig = px.bar(
            topic_emotion,

            x="Topic",

            y="Mentions",

            color="Emotion",

            barmode="stack",

            text="Mentions",

            title="Emotion Distribution by Topic"
        )

        fig.update_traces(
            textposition="inside"
        )

        fig.update_xaxes(
            tickangle=-35
        )

        st.plotly_chart(
            chart_style(
                fig,
                520
            ),
            use_container_width=True
        )

    # ======================================================
    # SENTIMENT OVERVIEW
    # ======================================================

    if "sentiment" in data.columns:

        st.markdown(
            "### 🎯 Audience Reaction"
        )

        sentiment_counts = (
            data["sentiment"]
            .map(sentiment_label)
            .value_counts()
            .reset_index()
        )

        sentiment_counts.columns = [
            "Sentiment",
            "Records"
        ]

        left, right = st.columns(
            2
        )

        with left:

            fig = px.pie(
                sentiment_counts,

                names="Sentiment",

                values="Records",

                hole=.55,

                title="Audience Sentiment",

                color_discrete_sequence=[
                    "#00C853",
                    "#FFC107",
                    "#FF1744"
                ]
            )

            fig.update_traces(
                textinfo="percent+label"
            )

            st.plotly_chart(
                chart_style(
                    fig,
                    400
                ),
                use_container_width=True
            )

        with right:

            fig = px.bar(
                sentiment_counts,

                x="Sentiment",

                y="Records",

                text="Records",

                title="Sentiment Comparison",

                color="Sentiment",

                color_discrete_sequence=[
                    "#00C853",
                    "#FFC107",
                    "#FF1744"
                ]
            )

            fig.update_traces(
                textposition="outside"
            )

            st.plotly_chart(
                chart_style(
                    fig,
                    400
                ),
                use_container_width=True
            )

    # ======================================================
    # AUTOMATIC INSIGHTS
    # ======================================================

    st.markdown(
        "### 💡 Automatic Trend Insights"
    )

    if top_words:

        top_topic = top_words[0][0]
        top_count = top_words[0][1]

        second_topic = (
            top_words[1][0]
            if len(top_words) > 1
            else "N/A"
        )

        third_topic = (
            top_words[2][0]
            if len(top_words) > 2
            else "N/A"
        )

        top_phrase = (
            top_phrases[0][0]
            if top_phrases
            else "No repeated phrase"
        )

        st.markdown(
            f"""
            <div class="summary-box">

            <h4>📌 What the data is saying</h4>

            <p>
            🔥 <b>{top_topic}</b> is the most discussed topic,
            appearing in <b>{top_count}</b> analyzed record(s).
            </p>

            <p>
            📈 Other major topics include
            <b>{second_topic}</b> and <b>{third_topic}</b>.
            </p>

            <p>
            💬 The most repeated phrase is
            <b>“{top_phrase}”</b>.
            </p>

            <p>
            😊 The dominant audience sentiment is
            <b>{dominant_sentiment}</b>.
            </p>

            <p>
            🎭 The dominant detected emotion is
            <b>{dominant_emotion}</b>.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ======================================================
    # TOP COMMENTS
    # ======================================================

    st.markdown(
        "### 💬 Feedback Behind the Trends"
    )

    if "sentiment" in data.columns:

        display_cols = [
            text_col,
            "sentiment"
        ]

        if "emotion" in data.columns:
            display_cols.append(
                "emotion"
            )

        st.dataframe(
            data[
                display_cols
            ].head(20),

            use_container_width=True,

            hide_index=True
        )

    else:

        st.dataframe(
            data[
                [text_col]
            ].head(20),

            use_container_width=True,

            hide_index=True
        )

    # ======================================================
    # EXPORT
    # ======================================================

    st.markdown(
        "### ⬇️ Export"
    )

    export_df = pd.DataFrame(
        top_words,
        columns=[
            "Topic",
            "Mentions"
        ]
    )

    st.download_button(
        "Download Trend Results",

        data=export_df.to_csv(
            index=False
        ).encode("utf-8"),

        file_name="trend_analysis.csv",

        mime="text/csv",

        use_container_width=True
    )


show_trend = show
