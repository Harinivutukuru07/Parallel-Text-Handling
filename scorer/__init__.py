# __init__.py
from .rules import calculate_score
from .sentiment import assign_sentiment
from .classifier import classify_text

__all__ = ["calculate_score", "assign_sentiment", "classify_text"]
