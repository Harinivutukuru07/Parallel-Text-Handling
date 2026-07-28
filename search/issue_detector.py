# issue_detector.py
from .regex_search import search_patterns

def detect_issues(text):
    return search_patterns(text)

def detect_patterns(text):
    # This acts as an alias or standard API endpoint
    patterns = search_patterns(text)
    return ",".join(patterns)
