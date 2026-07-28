# schema.py
import sqlite3
from module.constants import DB_NAME

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_text TEXT,
            score REAL,
            sentiment TEXT,
            patterns TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

def apply_indexes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Ignore errors if index already exists
    try:
        cursor.execute("CREATE INDEX idx_sentiment ON reviews(sentiment)")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("CREATE INDEX idx_score ON reviews(score)")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
