# Workflow

## 1. Data Ingestion
1. The user uploads a file (`.csv`, `.txt`, `.xlsx`) via the Streamlit web UI.
2. The `loader` module streams the file into memory and extracts the review texts into a list, stripping out empty sequences and handling parsing logic.

## 2. Text Processing Pipeline
1. The user triggers the processing phase.
2. The data is partitioned into batches to prevent memory bloat and optimize inter-process communication.
3. The `processor.parallel` module spins up a `multiprocessing.Pool` equal to `(System Cores - 1)`.
4. Inside each worker:
   - **Normalization**: The text is lowercased.
   - **Tokenization**: The text is split into distinct alphanumeric tokens.
   - **Scoring**: Sentiments are weighed heavily against the `scorer` lexicon (handling negations and intensifiers).
   - **Pattern Matching**: The `search` module tags any detected issues using Regex.

## 3. Data Storage
1. Processed tuples `(text, score, sentiment, patterns, timestamp)` are aggregated.
2. The `storage.queries` module connects to the SQLite database `reviews.db`.
3. An `executemany` batch transaction securely inserts all rows into the database.
4. Database indexes are validated to ensure future analytical queries run instantly.

## 4. UI Rendering & Analytics
1. The dashboard converts the processed results back into a `pandas.DataFrame`.
2. Interactive visualizations are generated utilizing `matplotlib`.
3. The DataFrame is exposed for previewing.
4. Finally, complete or sample outputs are available for the user to download as `.csv`.
