# tokenizer.py
from module.constants import TOKEN_PATTERN
from .normalizer import normalize_text

def tokenize(text):
    normalized = normalize_text(text)
    return TOKEN_PATTERN.findall(normalized)
