"""Fine-tune BERT (PyTorch) for binary sentiment on Reviews.csv.

Lightweight training loop for a quick smoke-run (CPU-friendly).

Usage:
python bert_pt_finetune.py --csv Reviews.csv --epochs 1 --batch_size 16 --limit 500
"""
import argparse
import os
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class TextDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(int(self.labels[idx]))
        return item


def detect_columns(df):
    text_candidates = [c for c in df.columns if c.lower() in ("text", "review", "reviewtext", "review_text")]
    label_candidates = [c for c in df.columns if c.lower() in ("score", "rating", "label", "sentiment")]
    return (text_candidates[0] if text_candidates else df.columns[0],
            label_candidates[0] if label_candidates else df.columns[-1])


def prepare_labels(series):
    try:
        s = pd.to_numeric(series, errors="coerce")
        mask = s.notna()
        s = s[mask]
        y = s.apply(lambda x: 1 if x >= 4 else (0 if x <= 2 else -1)).astype(int)
        return y, mask
    except Exception:
        s = series.astype(str).str.lower()
        pos = s.isin(["positive", "pos", "p", "1"])  
        neg = s.isin(["negative", "neg", "n", "0"])  
        y = pd.Series(np.where(pos, 1, np.where(neg, 0, -1)), index=series.index)
        mask = y != -1
        return y, mask


def collate_fn(batch):
    return {k: torch.stack([b[k] for b in batch]) for k in batch[0]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="Reviews.csv")
    parser.add_argument("--text_col", default=None)
    parser.add_argument("--label_col", default=None)
    parser.add_argument("--model_name", default="bert-base-uncased")
    parser.add_argument("--output_dir", default="./bert_sentiment_pt")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--max_len", type=int, default=128)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    text_col, label_col = (args.text_col, args.label_col)
    if not text_col or not label_col:
        detected_text, detected_label = detect_columns(df)
        text_col = text_col or detected_text
        label_col = label_col or detected_label

    labels, mask = prepare_labels(df[label_col])
    df = df.loc[mask]
    labels = labels.loc[mask]
    texts = df[text_col].astype(str)

    keep = labels != -1
    texts = texts.loc[keep]
    labels = labels.loc[keep].astype(int)

    # limit for quick smoke-run
    if args.limit and len(texts) > args.limit:
        sel = random.sample(list(texts.index), args.limit)
        texts = texts.loc[sel]
        labels = labels.loc[sel]

    X_train, X_val, y_train, y_val = train_test_split(texts, labels, test_size=0.1, random_state=42, stratify=labels)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    train_enc = tokenizer(list(X_train), padding=True, truncation=True, max_length=args.max_len, return_tensors='pt')
    val_enc = tokenizer(list(X_val), padding=True, truncation=True, max_length=args.max_len, return_tensors='pt')

    train_dataset = TextDataset({k: v.numpy() for k, v in train_enc.items()}, y_train.values)
    val_dataset = TextDataset({k: v.numpy() for k, v in val_enc.items()}, y_val.values)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2).to(device)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
    loss_fn = torch.nn.CrossEntropyLoss()

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels_batch = batch['labels'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            loss = loss_fn(logits, labels_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{args.epochs} - train loss: {total_loss/len(train_loader):.4f}")

    # quick eval
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels_batch = batch['labels'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = outputs.logits.argmax(dim=1)
            correct += (preds == labels_batch).sum().item()
            total += labels_batch.size(0)
    print(f"Validation accuracy: {correct}/{total} = {correct/total:.4f}")

    os.makedirs(args.output_dir, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Saved PyTorch model to", args.output_dir)


if __name__ == '__main__':
    main()
