# Parallel Text Handling Processor

## BERT (TensorFlow) Sentiment Fine-Tuning

This workspace also includes TensorFlow-based scripts to fine-tune and run inference with BERT for binary sentiment analysis.

Files:

- `requirements.txt` for Python dependencies
- `bert_tf_finetune.py` to fine-tune BERT on `Reviews.csv`
- `bert_tf_inference.py` to run predictions on a text or a folder of text files

Quick start:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python bert_tf_finetune.py --csv Reviews.csv --text_col Text --label_col Score --output_dir ./bert_sentiment --epochs 2 --batch_size 16
python bert_tf_inference.py --model_dir ./bert_sentiment --text "This product is great!"
```

## Overview

Parallel Text Handling Processor is a Python project for processing and analyzing large volumes of text and review data.
It combines multiprocessing-based file processing, rule-based sentiment scoring, regex-based pattern detection, and SQLite-backed storage.

## Features

1. Parallel text processing using Python multiprocessing
2. Rule-based sentiment scoring (Positive / Negative / Neutral)
3. Pattern-based issue detection with regular expressions
4. SQLite database storage and batch insertion
5. Query/index benchmarking for performance comparison
6. Sequential vs parallel runtime comparison on sample text files

## Project Structure

```text
Parallel-Text-Processor/
|-- benchmark.py
|-- database.py
|-- processor.py
|-- rules.py
|-- main.py
|-- main1.py
|-- Interface.py
|-- texts/
|   |-- large1.txt
|   |-- mixed1.txt
|   |-- negative1.txt
|   |-- neutral1.txt
|   `-- positive1.txt
`-- Reviews.csv
```

## How It Works

1. Reads text and review data from files and CSV inputs.
2. Extracts and normalizes tokens using regex and rule dictionaries.
3. Computes sentiment and pattern matches.
4. Stores and queries processed data in SQLite.
5. Compares sequential and multiprocessing execution times.

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the main pipeline:

```bash
python main.py
```

3. (Optional) Run Streamlit interface:

```bash
streamlit run Interface.py
```

## Requirements

1. Python 3.10+
2. SQLite (built-in)
