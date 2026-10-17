from wordcloud import WordCloud
import matplotlib.pyplot as plt


def generate_wordcloud(text):

    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white"
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12,6))

    ax.imshow(wc)

    ax.axis("off")

    return fig