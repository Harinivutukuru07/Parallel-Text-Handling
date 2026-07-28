# rules.py
from module.constants import TOKEN_PATTERN, NEGATIONS, INTENSIFIERS, DIMINISHERS, POSITIVE_WORDS, NEGATIVE_WORDS, CONTRAST_WORDS

def calculate_score(text):
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
        else:
            weight = 1
            negate = False

    for contrast in CONTRAST_WORDS:
        if contrast in text.lower():
            parts = text.lower().split(contrast)
            if len(parts) > 1:
                return calculate_score(parts[-1])
            break

    return score