# text_loader.py
import os

def load_text_files(folder_path):
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ]
    texts = []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            texts.append(f.read())
    return texts
