# main.py

import csv
import time
from multiprocessing import Pool, cpu_count

from processor import process_text
from database import setup_database, insert_results, apply_indexes
from benchmark import benchmark_queries


if __name__ == "__main__":

    setup_database()

    texts = []
    with open("Reviews.csv", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Text"]:
                texts.append(row["Text"])

    print("Total Reviews Loaded:", len(texts))

    if len(texts) < 1_000_000:
        multiplier = (1_000_000 // len(texts)) + 1
        texts = (texts * multiplier)[:1_000_000]

    start = time.time()

    with Pool(cpu_count()) as pool:
        results = list(pool.imap(process_text, texts, chunksize=1000))

    end = time.time()
    print("Parallel Processing Time:", round(end - start, 2), "seconds")

    insert_results(results)
    print("Data Stored Successfully")

    before = benchmark_queries()
    print("Query Time Before Index:", before)

    apply_indexes()

    after = benchmark_queries()
    print("Query Time After Index:", after)

    improvement = ((before - after) / before) * 100 if before > 0 else 0
    print("Performance Improvement:", round(improvement, 2), "%")