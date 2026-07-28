# sequential.py
import time
from .processor import process_text

def run_sequential(texts):
    start = time.time()
    results = [process_text(text) for text in texts]
    end = time.time()
    print("Sequential Time:", round(end - start, 4), "seconds")
    return results
