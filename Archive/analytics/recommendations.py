def generate_recommendation(df):

    positive = len(df[df["sentiment"] == "positive"])
    neutral = len(df[df["sentiment"] == "neutral"])
    negative = len(df[df["sentiment"] == "negative"])

    total = len(df)

    positive_percent = (positive / total) * 100
    negative_percent = (negative / total) * 100

    recommendations = []

    if positive_percent >= 60:
        recommendations.append(
            "✅ Audience response is highly positive."
        )
        recommendations.append(
            "📢 Continue creating similar content."
        )

    elif negative_percent >= 40:
        recommendations.append(
            "⚠ Audience response is mostly negative."
        )
        recommendations.append(
            "📉 Review content quality and presentation."
        )

    else:
        recommendations.append(
            "🙂 Audience response is mixed."
        )
        recommendations.append(
            "📈 Improve engagement with better titles and thumbnails."
        )

    top_emotion = df["emotion"].mode()[0]

    recommendations.append(
        f"😊 Dominant Emotion: {top_emotion}"
    )

    recommendations.append(
        "🏷 Suggested Hashtags:"
    )

    recommendations.append(
        "#AI #MachineLearning #Python"
    )

    return recommendations