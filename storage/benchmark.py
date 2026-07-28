# benchmark.py
import sqlite3
import time
from module.constants import DB_NAME

def benchmark_queries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    queries = [
        "SELECT COUNT(*) FROM reviews WHERE sentiment='Positive'",
        "SELECT AVG(score) FROM reviews",
        "SELECT * FROM reviews WHERE score > 2 LIMIT 1000"
    ]

    start = time.time()

    for q in queries:
        cursor.execute(q)
        cursor.fetchall()

    end = time.time()
    conn.close()

    return round(end - start, 4)
