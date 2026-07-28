# benchmark.py
import time
from loader.csv_loader import load_csv
from processor.parallel import run_parallel
from storage.database import setup_database, apply_indexes
from storage.queries import insert_results
from storage.benchmark import benchmark_queries

def run_benchmark():
    setup_database()

    print("Loading CSV...")
    texts = load_csv("data/Reviews.csv")
    print(f"Total Reviews Loaded: {len(texts)}")
    
    if not texts:
        print("No texts found to benchmark.")
        return

    # Expand texts to a larger dataset for benchmarking
    if len(texts) < 1_000_000:
        multiplier = (1_000_000 // len(texts)) + 1
        texts = (texts * multiplier)[:1_000_000]
        
    print(f"Expanded to {len(texts)} texts for benchmarking.")

    # Parallel processing
    print("Running parallel processing...")
    results = run_parallel(texts, batch_size=5000)
    print("Parallel processing complete.")

    # Insert results
    print("Inserting results...")
    insert_results(results)
    print("Results inserted.")

    # Benchmark before index
    print("Benchmarking queries before indexing...")
    time_before = benchmark_queries()
    print(f"Query Time Before Index: {time_before} seconds")

    # Apply index
    print("Applying indexes...")
    apply_indexes()
    
    # Benchmark after index
    print("Benchmarking queries after indexing...")
    time_after = benchmark_queries()
    print(f"Query Time After Index: {time_after} seconds")
    
    if time_before > 0:
        improvement = ((time_before - time_after) / time_before) * 100
        print(f"Performance Improvement: {round(improvement, 2)}%")

if __name__ == "__main__":
    run_benchmark()