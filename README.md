🚀 Parallel Text Handling Processor
====================================


📌 Overview
-------------

Parallel Text Handling Processor is a scalable text analytics system built in Python for high-volume review processing.
It performs rule-based and pattern-driven sentiment analysis, stores results in SQLite, and benchmarks database performance before and after optimization.
The system is designed to efficiently handle large datasets (up to 1 million records) using parallel processing techniques.

✨ Key Features
------------------

⚡ Parallel text processing using Python multiprocessing

🧠 Rule-based sentiment scoring (Positive / Negative / Neutral)

🔎 Pattern-based issue detection using regular expressions

🗄️ SQLite database storage

📦 Batch insertion for optimized database writes

📊 Performance benchmarking (before & after indexing)

📈 Index-based query optimization

🏗️ Project Architecture
------------------------

Parallel-Text-Processor/

│

├── rules.py  # Sentiment rules & pattern detection logic

├── processor.py    # Processes individual reviews

├── database.py     # Database setup and indexing

├── benchmark.py    # Query performance measurement

├── main.py         # Entry point (execution controller)

How to Run
----------

Install Python 3.10+

Place Reviews.csv in the project root

Run:

    python main.py

Requirements
------------

Python 3.10+

SQLite (built-in)



Python 3.10+
SQLite (built-in)
