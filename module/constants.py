# constants.py
import re

DB_NAME = "database/reviews.db"

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
