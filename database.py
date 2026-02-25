# database.py
"""
Handles all database-related operations.
"""

import sqlite3

DB_NAME = "sentiment_project.db"


def setup_database():
    """
    Initializes the SQLite database.
    Drops existing table and creates a fresh one.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS reviews")

    cursor.execute("""
        CREATE TABLE reviews (
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


def insert_results(results):
    """
    Performs batch insertion of processed reviews.

    Args:
        results (list): List of tuples containing
                        (text, score, sentiment, patterns, timestamp)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO reviews
        (review_text, score, sentiment, patterns, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, results)

    conn.commit()
    conn.close()


def apply_indexes():
    """
    Creates indexes on frequently queried columns
    to improve SELECT performance.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("CREATE INDEX idx_sentiment ON reviews(sentiment)")
    cursor.execute("CREATE INDEX idx_score ON reviews(score)")

    conn.commit()
    conn.close()