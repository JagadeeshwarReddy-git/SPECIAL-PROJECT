import sqlite3

conn = sqlite3.connect("analysis.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    positive INTEGER,
    neutral INTEGER,
    negative INTEGER,
    emotion TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def save_analysis(source, title, positive, neutral, negative, emotion):

    cursor.execute(
        """
        INSERT INTO analysis_history
        (source,title,positive,neutral,negative,emotion)
        VALUES(?,?,?,?,?,?)
        """,
        (
            source,
            title,
            positive,
            neutral,
            negative,
            emotion
        )
    )

    conn.commit()


def get_history():

    cursor.execute("""
        SELECT *
        FROM analysis_history
        ORDER BY id DESC
    """)

    return cursor.fetchall()