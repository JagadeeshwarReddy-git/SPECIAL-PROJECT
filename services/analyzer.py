from transformers import pipeline
from functools import lru_cache
import time


# ==========================================
# Model Configuration
# ==========================================

SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

MAX_RETRIES = 3
RETRY_DELAY = 3


# ==========================================
# Helper: Load Pipeline With Retry
# ==========================================

def load_pipeline_with_retry(task, model_name, **kwargs):

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            print(
                f"Loading model: {model_name} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            model = pipeline(
                task,
                model=model_name,
                **kwargs
            )

            print(f"Model loaded successfully: {model_name}")

            return model

        except Exception as e:

            last_error = e

            print(
                f"Failed to load {model_name} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            print(f"Error: {e}")

            if attempt < MAX_RETRIES:
                print(
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"\nUnable to load Hugging Face model:\n"
        f"{model_name}\n\n"
        f"Please check your internet connection and try again.\n\n"
        f"Original error:\n{last_error}"
    )


# ==========================================
# Load Sentiment Model
# ==========================================

@lru_cache(maxsize=1)
def get_sentiment_model():

    return load_pipeline_with_retry(
        "sentiment-analysis",
        SENTIMENT_MODEL
    )


# ==========================================
# Load Emotion Model
# ==========================================

@lru_cache(maxsize=1)
def get_emotion_model():

    return load_pipeline_with_retry(
        "text-classification",
        EMOTION_MODEL,
        top_k=1
    )


# ==========================================
# Clean Text
# ==========================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text).strip()

    # Limit input length
    text = text[:500]

    return text


# ==========================================
# Sentiment Analysis
# ==========================================

def analyze_sentiment(text):

    text = clean_text(text)

    if not text:
        return {
            "label": "neutral",
            "score": 0.0
        }

    try:

        model = get_sentiment_model()

        result = model(
            text,
            truncation=True,
            max_length=512
        )[0]

        return {
            "label": str(result["label"]).lower(),
            "score": float(result["score"])
        }

    except Exception as e:

        print(f"Sentiment analysis error: {e}")

        raise RuntimeError(
            f"Sentiment analysis failed.\n\n{e}"
        )


# ==========================================
# Emotion Analysis
# ==========================================

def analyze_emotion(text):

    text = clean_text(text)

    if not text:
        return {
            "emotion": "neutral",
            "score": 0.0
        }

    try:

        model = get_emotion_model()

        result = model(
            text,
            truncation=True,
            max_length=512
        )

        # top_k=1 normally returns:
        # [[{"label": "...", "score": ...}]]

        if (
            isinstance(result, list)
            and len(result) > 0
            and isinstance(result[0], list)
            and len(result[0]) > 0
        ):
            result = result[0][0]

        # Safety for alternate Transformers output format
        elif (
            isinstance(result, list)
            and len(result) > 0
            and isinstance(result[0], dict)
        ):
            result = result[0]

        else:
            raise ValueError(
                f"Unexpected emotion model output: {result}"
            )

        return {
            "emotion": str(result["label"]),
            "score": float(result["score"])
        }

    except Exception as e:

        print(f"Emotion analysis error: {e}")

        raise RuntimeError(
            f"Emotion analysis failed.\n\n{e}"
        )


# ==========================================
# Complete Text Analysis
# ==========================================

def analyze_text(text):

    text = clean_text(text)

    if not text:

        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "emotion": "neutral",
            "emotion_score": 0.0
        }

    sentiment = analyze_sentiment(text)

    emotion = analyze_emotion(text)

    return {
        "sentiment": sentiment["label"],
        "sentiment_score": sentiment["score"],
        "emotion": emotion["emotion"],
        "emotion_score": emotion["score"]
    }