# parallel.py
import time
from multiprocessing import Pool
from module.config import WORKER_PROCESSES
from .processor import process_text

def process_batch(batch):
    return [process_text(text) for text in batch]

def run_parallel(texts, batch_size=5000):
    start = time.time()
    
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]

    with Pool(WORKER_PROCESSES) as pool:
        batch_results = pool.map(process_batch, batches)
    
    # Flatten results
    final_results = [item for batch in batch_results for item in batch]
    
    end = time.time()
    print("Parallel Time:", round(end - start, 4), "seconds")
    return final_results
