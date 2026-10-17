import sqlite3

# ==========================================
# Database Connection
# ==========================================

DB_NAME = "social_media.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# ==========================================
# Users Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
)
""")

# ==========================================
# Analysis Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    positive INTEGER,
    neutral INTEGER,
    negative INTEGER,
    emotion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================
# History Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ==========================================
# Reports Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# ==========================================
# USER FUNCTIONS
# ==========================================

def register_user(username, email, password):
    cursor.execute(
        """
        INSERT INTO users(username,email,password)
        VALUES(?,?,?)
        """,
        (username, email, password)
    )
    conn.commit()


def login_user(username, password):
    cursor.execute(
        """
        SELECT * FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    )
    return cursor.fetchone()


# ==========================================
# ANALYSIS FUNCTIONS
# ==========================================

def save_analysis(source, title, positive, neutral, negative, emotion):
    cursor.execute(
        """
        INSERT INTO analysis
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


def get_analysis():
    cursor.execute("""
    SELECT *
    FROM analysis
    ORDER BY id DESC
    """)
    return cursor.fetchall()


# ==========================================
# HISTORY FUNCTIONS
# ==========================================

def save_history(action):
    cursor.execute(
        """
        INSERT INTO history(action)
        VALUES(?)
        """,
        (action,)
    )
    conn.commit()


def get_history():
    cursor.execute("""
    SELECT *
    FROM history
    ORDER BY id DESC
    """)
    return cursor.fetchall()


# ==========================================
# REPORT FUNCTIONS
# ==========================================

def save_report(report_name):
    cursor.execute(
        """
        INSERT INTO reports(report_name)
        VALUES(?)
        """,
        (report_name,)
    )
    conn.commit()


def get_reports():
    cursor.execute("""
    SELECT *
    FROM reports
    ORDER BY id DESC
    """)
    return cursor.fetchall()


# ==========================================
# CLOSE DATABASE
# ==========================================

def close_connection():
    conn.close()