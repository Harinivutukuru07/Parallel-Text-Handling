# config.py
import multiprocessing

WORKER_PROCESSES = max(1, multiprocessing.cpu_count() - 1)
BATCH_SIZE = 5000
