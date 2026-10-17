from collections import Counter
import re

def get_top_keywords(df, top_n=10):

    text = " ".join(df["clean_comment"].astype(str))

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

    stop_words = {
        "the","and","for","that","this","with","you","your",
        "are","was","were","have","has","had","they","them",
        "from","not","but","all","can","will","just","its",
        "it's","about","what","when","where","who","why",
        "how","our","their","his","her","she","him","out",
        "too","very","been","into","than","then","there",
        "also","because","would","could","should","did",
        "does","doing","after","before","over","under",
        "more","most","only","really","video","youtube"
    }

    words = [w for w in words if w not in stop_words]

    counter = Counter(words)

    return counter.most_common(top_n)