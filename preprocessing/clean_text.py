import re
import emoji

def clean_text(text):

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove emojis
    text = emoji.replace_emoji(text, replace="")

    # Remove hashtags
    text = re.sub(r"#\w+", "", text)

    # Remove mentions
    text = re.sub(r"@\w+", "", text)

    # Remove punctuation and numbers
    text = re.sub(r"[^a-zA-Z ]", "", text)

    # Remove extra spaces
    text = " ".join(text.split())

    return text