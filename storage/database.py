"""
Handles all database-related operations.
"""

import sqlite3
import time

DB_NAME = "sentiment_project.db"
LOCK_RETRY_ATTEMPTS = 5
LOCK_RETRY_DELAY_SECONDS = 0.5


def _get_connection():
    """
    Creates a SQLite connection configured for transient lock handling.
    """
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _execute_with_retry(operation):
    """
    Retries a DB operation when SQLite reports a temporary lock.
    """
    for attempt in range(1, LOCK_RETRY_ATTEMPTS + 1):
        try:
            return operation()
        except sqlite3.OperationalError as exc:
            message = str(exc).lower()
            is_locked = "database is locked" in message or "database table is locked" in message
            if not is_locked or attempt == LOCK_RETRY_ATTEMPTS:
                raise
            time.sleep(LOCK_RETRY_DELAY_SECONDS * attempt)


def setup_database():
    """
    Initializes the SQLite database.
    Drops existing table and creates a fresh one.
    """
    def _operation():
        with _get_connection() as conn:
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
            cursor.execute("DELETE FROM reviews")
            conn.commit()

    _execute_with_retry(_operation)


def insert_results(results):
    """
    Performs batch insertion of processed reviews.

    Args:
        results (list): List of tuples containing
                        (text, score, sentiment, patterns, timestamp)
    """
    def _operation():
        with _get_connection() as conn:
            cursor = conn.cursor()

            cursor.executemany("""
                INSERT INTO reviews
                (review_text, score, sentiment, patterns, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, results)

            conn.commit()

    _execute_with_retry(_operation)


def apply_indexes():
    """
    Creates indexes on frequently queried columns
    to improve SELECT performance.
    """
    def _operation():
        with _get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON reviews(sentiment)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_score ON reviews(score)")

            conn.commit()

    _execute_with_retry(_operation)
