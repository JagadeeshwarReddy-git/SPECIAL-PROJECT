
import re
import pandas as pd


# ============================================================
# SENTIMENT EVIDENCE KEYWORDS
# These phrases help explain a prediction.
# They do not reveal the model's internal reasoning.
# ============================================================

POSITIVE_PHRASES = [
    "absolutely love",
    "highly recommend",
    "very helpful",
    "really helpful",
    "excellent service",
    "great service",
    "amazing experience",
    "wonderful experience",
    "works perfectly",
    "easy to use",
    "user friendly",
    "well designed",
    "good quality",
    "great quality",
    "value for money",
    "love it",
    "loved it",
    "love this",
    "best ever",
    "very good",
    "really good",
    "so good",
    "excellent",
    "amazing",
    "awesome",
    "fantastic",
    "wonderful",
    "brilliant",
    "perfect",
    "outstanding",
    "recommend",
    "helpful",
    "reliable",
    "beautiful",
    "enjoyable",
    "impressed",
    "happy",
    "satisfied",
    "smooth",
    "fast",
    "easy",
    "good",
    "great",
    "nice",
    "useful",
    "affordable",
    "convenient",
    "comfortable",
    "best",
    "thank you",
    "thanks",
]

NEGATIVE_PHRASES = [
    "do not recommend",
    "don't recommend",
    "would not recommend",
    "not worth it",
    "waste of money",
    "waste of time",
    "customer service is terrible",
    "poor customer service",
    "keeps crashing",
    "crashes frequently",
    "stopped working",
    "does not work",
    "doesn't work",
    "not working",
    "not satisfied",
    "very disappointed",
    "really disappointed",
    "extremely slow",
    "too expensive",
    "hard to use",
    "difficult to use",
    "bad experience",
    "poor quality",
    "worst experience",
    "never again",
    "hate it",
    "hate this",
    "hated it",
    "terrible",
    "horrible",
    "awful",
    "disappointing",
    "disappointed",
    "useless",
    "annoying",
    "frustrating",
    "frustrated",
    "broken",
    "buggy",
    "unreliable",
    "overpriced",
    "expensive",
    "slow",
    "crash",
    "crashes",
    "problem",
    "problems",
    "issue",
    "issues",
    "failure",
    "failed",
    "poor",
    "bad",
    "worst",
    "hate",
    "angry",
    "boring",
    "confusing",
    "rude",
    "late",
    "error",
    "errors",
]

# Words that can reverse the meaning of nearby sentiment words.
NEGATIONS = {
    "not",
    "no",
    "never",
    "hardly",
    "barely",
    "isn't",
    "wasn't",
    "weren't",
    "don't",
    "doesn't",
    "didn't",
    "can't",
    "couldn't",
    "won't",
    "wouldn't",
    "shouldn't",
}


def _clean_text(text):
    """Convert input into safe, normalized text."""
    if text is None:
        return ""

    try:
        if pd.isna(text):
            return ""
    except (TypeError, ValueError):
        pass

    return re.sub(r"\s+", " ", str(text)).strip()


def _normalize_sentiment(sentiment):
    """Normalize common sentiment labels."""
    label = str(sentiment or "").strip().lower()

    if label in {"positive", "pos", "label_2"}:
        return "positive"

    if label in {"negative", "neg", "label_0"}:
        return "negative"

    if label in {"neutral", "neu", "label_1"}:
        return "neutral"

    return label or "unknown"


def _find_matching_phrases(text, phrases):
    """
    Find phrases actually present in the text.

    Longer phrases are checked first to prioritize meaningful evidence.
    """
    normalized = _clean_text(text).lower()
    matches = []

    for phrase in sorted(phrases, key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

        if re.search(pattern, normalized):
            matches.append(phrase)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(matches))


def _is_negated(text, phrase):
    """
    Check for a nearby negation before a sentiment phrase.

    This is a simple heuristic, not a complete linguistic parser.
    """
    normalized = _clean_text(text).lower()
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

    match = re.search(pattern, normalized)

    if not match:
        return False

    preceding_text = normalized[:match.start()]
    preceding_words = re.findall(r"\b[\w']+\b", preceding_text)

    # Inspect the previous three words for a negation.
    nearby_words = preceding_words[-3:]

    return any(
        word in NEGATIONS
        for word in nearby_words
    )


def _get_evidence(text, sentiment):
    """
    Return evidence phrases that agree with the predicted sentiment.

    Opposite-polarity words are retained separately so mixed feedback
    is not incorrectly presented as one-sided.
    """
    positive_matches = _find_matching_phrases(
        text, POSITIVE_PHRASES
    )

    negative_matches = _find_matching_phrases(
        text, NEGATIVE_PHRASES
    )

    positive_evidence = []
    negative_evidence = []

    for phrase in positive_matches:
        if _is_negated(text, phrase):
            negative_evidence.append(
                f"not {phrase}"
            )
        else:
            positive_evidence.append(phrase)

    for phrase in negative_matches:
        if _is_negated(text, phrase):
            positive_evidence.append(
                f"not {phrase}"
            )
        else:
            negative_evidence.append(phrase)

    if sentiment == "positive":
        relevant = positive_evidence
        opposite = negative_evidence

    elif sentiment == "negative":
        relevant = negative_evidence
        opposite = positive_evidence

    else:
        relevant = []
        opposite = positive_evidence + negative_evidence

    return {
        "positive_evidence": list(dict.fromkeys(positive_evidence)),
        "negative_evidence": list(dict.fromkeys(negative_evidence)),
        "relevant_evidence": list(dict.fromkeys(relevant)),
        "opposite_evidence": list(dict.fromkeys(opposite)),
    }


def explain_sentiment(text, sentiment, confidence=None):
    """
    Explain a sentiment prediction using evidence from the input text.

    Returns:
        {
            "sentiment_explanation": str,
            "evidence_phrases": list
        }
    """
    text = _clean_text(text)
    sentiment = _normalize_sentiment(sentiment)

    if not text:
        return {
            "sentiment_explanation": (
                "No text was available to explain this prediction."
            ),
            "evidence_phrases": [],
        }

    evidence = _get_evidence(text, sentiment)
    relevant = evidence["relevant_evidence"]
    opposite = evidence["opposite_evidence"]

    if sentiment == "positive":
        if relevant:
            explanation = (
                "The model classified this feedback as positive. "
                "The text contains expressions such as "
                + ", ".join(
                    f'"{phrase}"' for phrase in relevant[:5]
                )
                + ", which are commonly associated with praise, "
                  "satisfaction, or approval."
            )
        else:
            explanation = (
                "The model classified this feedback as positive, "
                "but the explanation rules did not find a clear "
                "positive keyword or phrase. Review the original "
                "text before drawing conclusions."
            )

    elif sentiment == "negative":
        if relevant:
            explanation = (
                "The model classified this feedback as negative. "
                "The text contains expressions such as "
                + ", ".join(
                    f'"{phrase}"' for phrase in relevant[:5]
                )
                + ", which are commonly associated with criticism, "
                  "problems, dissatisfaction, or frustration."
            )
        else:
            explanation = (
                "The model classified this feedback as negative, "
                "but the explanation rules did not find a clear "
                "negative keyword or phrase. Review the original "
                "text before drawing conclusions."
            )

    elif sentiment == "neutral":
        if relevant:
            explanation = (
                "The model classified this feedback as neutral, "
                "but the explanation rules detected potentially "
                "opinion-related phrases: "
                + ", ".join(
                    f'"{phrase}"' for phrase in relevant[:5]
                )
                + ". The comment may contain mixed or subtle "
                  "sentiment, so its classification should be "
                  "reviewed in context."
            )
        else:
            explanation = (
                "The model classified this feedback as neutral. "
                "The explanation rules did not find a clear "
                "positive or negative expression in the text. "
                "It may be factual, informational, or ambiguous; "
                "this does not prove that the comment is emotionless."
            )

    else:
        explanation = (
            f"The sentiment label is '{sentiment}'. "
            "A standard positive, negative, or neutral explanation "
            "could not be generated."
        )

    if opposite:
        explanation += (
            " The text also contains potentially conflicting "
            "evidence: "
            + ", ".join(
                f'"{phrase}"' for phrase in opposite[:3]
            )
            + ". This may indicate mixed sentiment."
        )

    # Confidence is reported separately from the explanation.
    if confidence is not None:
        try:
            confidence_value = float(confidence)

            if 0 <= confidence_value <= 1:
                confidence_value *= 100

            explanation += (
                f" Model-reported confidence: "
                f"{confidence_value:.1f}%."
            )
        except (TypeError, ValueError):
            pass

    return {
        "sentiment_explanation": explanation,
        "evidence_phrases": relevant,
    }


def explain_emotion(emotion, confidence=None):
    """Explain a predicted emotion without claiming certainty."""
    emotion = str(emotion or "unknown").strip().lower()

    emotion_explanations = {
        "joy": "The model detected signals commonly associated with happiness or enjoyment.",
        "happiness": "The model detected signals commonly associated with happiness or enjoyment.",
        "sadness": "The model detected signals commonly associated with sadness or disappointment.",
        "anger": "The model detected signals commonly associated with anger, irritation, or frustration.",
        "fear": "The model detected signals commonly associated with fear, worry, or uncertainty.",
        "surprise": "The model detected signals commonly associated with surprise or an unexpected reaction.",
        "disgust": "The model detected signals commonly associated with dislike or strong aversion.",
        "love": "The model detected signals commonly associated with affection or strong positive attachment.",
        "neutral": "The model detected a relatively neutral emotional pattern.",
    }

    explanation = emotion_explanations.get(
        emotion,
        f"The model predicted the emotion '{emotion}'."
    )

    if confidence is not None:
        try:
            confidence_value = float(confidence)

            if 0 <= confidence_value <= 1:
                confidence_value *= 100

            explanation += (
                f" Model-reported confidence: "
                f"{confidence_value:.1f}%."
            )
        except (TypeError, ValueError):
            pass

    return explanation


def add_row_explanations(
    dataframe,
    text_col="text",
    sentiment_col="sentiment",
    sentiment_score_col="sentiment_score",
    emotion_col="emotion",
    emotion_score_col="emotion_score",
):
    """
    Add explanation columns to every row of a DataFrame.

    Original data is preserved; a copy is returned.
    """
    if dataframe is None:
        return pd.DataFrame()

    result = dataframe.copy()

    if result.empty:
        for column in [
            "sentiment_explanation",
            "evidence_phrases",
            "emotion_explanation",
        ]:
            result[column] = pd.Series(dtype="object")

        return result

    def explain_row(row):
        text = row.get(text_col, "")
        sentiment = row.get(sentiment_col, "unknown")

        confidence = (
            row.get(sentiment_score_col)
            if sentiment_score_col in result.columns
            else None
        )

        return explain_sentiment(
            text,
            sentiment,
            confidence,
        )

    sentiment_results = result.apply(explain_row, axis=1)

    result["sentiment_explanation"] = sentiment_results.apply(
        lambda item: item["sentiment_explanation"]
    )

    result["evidence_phrases"] = sentiment_results.apply(
        lambda item: ", ".join(item["evidence_phrases"])
    )

    if emotion_col in result.columns:
        if emotion_score_col in result.columns:
            result["emotion_explanation"] = result.apply(
                lambda row: explain_emotion(
                    row.get(emotion_col, "unknown"),
                    row.get(emotion_score_col),
                ),
                axis=1,
            )
        else:
            result["emotion_explanation"] = result[
                emotion_col
            ].apply(explain_emotion)
    else:
        result["emotion_explanation"] = (
            "Emotion analysis was not available for this record."
        )

    return result


def explain_distribution(dataframe, column):
    """Create a readable summary of a categorical distribution."""
    if dataframe is None or dataframe.empty:
        return "There is no data available to summarize."

    if column not in dataframe.columns:
        return f"The column '{column}' was not found."

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    if values.empty:
        return f"No valid values were found in '{column}'."

    counts = values.value_counts()
    total = int(counts.sum())

    parts = []

    for label, count in counts.items():
        percentage = (count / total) * 100

        parts.append(
            f"{label}: {count} records ({percentage:.1f}%)"
        )

    return (
        f"Distribution of {column}: "
        + "; ".join(parts)
        + "."
    )
