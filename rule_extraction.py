# =========================================================
# RULE EXTRACTION SCRIPT
# =========================================================

import csv
import re
from collections import Counter

# ---------------------------
# Stopwords (basic filtering)
# ---------------------------
STOPWORDS = {
    "the", "and", "is", "this", "it", "to", "a",
    "of", "for", "in", "on", "with", "that",
    "was", "are", "as", "but", "be", "have",
    "had", "has", "very", "my", "so", "at",
    "they", "you", "i"
}

WORD_PATTERN = re.compile(r"\b\w+\b")

# ---------------------------
# Read Dataset
# ---------------------------
positive_texts = []
negative_texts = []

print("Reading dataset...")

with open("Reviews.csv", newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        text = row["Text"]
        rating = int(row["Score"])

        if not text:
            continue

        if rating >= 4:
            positive_texts.append(text)
        elif rating <= 2:
            negative_texts.append(text)

print("Positive Reviews:", len(positive_texts))
print("Negative Reviews:", len(negative_texts))


# ---------------------------
# Function to Count Words
# ---------------------------
def get_word_counts(texts):
    counter = Counter()

    for text in texts:
        words = WORD_PATTERN.findall(text.lower())

        filtered_words = [
            w for w in words
            if w not in STOPWORDS and len(w) > 2
        ]

        counter.update(filtered_words)

    return counter


# ---------------------------
# Get Word Frequencies
# ---------------------------
print("Extracting word frequencies...")

pos_counter = get_word_counts(positive_texts)
neg_counter = get_word_counts(negative_texts)


# ---------------------------
# Identify Strong Rules (Improved Logic)
# ---------------------------
# ---------------------------
# Identify Strong Sentiment Rules (Better Logic)
# ---------------------------
strong_positive = []
strong_negative = []

MIN_TOTAL = 100  # ignore rare words

all_words = set(pos_counter.keys()).union(set(neg_counter.keys()))

for word in all_words:
    pos_count = pos_counter[word]
    neg_count = neg_counter[word]
    total = pos_count + neg_count

    if total < MIN_TOTAL:
        continue

    difference = pos_count - neg_count

    # Strong Positive
    if difference > 200:
        strong_positive.append((word, difference))

    # Strong Negative
    elif difference < -200:
        strong_negative.append((word, abs(difference)))

# Sort by strength
strong_positive.sort(key=lambda x: x[1], reverse=True)
strong_negative.sort(key=lambda x: x[1], reverse=True)

# Keep only words
strong_positive = [word for word, _ in strong_positive]
strong_negative = [word for word, _ in strong_negative]
print("Strong Positive Words Found:", len(strong_positive))
print("Strong Negative Words Found:", len(strong_negative))
# ---------------------------
# Save Rules to Files
# ---------------------------
with open("positive_rules.txt", "w") as f:
    for word in strong_positive:
        f.write(word + "\n")

with open("negative_rules.txt", "w") as f:
    for word in strong_negative:
        f.write(word + "\n")

print("Rules saved successfully!")
print("Files created: positive_rules.txt & negative_rules.txt")