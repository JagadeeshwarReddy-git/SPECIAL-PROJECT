import pandas as pd
from preprocessing.clean_text import clean_text
from analytics.sentiment import predict_sentiment
from analytics.emotion import predict_emotion

df = pd.read_csv("data/raw/youtube_comments.csv")

df["clean_comment"] = df["comment"].astype(str).apply(clean_text)

# Sentiment
sentiments = df["clean_comment"].apply(predict_sentiment)

df["sentiment"] = sentiments.apply(lambda x:x["sentiment"])

df["confidence"] = sentiments.apply(lambda x:x["score"])

# Emotion
emotions = df["clean_comment"].apply(predict_emotion)

df["emotion"] = emotions.apply(lambda x:x["emotion"])

df["emotion_score"] = emotions.apply(lambda x:x["score"])

df.to_csv(
    "data/cleaned/social_media_analysis.csv",
    index=False
)

print(
    df[
        [
            "comment",
            "sentiment",
            "emotion"
        ]
    ].head()
) 
from analytics.dashboard_data import get_summary

summary = get_summary(df)

print(summary)