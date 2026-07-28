# System Architecture

The **Parallel Text Handling Processor** is built on a highly modular architecture designed to support scalable ingestion, efficient sentiment analysis processing, and structured data storage.

## Core Modules

- **Loader (`loader/`)**
  - Responsible for reading inputs from diverse data sources, specifically focusing on large `.txt`, `.csv`, and `.xlsx` files.

- **Processor (`processor/`)**
  - **Tokenizer & Normalizer**: Normalizes incoming text (lowercasing) and safely splits text into words using compiled regex patterns for speed.
  - **Parallel Execution (`parallel.py`)**: Uses Python's `multiprocessing.Pool` to divide huge datasets (e.g., millions of rows) into chunks (batches of 5,000) and distribute them across available CPU cores for concurrent processing, vastly reducing execution time.

- **Scorer (`scorer/`)**
  - Houses the sentiment lexicons (positive, negative, negations, intensifiers, diminishers).
  - Calculates sentiment scores dynamically by traversing the text and factoring in localized contexts like contrast words ("but", "however").

- **Search / Pattern Detection (`search/`)**
  - Detects prevalent issues using fast, pre-compiled regular expressions.
  - Automatically tags reviews containing keywords related to phishing, scams, delivery issues, product damage, or customer service complaints.

- **Storage (`storage/`)**
  - Built on SQLite for robust, lightweight structured data storage.
  - Utilizes batch inserts (`executemany`) to prevent I/O bottlenecks.
  - Employs Indexing (`CREATE INDEX`) to accelerate complex query execution times post-processing.

- **Interface (`app.py` & `Interface.py`)**
  - A responsive Streamlit dashboard offering file uploading, a progress tracker, dynamic result visualisations (Pie/Bar charts), data preview, and CSV downloading.
