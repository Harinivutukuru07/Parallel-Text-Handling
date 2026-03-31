"""
Contains rule-based sentiment scoring logic
and pattern detection utilities.
"""

import re

# ------------------------------------------
# Word Dictionaries
# ------------------------------------------

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing",
    "love", "awesome", "nice", "perfect",
    "happy", "satisfied", "helpful", "reliable",
    "fast", "smooth", "recommended"
}

NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "worst",
    "hate", "awful", "disappointing",
    "sad", "horrible", "spam", "scam",
    "fraud", "phishing", "misleading", "fake"
}

NEGATIONS = {"not", "no", "never", "none", "n't"}
INTENSIFIERS = {"very", "extremely", "really", "too", "so"}
DIMINISHERS = {"slightly", "little", "somewhat", "barely"}
CONTRAST_WORDS = {"but", "however", "though", "although"}

# Precompiled regex for tokenization
TOKEN_PATTERN = re.compile(r"\b\w+\b")

# Precompiled pattern rules for business issue detection
PATTERN_RULES = {
    "refund": re.compile(r"\b(refund|money back|return)\b"),
    "delivery_issue": re.compile(r"\b(delayed|late|not delivered)\b"),
    "product_damage": re.compile(r"\b(broken|damaged|defective)\b"),
    "customer_service": re.compile(r"\b(customer service|no response|rude)\b"),
    "price_complaint": re.compile(r"\b(expensive|overpriced|waste of money)\b"),
    "sarcasm": re.compile(r"\b(yeah right|as if|thanks for nothing)\b"),
    "spam": re.compile(r"\b(spam|unsolicited|junk|promotional message)\b"),
    "scam_risk": re.compile(r"\b(scam|fraud|fake offer|too good to be true)\b"),
    "phishing": re.compile(r"\b(phishing|click here|verify account|suspicious link)\b"),
    "account_security": re.compile(r"\b(hacked|account compromised|unauthorized login)\b"),
    "payment_issue": re.compile(r"\b(double charged|charged twice|payment failed|refund pending)\b"),
    "quality_issue": re.compile(r"\b(low quality|poor quality|stopped working|not as described)\b")
}


def calculate_score(text):
    """
    Calculates sentiment score using rule-based logic.

    Handles:
    - Positive and negative words
    - Negations (e.g., "not good")
    - Intensifiers (e.g., "very good")
    - Diminishers (e.g., "slightly bad")
    - Contrast words (e.g., "but")

    Returns:
        float: Computed sentiment score
    """
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

    # Apply contrast rule
    for contrast in CONTRAST_WORDS:
        if contrast in text.lower():
            parts = text.lower().split(contrast)
            if len(parts) > 1:
                return calculate_score(parts[-1])
            break

    return score


def assign_sentiment(score):
    """
    Converts numeric score into sentiment label.

    Args:
        score (float): Sentiment score

    Returns:
        str: 'Positive', 'Negative', or 'Neutral'
    """
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"


def detect_patterns(text):
    """
    Detects predefined issue patterns in review text.

    Args:
        text (str): Review text

    Returns:
        str: Comma-separated pattern labels found
    """
    text = text.lower()
    found = []

    for label, pattern in PATTERN_RULES.items():
        if pattern.search(text):
            found.append(label)

    return ",".join(found) if found else "none"
