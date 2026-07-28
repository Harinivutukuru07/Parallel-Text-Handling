# regex_search.py
from module.constants import PATTERN_RULES

def search_patterns(text):
    text_lower = text.lower()
    patterns = []
    for label, pattern in PATTERN_RULES.items():
        if pattern.search(text_lower):
            patterns.append(label)
    return patterns
