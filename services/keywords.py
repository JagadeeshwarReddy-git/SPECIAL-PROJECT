from collections import Counter
import re


def get_keywords(text, top=15):

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

    stopwords = {
        "the","and","for","that","this","with","have","has",
        "was","are","you","your","they","them","will","would",
        "from","about","there","their","into","here","when",
        "where","what","which","could","should","been","also"
    }

    words = [w for w in words if w not in stopwords]

    counter = Counter(words)

    return counter.most_common(top)