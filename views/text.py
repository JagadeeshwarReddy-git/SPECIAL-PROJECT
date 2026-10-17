
import html

import pandas as pd
import streamlit as st

from services.analyzer import analyze_text
from services.explanation_service import (
    explain_sentiment,
    explain_emotion,
)
from views.history import save_history


def _sentiment_label(value):
    value = str(value).lower()

    if value == "positive":
        return "Positive"
    if value == "negative":
        return "Negative"
    if value == "neutral":
        return "Neutral"

    return value.capitalize()


def _result_card(title, value, confidence, icon):
    st.markdown(
        f"""
        <div class="text-result-card">
            <div class="text-result-icon">{icon}</div>
            <div class="text-result-label">{title}</div>
            <div class="text-result-value">
                {html.escape(str(value))}
            </div>
            <div class="text-result-confidence">
                Confidence&nbsp;&nbsp;
                <strong>{confidence:.1%}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show():
    # ---------------------------------------------------------
    # Styling
    # ---------------------------------------------------------
    st.markdown(
        """
        <style>
        .text-page-title {
            font-size: 32px;
            font-weight: 700;
            margin: 8px 0 4px;
            letter-spacing: -0.5px;
        }

        .text-page-subtitle {
            color: #64748b;
            font-size: 15px;
            margin-bottom: 24px;
        }

        .text-input-card {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 22px;
        }

        .text-card-title {
            font-size: 18px;
            font-weight: 650;
            margin-bottom: 5px;
        }

        .text-card-description {
            color: #64748b;
            font-size: 13px;
            margin-bottom: 14px;
        }

        .text-result-card {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 19px;
            min-height: 145px;
        }

        .text-result-icon {
            font-size: 23px;
            margin-bottom: 9px;
        }

        .text-result-label {
            color: #64748b;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .text-result-value {
            font-size: 21px;
            font-weight: 700;
            overflow-wrap: anywhere;
        }

        .text-result-confidence {
            color: #64748b;
            font-size: 11px;
            margin-top: 9px;
        }

        .text-section-title {
            font-size: 20px;
            font-weight: 700;
            margin: 27px 0 13px;
        }

        .text-analysis-box {
            background: var(--secondary-background-color, #ffffff);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
        }

        .text-analysis-label {
            color: #64748b;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .text-analysis-content {
            font-size: 15px;
            line-height: 1.65;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .text-info {
            border-left: 3px solid #3b82f6;
            background: var(--secondary-background-color, #f8fafc);
            padding: 13px 16px;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.6;
        }

        .text-success {
            border: 1px solid #bbf7d0;
            background: #f0fdf4;
            color: #166534;
            padding: 11px 14px;
            border-radius: 8px;
            font-size: 13px;
            margin-top: 14px;
        }

        @media (prefers-color-scheme: dark) {
            .text-input-card,
            .text-result-card,
            .text-analysis-box {
                border-color: #334155;
            }

            .text-page-subtitle,
            .text-card-description,
            .text-result-label,
            .text-result-confidence,
            .text-analysis-label {
                color: #94a3b8;
            }

            .text-success {
                background: #052e16;
                border-color: #166534;
                color: #bbf7d0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------
    st.markdown(
        '<div class="text-page-title">✍️ Text Analyzer</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="text-page-subtitle">'
        "Enter a sentence, comment, review, or short piece of text "
        "to analyze its sentiment and emotion."
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Input
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="text-input-card">
            <div class="text-card-title">Enter text to analyze</div>
            <div class="text-card-description">
                The text will be processed using the project's
                sentiment and emotion models.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    text = st.text_area(
        "Text",
        placeholder=(
            "Example: I really enjoyed this product. "
            "The quality is excellent and I would definitely "
            "recommend it."
        ),
        height=190,
        label_visibility="collapsed",
        key="text_analyzer_input",
    )

    char_count = len(text.strip())
    word_count = len(text.split()) if text.strip() else 0

    c1, c2 = st.columns(2)

    with c1:
        st.caption(f"Characters: {char_count:,}")

    with c2:
        st.caption(f"Words: {word_count:,}")

    analyze_clicked = st.button(
        "🔍 Analyze Text",
        use_container_width=True,
        type="primary",
    )

    if not analyze_clicked:
        st.markdown(
            """
            <div class="text-info" style="margin-top:18px;">
                <strong>Tip:</strong> Try a complete sentence or a
                short review for a more meaningful result.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    if not text.strip():
        st.warning("Please enter some text before starting the analysis.")
        return

    cleaned_text = text.strip()

    # ---------------------------------------------------------
    # Sentiment and emotion analysis
    # ---------------------------------------------------------
    try:
        with st.spinner("Analyzing your text..."):
            result = analyze_text(cleaned_text)

        sentiment = str(
            result.get("sentiment", "neutral")
        ).lower()

        sentiment_score = float(
            result.get("sentiment_score", 0.0)
        )

        emotion = str(
            result.get("emotion", "neutral")
        ).lower()

        emotion_score = float(
            result.get("emotion_score", 0.0)
        )

    except Exception as e:
        st.error(
            "The text could not be analyzed right now. "
            "Please check your model setup and try again."
        )
        with st.expander("Technical error details"):
            st.code(str(e))
        return

    # ---------------------------------------------------------
    # Explainable AI
    # ---------------------------------------------------------
    try:
        sentiment_explanation = explain_sentiment(
            cleaned_text,
            sentiment,
            sentiment_score,
        )

        emotion_explanation = explain_emotion(
            emotion,
            emotion_score,
        )

        if not isinstance(sentiment_explanation, dict):
            sentiment_explanation = {
                "sentiment_explanation": str(sentiment_explanation),
                "evidence_phrases": [],
            }

    except Exception as e:
        st.warning(
            "The predictions were generated, but the explanations "
            "could not be generated."
        )

        sentiment_explanation = {
            "sentiment_explanation": "Explanation unavailable.",
            "evidence_phrases": [],
        }
        emotion_explanation = "Explanation unavailable."

        with st.expander("Explanation error details"):
            st.code(str(e))

    sentiment_explanation_text = str(
        sentiment_explanation.get(
            "sentiment_explanation",
            "No explanation available.",
        )
    )

    evidence_phrases = sentiment_explanation.get(
        "evidence_phrases",
        [],
    )

    # ---------------------------------------------------------
    # Save current analysis for other modules
    # ---------------------------------------------------------
    df = pd.DataFrame(
        [
            {
                "text": cleaned_text,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "emotion": emotion,
                "emotion_score": emotion_score,
                "sentiment_explanation": sentiment_explanation_text,
                "evidence_phrases": str(evidence_phrases),
                "emotion_explanation": str(emotion_explanation),
            }
        ]
    )

    st.session_state.analysis_df = df

    sentiment_text = _sentiment_label(sentiment)
    emotion_text = emotion.capitalize()

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------
    st.markdown(
        '<div class="text-section-title">📊 Analysis Results</div>',
        unsafe_allow_html=True,
    )

    r1, r2 = st.columns(2)

    with r1:
        sentiment_icon = {
            "positive": "😊",
            "negative": "😟",
            "neutral": "😐",
        }.get(sentiment, "🔎")

        _result_card(
            "Sentiment",
            sentiment_text,
            sentiment_score,
            sentiment_icon,
        )

    with r2:
        _result_card(
            "Emotion",
            emotion_text,
            emotion_score,
            "🎭",
        )

    # ---------------------------------------------------------
    # Original text
    # ---------------------------------------------------------
    st.markdown(
        '<div class="text-section-title">📝 Analyzed Text</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="text-analysis-box">
            <div class="text-analysis-label">Your input</div>
            <div class="text-analysis-content">
                {html.escape(cleaned_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Result overview
    # ---------------------------------------------------------
    st.markdown(
        '<div class="text-section-title">💡 Result Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="text-info">
            The model classified the text as
            <strong>{html.escape(sentiment_text)}</strong>
            with a confidence of <strong>{sentiment_score:.1%}</strong>.
            The detected dominant emotion is
            <strong>{html.escape(emotion_text)}</strong>
            with a confidence of <strong>{emotion_score:.1%}</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Explainable AI panel
    # ---------------------------------------------------------
    st.markdown(
        '<div class="text-section-title">'
        '🧠 Explainable AI — Why These Predictions?'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("### 😊 Sentiment Explanation")

        st.write(sentiment_explanation_text)

        st.markdown("**Potential text clues**")
        st.write(evidence_phrases)

        st.divider()

        st.markdown("### 🎭 Emotion Explanation")
        st.write(emotion_explanation)

        st.caption(
            "These explanations use predefined language clues and "
            "descriptions of the predicted labels. They do not reveal "
            "the model's internal reasoning."
        )

    # ---------------------------------------------------------
    # Technical model output
    # ---------------------------------------------------------
    model_output = {
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 4),
        "emotion": emotion,
        "emotion_score": round(emotion_score, 4),
        "sentiment_explanation": sentiment_explanation,
        "emotion_explanation": emotion_explanation,
    }

    with st.expander("🔎 View model output"):
        st.json(model_output)

    # ---------------------------------------------------------
    # Save full analysis to History
    # ---------------------------------------------------------
    try:
        save_history(
            analysis_type="Text",
            records_count=1,
            sentiment=sentiment_text,
            emotion=emotion_text,
            source_name=cleaned_text[:80],
            details={
                "text": cleaned_text,
                "records": [
                    {
                        "text": cleaned_text,
                        "sentiment": sentiment,
                        "sentiment_score": sentiment_score,
                        "emotion": emotion,
                        "emotion_score": emotion_score,
                        "sentiment_explanation": sentiment_explanation_text,
                        "evidence_phrases": evidence_phrases,
                        "emotion_explanation": emotion_explanation,
                    }
                ],
                "metadata": {
                    "analysis_type": "Text",
                    "character_count": len(cleaned_text),
                    "word_count": len(cleaned_text.split()),
                    "sentiment_confidence": sentiment_score,
                    "emotion_confidence": emotion_score,
                    "sentiment_explanation": sentiment_explanation_text,
                    "evidence_phrases": evidence_phrases,
                    "emotion_explanation": emotion_explanation,
                },
            },
        )

    except Exception as e:
        st.warning(
            "Analysis completed, but the History entry could "
            "not be saved."
        )

        with st.expander("History error details"):
            st.code(str(e))

    # ---------------------------------------------------------
    # Completion message
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="text-success">
            ✓ Text analysis completed successfully.
        </div>
        """,
        unsafe_allow_html=True,
    )


show_text = show
