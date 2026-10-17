import pandas as pd
import ollama

MODEL = "llama3.2"


def prepare_dataset(dataframe):
    """
    Convert the current analysis dataframe into a compact summary
    that the local AI model can understand.
    """

    if dataframe is None or dataframe.empty:
        return "No analysis data is currently available."

    df = dataframe.copy()

    context = []

    # Total records
    context.append(f"Total analyzed records: {len(df)}")

    # Sentiment information
    if "sentiment" in df.columns:
        sentiment_counts = (
            df["sentiment"]
            .astype(str)
            .str.lower()
            .value_counts()
            .to_dict()
        )

        context.append(
            f"Sentiment distribution: {sentiment_counts}"
        )

    # Emotion information
    if "emotion" in df.columns:
        emotion_counts = (
            df["emotion"]
            .astype(str)
            .str.lower()
            .value_counts()
            .to_dict()
        )

        context.append(
            f"Emotion distribution: {emotion_counts}"
        )

    # Likes information
    if "likes" in df.columns:
        likes = pd.to_numeric(
            df["likes"],
            errors="coerce"
        ).fillna(0)

        context.append(
            f"Total likes: {int(likes.sum())}"
        )

        context.append(
            f"Average likes: {likes.mean():.2f}"
        )

    # Find text/comment column
    possible_text_columns = [
        "comment",
        "text",
        "comments",
        "content"
    ]

    text_column = None

    for column in possible_text_columns:
        if column in df.columns:
            text_column = column
            break

    # Add sample comments
    if text_column:
        samples = (
            df[text_column]
            .dropna()
            .astype(str)
            .head(15)
            .tolist()
        )

        if samples:
            context.append("Sample comments:")

            for i, comment in enumerate(samples, 1):
                context.append(
                    f"{i}. {comment[:300]}"
                )

    return "\n".join(context)


def ask_ai(question, dataframe):
    """
    Ask the local Ollama model a question about
    the current social-media analysis.
    """

    if not question or not question.strip():
        return "Please enter a question."

    if dataframe is None or dataframe.empty:
        return (
            "No analysis data is available yet. "
            "Please analyze YouTube comments, text, or a CSV file first."
        )

    dataset_context = prepare_dataset(dataframe)

    prompt = f"""
You are an AI assistant inside an AI-Based Social Media Analytics application.

Your job is to explain the analyzed social-media data clearly.

Use ONLY the provided analysis data when making claims about the dataset.
Do not invent statistics.

ANALYSIS DATA:
{dataset_context}

USER QUESTION:
{question}

Instructions:
- Give a clear and concise answer.
- Use the sentiment and emotion results when relevant.
- Mention actual numbers when available.
- If the available data cannot answer the question, clearly say so.
- Do not invent comments, statistics, trends, or facts.
- For recommendations, clearly base them on the supplied analysis.
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:

        error_message = str(e)

        if "connection" in error_message.lower():
            return (
                "⚠️ Ollama is not running.\n\n"
                "Start Ollama and try again."
            )

        if "not found" in error_message.lower():
            return (
                f"⚠️ The local model '{MODEL}' was not found.\n\n"
                f"Run: ollama pull {MODEL}"
            )

        return (
            "⚠️ The local AI assistant encountered an error.\n\n"
            f"{error_message}"
        )