def generate_summary(df):

    positive = len(df[df["sentiment"] == "positive"])
    negative = len(df[df["sentiment"] == "negative"])
    neutral = len(df[df["sentiment"] == "neutral"])

    total = len(df)

    if positive > negative:
        mood = "Overall audience reaction is Positive."
    elif negative > positive:
        mood = "Overall audience reaction is Negative."
    else:
        mood = "Overall audience reaction is Neutral."

    return f"""
## Analysis Summary

Total Comments: {total}

Positive: {positive}

Neutral: {neutral}

Negative: {negative}

Conclusion: {mood}
"""