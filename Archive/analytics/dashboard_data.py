import pandas as pd

def get_summary(df):

    sentiment_counts = df["sentiment"].value_counts()

    emotion_counts = df["emotion"].value_counts()

    return {

        "total_comments": len(df),

        "positive": sentiment_counts.get("positive", 0),

        "neutral": sentiment_counts.get("neutral", 0),

        "negative": sentiment_counts.get("negative", 0),

        "top_emotions": emotion_counts.to_dict()

    }