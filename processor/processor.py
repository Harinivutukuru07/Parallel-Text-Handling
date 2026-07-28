# processor.py
from datetime import datetime
from scorer.classifier import classify_text
from search.issue_detector import detect_patterns

def process_text(text):
    score, sentiment = classify_text(text)
    patterns = detect_patterns(text)
    return (text, score, sentiment, patterns, datetime.now().isoformat())