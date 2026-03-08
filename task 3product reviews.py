# =========================================================
# MODULE 1: IMPORTS
# =========================================================
import csv
import re
import time
import sqlite3
from datetime import datetime
from multiprocessing import Pool, cpu_count




# =========================================================
# MODULE 2: POSITIVE & NEGATIVE WORD LISTS & PRECOMPILED PATTERNS
# =========================================================
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing",
    "love", "awesome", "nice", "perfect",
    "happy", "satisfied"
}

NEGATIVE_WORDS = {    "bad", "poor", "terrible", "worst",
    "hate", "awful", "disappointing",
    "sad", "horrible"
}

NEGATIONS = {"not", "no", "never", "none", "n't"}

INTENSIFIERS = {"very", "extremely", "really", "too", "so"}

DIMINISHERS = {"slightly", "little", "somewhat", "barely"}

CONTRAST_WORDS = {"but", "however", "though", "although"}

# Precompiled regex patterns for optimal performance
TOKEN_PATTERN = re.compile(r"\b\w+\b")

# Precompiled pattern rules for detect_patterns function
PATTERN_RULES = {
    "refund_request": re.compile(r"\brefund|money back|return item\b"),
    "delivery_issue": re.compile(r"\b(delayed|late delivery|not delivered|shipping issue)\b"),
    "product_damage": re.compile(r"\b(broken|damaged|defective|cracked|faulty)\b"),
    "performance_issue": re.compile(r"\b(stopped working|doesn't work|not working|malfunction)\b"),
    "customer_service_issue": re.compile(r"\b(customer service|support team|no response|rude service)\b"),
    "price_complaint": re.compile(r"\b(expensive|overpriced|not worth|waste of money)\b"),
    "positive_recommendation": re.compile(r"\b(highly recommend|worth buying|must buy|best purchase)\b"),
    "sarcasm_indicator": re.compile(r"\b(yeah right|as if|thanks for nothing)\b")
}


# =========================================================
# MODULE 3: SENTIMENT CALCULATION FUNCTIONS
# =========================================================
def calculate_score(text):
    words = TOKEN_PATTERN.findall(text.lower())
    score = 0
    weight = 1
    negate = False

    for i, word in enumerate(words):

        # Detect negation
        if word in NEGATIONS:
            negate = True
            continue

        # Detect intensifiers
        if word in INTENSIFIERS:
            weight = 2
            continue

        # Detect diminishers
        if word in DIMINISHERS:
            weight = 0.5
            continue

        # Positive word
        if word in POSITIVE_WORDS:
            val = weight
            if negate:
                val = -val
            score += val
            weight = 1
            negate = False

        # Negative word
        elif word in NEGATIVE_WORDS:
            val = -weight
            if negate:
                val = -val
            score += val
            weight = 1
            negate = False

        else:
            weight = 1
            negate = False

    # Contrast handling (focus on part after "but")
    for contrast in CONTRAST_WORDS:
        if contrast in text.lower():
            parts = text.lower().split(contrast)
            if len(parts) > 1:
                score = calculate_score(parts[-1])
            break

    return score 
def assign_sentiment(score):
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"
# =========================================================
# MODULE 3B: PATTERN DETECTION
# =========================================================
def detect_patterns(text):
    text_lower = text.lower()
    patterns = []

    for label, pattern in PATTERN_RULES.items():
        if pattern.search(text_lower):
            patterns.append(label)

    return patterns


# =========================================================
# MODULE 4: DATABASE CREATION
# =========================================================
def create_database():
    conn = sqlite3.connect("sentiment.db")
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    score REAL,
    sentiment TEXT,
    patterns TEXT,
    timestamp TEXT
)
""")

    conn.commit()
    conn.close()


# =========================================================
# MODULE 5: INSERT RESULTS (NORMAL INSERT LOOP)
# =========================================================
def insert_results(results):
    conn = sqlite3.connect("sentiment.db")
    cursor = conn.cursor()

    for text, score, sentiment, patterns in results:
        cursor.execute("""
INSERT INTO reviews (text, score, sentiment, patterns, timestamp)
VALUES (?, ?, ?, ?, ?)
""", (text, score, sentiment, patterns,
      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()
# =========================================================
# MODULE 9: DISPLAY STORED RESULTS
# =========================================================
def display_results(limit=10):
    conn = sqlite3.connect("sentiment.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, score, sentiment, timestamp FROM reviews LIMIT ?", (limit,))
    rows = cursor.fetchall()

    print("\nSample Stored Records:")
    for row in rows:
        print(row)

    conn.close()


# =========================================================
# MODULE 7: WORKER FUNCTION (PROCESS CHUNK)
# =========================================================
def process_text(text):
    score = calculate_score(text)
    sentiment = assign_sentiment(score)
    patterns = detect_patterns(text)
    return (text, score, sentiment, ",".join(patterns))


# =========================================================
# MODULE 7B: BATCH PROCESSING FUNCTION
# =========================================================
def process_batch(batch):
    return [process_text(text) for text in batch]
# =========================================================
# MODULE 8: MAIN EXECUTION
# =========================================================
# =========================================================
# MODULE 8: MAIN EXECUTION
# =========================================================
if __name__ == "__main__":

    file_path = "Reviews.csv"

    texts = []

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            text = row["Text"]
            if text:
                texts.append(text)

    print("Total reviews loaded:", len(texts))

    create_database()

    # ---------------------------
    # Sequential Processing
    # ---------------------------
    start_seq = time.time()

    seq_results = []
    for text in texts:
        score = calculate_score(text)
        sentiment = assign_sentiment(score)
        seq_results.append((text, score, sentiment))

    end_seq = time.time()
    print("Sequential Time:", round(end_seq - start_seq, 4), "seconds")

    # ---------------------------
    # Parallel Processing with Batch Handling
    # ---------------------------
    num_processes = cpu_count()
    print("Using", num_processes, "CPU cores")

    start_time = time.time()

    batch_size = 5000
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]

    with Pool(num_processes) as pool:
        batch_results = pool.map(process_batch, batches)
    
    # Flatten the results from batches
    final_results = [item for batch in batch_results for item in batch]

    end_time = time.time()
    print("Parallel Time:", round(end_time - start_time, 4), "seconds")

    insert_results(final_results)

    print("All results stored successfully.")

    display_results(10)