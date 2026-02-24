# =========================================================
# PARALLEL TEXT HANDLING PROCESSOR
# =========================================================

import csv
import re
import time
import sqlite3
from datetime import datetime
from multiprocessing import Pool, cpu_count

DB_NAME = "sentiment_project.db"

# =========================================================
# MODULE 1: SENTIMENT RULES & PRECOMPILED PATTERNS
# =========================================================

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing",
    "love", "awesome", "nice", "perfect",
    "happy", "satisfied"
}

NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "worst",
    "hate", "awful", "disappointing",
    "sad", "horrible"
}

NEGATIONS = {"not", "no", "never", "none", "n't"}
INTENSIFIERS = {"very", "extremely", "really", "too", "so"}
DIMINISHERS = {"slightly", "little", "somewhat", "barely"}
CONTRAST_WORDS = {"but", "however", "though", "although"}

TOKEN_PATTERN = re.compile(r"\b\w+\b")

PATTERN_RULES = {
    "refund": re.compile(r"\brefund|money back|return\b"),
    "delivery_issue": re.compile(r"\b(delayed|late|not delivered)\b"),
    "product_damage": re.compile(r"\b(broken|damaged|defective)\b"),
    "customer_service": re.compile(r"\b(customer service|no response|rude)\b"),
    "price_complaint": re.compile(r"\b(expensive|overpriced|waste of money)\b"),
    "sarcasm": re.compile(r"\b(yeah right|as if|thanks for nothing)\b")
}

# =========================================================
# MODULE 2: SENTIMENT CALCULATION
# =========================================================

def calculate_score(text):
    words = TOKEN_PATTERN.findall(text.lower())
    score = 0
    weight = 1
    negate = False

    for word in words:

        if word in NEGATIONS:
            negate = True
            continue

        if word in INTENSIFIERS:
            weight = 2
            continue

        if word in DIMINISHERS:
            weight = 0.5
            continue

        if word in POSITIVE_WORDS:
            val = weight
            score += -val if negate else val
            negate = False
            weight = 1

        elif word in NEGATIVE_WORDS:
            val = -weight
            score += -val if negate else val
            negate = False
            weight = 1

    # Contrast handling (focus on part after "but")
    for contrast in CONTRAST_WORDS:
        if contrast in text.lower():
            parts = text.lower().split(contrast)
            if len(parts) > 1:
                return calculate_score(parts[-1])
            break

    return score


def assign_sentiment(score):
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"


def detect_patterns(text):
    text = text.lower()
    found = []

    for label, pattern in PATTERN_RULES.items():
        if pattern.search(text):
            found.append(label)

    return ",".join(found)

# =========================================================
# MODULE 3: DATABASE SETUP
# =========================================================

def setup_database():
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

# =========================================================
# MODULE 4: PARALLEL WORKER
# =========================================================

def process_text(text):
    score = calculate_score(text)
    sentiment = assign_sentiment(score)
    patterns = detect_patterns(text)
    return (text, score, sentiment, patterns, datetime.now().isoformat())

# =========================================================
# MODULE 5: BATCH INSERT (FAST)
# =========================================================

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

# =========================================================
# MODULE 6: PERFORMANCE BENCHMARKING
# =========================================================

def benchmark_queries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    queries = [
        "SELECT COUNT(*) FROM reviews WHERE sentiment='Positive'",
        "SELECT AVG(score) FROM reviews",
        "SELECT * FROM reviews WHERE score > 2"
    ]

    start = time.time()

    for q in queries:
        cursor.execute(q)
        cursor.fetchall()

    end = time.time()
    conn.close()

    return round(end - start, 4)

# =========================================================
# MODULE 7: INDEX OPTIMIZATION
# =========================================================

def apply_indexes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("CREATE INDEX idx_sentiment ON reviews(sentiment)")
    cursor.execute("CREATE INDEX idx_score ON reviews(score)")

    conn.commit()
    conn.close()

# =========================================================
# MAIN EXECUTION
# =========================================================

if __name__ == "__main__":

    setup_database()

    # Load CSV
    texts = []
    with open("Reviews.csv", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Text"]:
                texts.append(row["Text"])

    print("Total Reviews Loaded:", len(texts))

    # ensure we have at least one million entries for benchmarking
    if not texts:
        raise RuntimeError("no reviews loaded - cannot generate test data")

    if len(texts) < 1_000_000:
        multiplier = (1_000_000 // len(texts)) + 1
        texts = (texts * multiplier)[:1_000_000]

    # ---------------------------
    # Parallel Processing
    # ---------------------------
    start_parallel = time.time()

    with Pool(cpu_count()) as pool:
        results = list(pool.imap(process_text, texts, chunksize=1000))

    end_parallel = time.time()
    print("Parallel Processing Time:", round(end_parallel - start_parallel, 2), "seconds")

    # ---------------------------
    # Batch Insert
    # ---------------------------
    insert_results(results)
    print("Data Stored Successfully")

    # ---------------------------
    # Benchmark BEFORE Index
    # ---------------------------
    before = benchmark_queries()
    print("Query Time Before Index:", before, "seconds")

    # ---------------------------
    # Apply Index Optimization
    # ---------------------------
    apply_indexes()

    # ---------------------------
    # Benchmark AFTER Index
    # ---------------------------
    after = benchmark_queries()
    print("Query Time After Index:", after, "seconds")

    improvement = ((before - after) / before) * 100 if before > 0 else 0

    print("\nPerformance Improvement:", round(improvement, 2), "%")