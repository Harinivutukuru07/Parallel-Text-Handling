# classifier.py
from .rules import calculate_score
from .sentiment import assign_sentiment

def classify_text(text):
    score = calculate_score(text)
    sentiment = assign_sentiment(score)
    return score, sentiment
