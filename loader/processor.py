from datetime import datetime
from scorer.rules import calculate_score, assign_sentiment, detect_patterns


def process_text(text):
    score = calculate_score(text)
    sentiment = assign_sentiment(score)
    patterns = detect_patterns(text)
    return (text, score, sentiment, patterns, datetime.now().isoformat())
