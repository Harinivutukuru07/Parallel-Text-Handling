# helpers.py
import time
from contextlib import contextmanager

@contextmanager
def time_it(description="Operation"):
    start = time.time()
    yield
    end = time.time()
    print(f"{description} Time: {round(end - start, 4)} seconds")
