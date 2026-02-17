import os
import re
import time
from multiprocessing import Pool, cpu_count

# ---------------------------
# Rule-based scoring dictionary
# ---------------------------
SCORES = {
    "good": 1,
    "great": 2,
    "excellent": 3,
    "happy": 1,
    "bad": -1,
    "poor": -2,
    "sad": -1,
    "terrible": -3
}


# ---------------------------
# Worker Function
# ---------------------------
def process_file(filepath):
    filename = os.path.basename(filepath)

    print(f"Processing task: {filename}")
    

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().lower()

    words = re.findall(r"\b\w+\b", text)

    score = 0
    for word in words:
        score += SCORES.get(word, 0)

    print(f"Task executed: {filename}")
    return (os.path.basename(filepath), score)


# ---------------------------
# Sequential Processing
# ---------------------------
def run_sequential(files):
    print("\nRunning in SINGLE process mode...\n")
    start = time.time()

    results = []
    for f in files:
        results.append(process_file(f))

    end = time.time()
    print("\nSingle Process Time:", round(end - start, 4), "seconds")
    return results


# ---------------------------
# Parallel Processing
# ---------------------------
def run_parallel(files):
    print("\nRunning in MULTI process mode...\n")
    start = time.time()

    with Pool(cpu_count()) as pool:
        results = pool.map(process_file, files)

    end = time.time()
    print("\nMulti Process Time:", round(end - start, 4), "seconds")
    return results


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":

    folder_path = input("Enter folder path containing text files: ")

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ]

    if not files:
        print("No text files found.")
    else:
        print(f"\nFound {len(files)} files.\n")

        # Sequential
        seq_results = run_sequential(files)

        print("\n" + "-"*50)

        # Parallel
        par_results = run_parallel(files)

        print("\nResults:\n")
        for filename, score in par_results:
            print(f"{filename} -> Score: {score}")