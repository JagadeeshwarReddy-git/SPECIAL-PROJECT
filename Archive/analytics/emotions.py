from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

def predict_emotion(text):

    result = emotion_classifier(str(text)[:512])[0][0]

    return {
        "emotion": result["label"],
        "score": round(result["score"], 4)
    }