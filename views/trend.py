
import re
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st


STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "have",
    "has", "had", "was", "were", "are", "you", "your", "they",
    "their", "them", "but", "not", "all", "too", "very", "just",
    "about", "what", "when", "where", "which", "who", "why",
    "how", "can", "could", "would", "should", "will", "been",
    "being", "into", "than", "then", "there", "here", "its",
    "our", "out", "get", "got", "getting", "also", "more",
    "most", "some", "such", "only", "really", "still", "much",
    "many", "one", "two", "three", "make", "made", "did",
    "does", "is", "it", "in", "on", "of", "to", "a", "an",
    "as", "at", "by", "be", "or", "if", "so", "we", "i",
    "me", "my", "he", "she", "his", "her", "us", "im",
    "ive", "youre", "theyre", "dont", "didnt", "doesnt",
    "wasnt", "wont", "yeah", "yes", "no", "okay", "ok",
}

GENERIC_WORDS = {
    "video", "videos", "comment", "comments", "channel",
    "youtube", "watch", "watched", "watching", "people",
    "person", "thing", "things", "time", "day", "days",
    "content", "thanks", "thank", "hello", "hey", "guys",
    "everyone", "someone", "something",
}


def find_column(df, candidates):
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def find_text_column(df):
    column = find_column(
        df,
        [
            "comment", "comments", "text", "content",
            "review", "reviews", "message", "feedback",
            "clean_comment", "post", "caption", "description",
        ],
    )

    if column is not None:
        return column

    object_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    best_column = None
    best_length = 0

    for column in object_columns:
        length = (
            df[column]
            .fillna("")
            .astype(str)
            .str.len()
            .sum()
        )

        if length > best_length:
            best_column = column
            best_length = length

    return best_column


def clean_words(text, strict=True):
    text = str(text).lower()

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text,
    )

    text = re.sub(r"[@#]", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    result = []

    for word in text.split():
        if len(word) < 3 or word.isdigit():
            continue

        if word in STOPWORDS:
            continue

        if strict and word in GENERIC_WORDS:
            continue

        result.append(word)

    if not result and strict:
        return clean_words(text, strict=False)

    return result


def sentiment_label(value):
    value = str(value).strip().lower()

    if value in {"positive", "pos", "very positive"}:
        return "Positive"

    if value in {"negative", "neg", "very negative"}:
        return "Negative"

    if value in {"neutral", "neu"}:
        return "Neutral"

    if value in {"label_2"}:
        return "Positive"

    if value in {"label_0"}:
        return "Negative"

    if value in {"label_1"}:
        return "Neutral"

    return "Unknown"


def get_shared_analysis_data():
    """Retrieve analysis results regardless of the input page."""

    for key in (
        "analysis_df",
        "universal_analysis_df",
        "df",
    ):
        candidate = st.session_state.get(key)

        if isinstance(candidate, pd.DataFrame) and not candidate.empty:
            return candidate.copy()

    return None


def build_word_counts(texts):
    counter = Counter()

    for text in texts:
        words = clean_words(text)
        counter.update(set(words))

    return counter


def build_phrase_counts(texts, phrase_size=2):
    counter = Counter()

    for text in texts:
        words = clean_words(text)

        phrases = [
            " ".join(words[i:i + phrase_size])
            for i in range(len(words) - phrase_size + 1)
        ]

        counter.update(set(phrases))

    return counter


def build_topic_sentiment(df, text_column, sentiment_column, topics):
    records = []

    if sentiment_column is None:
        return pd.DataFrame()

    for _, row in df.iterrows():
        words = set(clean_words(row[text_column]))
        sentiment = sentiment_label(row[sentiment_column])

        if sentiment == "Unknown":
            continue

        for topic in topics:
            if topic in words:
                records.append({
                    "Topic": topic,
                    "Sentiment": sentiment,
                    "Mentions": 1,
                })

    if not records:
        return pd.DataFrame()

    return (
        pd.DataFrame(records)
        .groupby(["Topic", "Sentiment"], as_index=False)["Mentions"]
        .sum()
    )


def build_topic_emotions(df, text_column, emotion_column, topics):
    records = []

    if emotion_column is None:
        return pd.DataFrame()

    for _, row in df.iterrows():
        words = set(clean_words(row[text_column]))
        emotion = str(row[emotion_column]).strip().title()

        if emotion.lower() in {"", "nan", "none", "unknown"}:
            continue

        for topic in topics:
            if topic in words:
                records.append({
                    "Topic": topic,
                    "Emotion": emotion,
                    "Mentions": 1,
                })

    if not records:
        return pd.DataFrame()

    return (
        pd.DataFrame(records)
        .groupby(["Topic", "Emotion"], as_index=False)["Mentions"]
        .sum()
    )


def show():
    st.markdown(
        """
        <style>
        .trend-header {
            padding: 24px;
            border-radius: 18px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            color: white;
        }
        .trend-header h1 {
            color: white;
            margin: 0;
        }
        .trend-header p {
            color: white;
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="trend-header">
            <h1>📈 Trend Analyzer</h1>
            <p>
                Discover popular topics, repeated phrases, audience
                sentiment, and emotions in your analyzed content.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOAD SHARED ANALYSIS DATA
    # --------------------------------------------------------

    df = get_shared_analysis_data()

    if df is None:
        st.warning(
            "No analyzed data is available. Open CSV Upload, upload "
            "your file, and click Analyze file first."
        )

        if st.button("Open CSV Upload"):
            st.session_state["navigation_page"] = "📂 CSV Upload"
            st.rerun()

        return

    text_column = find_text_column(df)

    if text_column is None:
        st.error(
            "No text column was found. Your dataset needs a column "
            "such as text, comment, content, review, or message."
        )

        st.write("Available columns:", list(df.columns))
        return

    sentiment_column = find_column(
        df,
        ["sentiment", "predicted_sentiment", "sentiment_label"],
    )

    emotion_column = find_column(
        df,
        ["emotion", "predicted_emotion", "emotion_label"],
    )

    data = df.copy()

    data[text_column] = (
        data[text_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data = data[data[text_column] != ""].copy()

    if data.empty:
        st.warning("The selected text column contains no usable text.")
        return

    # Normalize sentiment and emotion labels.
    if sentiment_column:
        data[sentiment_column] = data[sentiment_column].apply(
            sentiment_label
        )

    if emotion_column:
        data[emotion_column] = (
            data[emotion_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.title()
        )

    st.caption(
        f"Source: {st.session_state.get('analysis_source', st.session_state.get('universal_analysis_filename', 'Current analysis'))}"
    )

    # --------------------------------------------------------
    # KEY METRICS
    # --------------------------------------------------------

    texts = data[text_column].tolist()
    word_counts = build_word_counts(texts)
    phrase_counts = build_phrase_counts(texts, 2)
    triple_counts = build_phrase_counts(texts, 3)

    top_words = word_counts.most_common(15)
    top_phrases = phrase_counts.most_common(10)
    top_triples = triple_counts.most_common(10)

    total_records = len(data)
    total_words = sum(len(clean_words(text)) for text in texts)
    unique_words = len(word_counts)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Analyzed Records", f"{total_records:,}")
    c2.metric("Words Processed", f"{total_words:,}")
    c3.metric("Unique Topics", f"{unique_words:,}")
    c4.metric(
        "Repeated Phrases",
        sum(count for _, count in top_phrases),
    )

    # --------------------------------------------------------
    # POPULAR TOPICS
    # --------------------------------------------------------

    st.divider()
    st.subheader("🔥 Most Discussed Topics")

    if top_words:
        topics_df = pd.DataFrame(
            top_words,
            columns=["Topic", "Mentions"],
        ).sort_values("Mentions")

        fig = px.bar(
            topics_df,
            x="Mentions",
            y="Topic",
            orientation="h",
            text="Mentions",
            color="Mentions",
            color_continuous_scale="Viridis",
            title="Most Frequently Mentioned Topics",
        )

        fig.update_layout(
            height=max(400, len(topics_df) * 32),
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Topic Highlights")

        st.markdown(
            " ".join(
                f'<span style="display:inline-block;padding:7px 12px;'
                f'margin:4px;border-radius:18px;background:#7057c8;'
                f'color:white">{topic} ({count})</span>'
                for topic, count in top_words[:12]
            ),
            unsafe_allow_html=True,
        )
    else:
        st.info("No meaningful keywords were found in the uploaded text.")

    # --------------------------------------------------------
    # COMMON PHRASES
    # --------------------------------------------------------

    st.divider()
    st.subheader("💬 Common Phrases")

    left, right = st.columns(2)

    with left:
        if top_phrases:
            phrase_df = pd.DataFrame(
                top_phrases,
                columns=["Phrase", "Mentions"],
            ).sort_values("Mentions")

            fig = px.bar(
                phrase_df,
                x="Mentions",
                y="Phrase",
                orientation="h",
                text="Mentions",
                title="Common Two-Word Phrases",
                color="Mentions",
                color_continuous_scale="Viridis",
            )

            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No repeated two-word phrases were found.")

    with right:
        if top_triples:
            triple_df = pd.DataFrame(
                top_triples,
                columns=["Phrase", "Mentions"],
            ).sort_values("Mentions")

            fig = px.bar(
                triple_df,
                x="Mentions",
                y="Phrase",
                orientation="h",
                text="Mentions",
                title="Common Three-Word Phrases",
                color="Mentions",
                color_continuous_scale="Plasma",
            )

            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No repeated three-word phrases were found.")

    # --------------------------------------------------------
    # SENTIMENT OVERVIEW
    # --------------------------------------------------------

    st.divider()
    st.subheader("😊 Audience Sentiment")

    if sentiment_column:
        sentiment_counts = (
            data[sentiment_column]
            .value_counts()
            .rename_axis("Sentiment")
            .reset_index(name="Records")
        )

        sentiment_counts = sentiment_counts[
            sentiment_counts["Sentiment"] != "Unknown"
        ]

        if not sentiment_counts.empty:
            left, right = st.columns(2)

            with left:
                fig = px.pie(
                    sentiment_counts,
                    names="Sentiment",
                    values="Records",
                    hole=0.5,
                    title="Sentiment Distribution",
                    color="Sentiment",
                    color_discrete_map={
                        "Positive": "#16A34A",
                        "Neutral": "#CA8A04",
                        "Negative": "#DC2626",
                    },
                )

                st.plotly_chart(fig, use_container_width=True)

            with right:
                fig = px.bar(
                    sentiment_counts,
                    x="Sentiment",
                    y="Records",
                    color="Sentiment",
                    text="Records",
                    title="Sentiment Comparison",
                )

                st.plotly_chart(fig, use_container_width=True)

            top_topics = [topic for topic, _ in top_words[:12]]

            topic_sentiment = build_topic_sentiment(
                data,
                text_column,
                sentiment_column,
                top_topics,
            )

            if not topic_sentiment.empty:
                st.subheader("Sentiment Across Trending Topics")

                fig = px.bar(
                    topic_sentiment,
                    x="Topic",
                    y="Mentions",
                    color="Sentiment",
                    barmode="group",
                    text="Mentions",
                )

                fig.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(
                    topic_sentiment,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No recognized sentiment labels are available.")
    else:
        st.info(
            "This dataset has not been analyzed for sentiment. "
            "Run Analyze file in CSV Upload to enable sentiment trends."
        )

    # --------------------------------------------------------
    # EMOTION ANALYSIS
    # --------------------------------------------------------

    st.divider()
    st.subheader("🎭 Emotion Trends")

    if emotion_column:
        emotion_data = data[
            ~data[emotion_column].str.lower().isin(
                ["", "nan", "none", "unknown"]
            )
        ]

        if not emotion_data.empty:
            emotion_counts = (
                emotion_data[emotion_column]
                .value_counts()
                .rename_axis("Emotion")
                .reset_index(name="Records")
            )

            fig = px.bar(
                emotion_counts,
                x="Emotion",
                y="Records",
                color="Emotion",
                text="Records",
                title="Emotion Distribution",
            )

            st.plotly_chart(fig, use_container_width=True)

            top_topics = [topic for topic, _ in top_words[:10]]

            topic_emotions = build_topic_emotions(
                data,
                text_column,
                emotion_column,
                top_topics,
            )

            if not topic_emotions.empty:
                st.subheader("Emotions Connected to Topics")

                fig = px.bar(
                    topic_emotions,
                    x="Topic",
                    y="Mentions",
                    color="Emotion",
                    barmode="stack",
                    text="Mentions",
                )

                fig.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No usable emotion labels are available.")
    else:
        st.info(
            "Emotion results are unavailable. Run the file analysis "
            "first to generate emotion labels."
        )

    # --------------------------------------------------------
    # AUTOMATIC INSIGHTS
    # --------------------------------------------------------

    st.divider()
    st.subheader("💡 Automatic Trend Insights")

    if top_words:
        top_topic, top_count = top_words[0]

        second_topic = (
            top_words[1][0] if len(top_words) > 1 else "N/A"
        )

        third_topic = (
            top_words[2][0] if len(top_words) > 2 else "N/A"
        )

        st.markdown(
            f"""
            **Most discussed topic:** {top_topic} ({top_count} records)

            **Other popular topics:** {second_topic}, {third_topic}

            **Most repeated phrase:** {
                top_phrases[0][0] if top_phrases else "None detected"
            }
            """
        )

        if sentiment_column:
            valid_sentiments = data[
                data[sentiment_column] != "Unknown"
            ][sentiment_column]

            if not valid_sentiments.empty:
                dominant_sentiment = valid_sentiments.mode().iloc[0]
                st.write(
                    f"**Dominant audience sentiment:** {dominant_sentiment}"
                )

        if emotion_column:
            valid_emotions = data[
                ~data[emotion_column].str.lower().isin(
                    ["", "nan", "none", "unknown"]
                )
            ][emotion_column]

            if not valid_emotions.empty:
                dominant_emotion = valid_emotions.mode().iloc[0]
                st.write(
                    f"**Dominant detected emotion:** {dominant_emotion}"
                )
    else:
        st.info("There is not enough text to generate trend insights.")

    # --------------------------------------------------------
    # RECORD EXPLORER
    # --------------------------------------------------------

    st.divider()
    st.subheader("🔎 Explore Records")

    search_query = st.text_input(
        "Search uploaded content",
        placeholder="Search for a word or phrase...",
        key="trend_search_query",
    )

    filtered = data.copy()

    if search_query.strip():
        filtered = filtered[
            filtered[text_column].str.contains(
                search_query.strip(),
                case=False,
                regex=False,
                na=False,
            )
        ]

    st.caption(f"{len(filtered):,} matching records")

    display_columns = [text_column]

    if sentiment_column:
        display_columns.append(sentiment_column)

    if emotion_column:
        display_columns.append(emotion_column)

    st.dataframe(
        filtered[display_columns].head(100),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    st.divider()
    st.subheader("⬇️ Export Trend Results")

    export_df = pd.DataFrame(
        top_words,
        columns=["Topic", "Mentions"],
    )

    st.download_button(
        "Download Trend Results",
        data=export_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="trend_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Download Filtered Records",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="trend_filtered_records.csv",
        mime="text/csv",
        use_container_width=True,
    )


show_trend = show


if __name__ == "__main__":
    show()
