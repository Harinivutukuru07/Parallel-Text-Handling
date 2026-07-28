# queries.py
import sqlite3
from module.constants import DB_NAME

def insert_results(results):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() 

    cursor.executemany("""
        INSERT INTO reviews
        (review_text, score, sentiment, patterns, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, results)

    conn.commit()
    conn.close()

def get_sample_results(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, score, sentiment, created_at FROM reviews LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return rows
