# csv_loader.py
import csv

def load_csv(file_path, text_column="Text"):
    texts = []
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = row.get(text_column)
            if text:
                texts.append(text)
    return texts
