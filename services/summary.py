
"""Reusable summaries for completed analysis results."""

from collections import Counter
import re

import pandas as pd
import streamlit as st


TEXT_NAMES = (
    "text", "comment", "comments", "content", "review", "reviews",
    "message", "feedback", "description", "tweet", "post", "caption",
)

STOPWORDS = set("""
a an the and or but if while is are was were be been being to of
in on for from by with as at it its this that these those into about
over after before between during not no so than then there their they
them we our you your i he she his her who what when where why how can
could would should may might will do does did have has had also very
more most some any each other such only own same both few many much
one two just really
""".split())


def _text_column(df, preferred=None):
    """Find the most likely text column in a DataFrame."""

    if preferred is not None and preferred in df.columns:
        return preferred

    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in TEXT_NAMES:
        if name in lookup:
            return lookup[name]

    candidates = [
        column
        for column in df.columns
        if (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        )
    ]

    if not candidates:
        return None

    def average_length(column):
        values = df[column].dropna().astype(str)

        if values.empty:
            return 0

        return values.str.len().mean()

    return max(candidates, key=average_length)


def _extract_summary(texts, max_sentences=5):
    """
    Generate a local extractive summary by ranking sentences
    using the frequency of meaningful words.
    """

    joined = " ".join(
        str(value).strip()
        for value in texts
        if (
            value is not None
            and str(value).strip()
            and str(value).strip().lower() != "nan"
        )
    )

    if not joined:
        return "No readable text was available to summarize."

    sentences = [
        re.sub(r"\s+", " ", sentence).strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", joined)
    ]

    sentences = [
        sentence
        for sentence in sentences
        if len(sentence.split()) >= 4
    ]

    if not sentences:
        return joined[:1600]

    if len(sentences) <= max_sentences:
        return "\n\n".join(sentences)

    frequencies = Counter()
    tokenized_sentences = []

    for sentence in sentences:
        words = [
            word
            for word in re.findall(
                r"[a-zA-Z0-9']+", sentence.lower()
            )
            if len(word) > 2 and word not in STOPWORDS
        ]

        tokenized_sentences.append(words)
        frequencies.update(words)

    scored_sentences = []

    for index, words in enumerate(tokenized_sentences):
        if not words:
            score = 0
        else:
            score = sum(
                frequencies[word] for word in words
            ) / max(len(words) ** 0.5, 1)

        scored_sentences.append((score, index))

    top_sentences = sorted(
        scored_sentences,
        reverse=True,
    )[:max_sentences]

    selected_indices = sorted(
        index for _, index in top_sentences
    )

    return "\n\n".join(
        sentences[index]
        for index in selected_indices
    )


def render_analysis_summary(
    df,
    title="Analysis Summary",
    text_col=None,
    key_prefix="analysis_summary",
):
    """
    Display a summary of a completed analysis DataFrame.

    Includes:
    - Number of analyzed records
    - Dominant sentiment and emotion, when available
    - Important sentences from the text
    - Sentiment and emotion distributions
    - Downloadable summary
    """

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info(
            "Complete an analysis first to generate its summary."
        )
        return None

    column = _text_column(df, text_col)

    if column is not None:
        texts = (
            df[column]
            .fillna("")
            .astype(str)
            .tolist()
        )
    else:
        texts = []

    summary = _extract_summary(texts)

    sentiment_names = {
        "sentiment",
        "predicted_sentiment",
        "sentiment_label",
        "analytics_sentiment",
        "dashboard_sentiment",
        "report_sentiment",
    }

    emotion_names = {
        "emotion",
        "predicted_emotion",
        "analytics_emotion",
    }

    sentiment_col = next(
        (
            col for col in df.columns
            if str(col).strip().lower() in sentiment_names
        ),
        None,
    )

    emotion_col = next(
        (
            col for col in df.columns
            if str(col).strip().lower() in emotion_names
        ),
        None,
    )

    if sentiment_col is not None:
        sentiments = (
            df[sentiment_col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.title()
        )

        valid_sentiments = sentiments[
            sentiments.isin(
                ["Positive", "Neutral", "Negative"]
            )
        ]

        dominant_sentiment = (
            valid_sentiments.value_counts().idxmax()
            if not valid_sentiments.empty
            else "Not available"
        )
    else:
        sentiments = pd.Series(dtype=str)
        dominant_sentiment = "Not available"

    if emotion_col is not None:
        emotions = (
            df[emotion_col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.title()
        )

        valid_emotions = emotions[
            ~emotions.isin(
                ["", "Unknown", "Nan", "None"]
            )
        ]

        dominant_emotion = (
            valid_emotions.value_counts().idxmax()
            if not valid_emotions.empty
            else "Not available"
        )
    else:
        emotions = pd.Series(dtype=str)
        valid_emotions = pd.Series(dtype=str)
        dominant_emotion = "Not available"

    st.markdown(f"### 🧾 {title}")

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Records analyzed",
        f"{len(df):,}",
    )

    metric_columns[1].metric(
        "Dominant sentiment",
        dominant_sentiment,
    )

    metric_columns[2].metric(
        "Dominant emotion",
        dominant_emotion,
    )

    metric_columns[3].metric(
        "Text column",
        str(column) if column is not None else "Not found",
    )

    st.markdown("**Summary**")
    st.write(summary)

    details = []

    if sentiment_col is not None:
        counts = sentiments.value_counts()
        total = max(len(df), 1)

        distribution = ", ".join(
            f"{label}: {int(count)} ({count / total:.1%})"
            for label, count in counts.items()
        )

        details.append(
            f"Sentiment distribution: {distribution}"
        )

    if emotion_col is not None:
        emotion_counts = valid_emotions.value_counts().head(5)

        if not emotion_counts.empty:
            distribution = ", ".join(
                f"{label} ({int(count)})"
                for label, count in emotion_counts.items()
            )

            details.append(
                f"Most common emotions: {distribution}"
            )

    if details:
        st.markdown("**Key findings**")

        for detail in details:
            st.markdown(f"- {detail}")

    downloadable = f"{title}\n\n{summary}"

    if details:
        downloadable += "\n\n" + "\n".join(details)

    safe_key = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        key_prefix,
    )

    st.download_button(
        label="⬇️ Download analysis summary",
        data=downloadable,
        file_name="analysis_summary.txt",
        mime="text/plain",
        key=f"{safe_key}_download",
    )

    return downloadable
