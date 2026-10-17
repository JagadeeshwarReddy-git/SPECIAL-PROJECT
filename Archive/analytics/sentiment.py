from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def predict_sentiment(text):
    result = classifier(text[:512])[0]

    return {
        "sentiment": result["label"],
        "score": round(result["score"], 4)
    }