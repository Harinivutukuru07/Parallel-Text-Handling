"""Fine-tune BERT (TensorFlow) for binary sentiment on Reviews.csv.

Usage examples:
python bert_tf_finetune.py --csv Reviews.csv --text_col "Text" --label_col "Score" --output_dir ./bert_sentiment --epochs 2 --batch_size 16
"""
import argparse
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification


def detect_columns(df):
    text_candidates = [c for c in df.columns if c.lower() in ("text", "review", "reviewtext", "review_text")]
    label_candidates = [c for c in df.columns if c.lower() in ("score", "rating", "label", "sentiment")]
    return (text_candidates[0] if text_candidates else df.columns[0],
            label_candidates[0] if label_candidates else df.columns[-1])


def prepare_labels(series):
    # try numeric mapping: >=4 -> 1, <=2 -> 0, drop 3
    try:
        s = pd.to_numeric(series, errors="coerce")
        mask = s.notna()
        s = s[mask]
        y = s.apply(lambda x: 1 if x >= 4 else (0 if x <= 2 else -1)).astype(int)
        return y, mask
    except Exception:
        # fallback: map common strings
        s = series.astype(str).str.lower()
        pos = s.isin(["positive", "pos", "p", "1"])  
        neg = s.isin(["negative", "neg", "n", "0"])  
        y = pd.Series(np.where(pos, 1, np.where(neg, 0, -1)), index=series.index)
        mask = y != -1
        return y, mask


def tokenize_texts(tokenizer, texts, max_len):
    return tokenizer(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors="tf")


def build_dataset(encodings, labels, batch_size, shuffle=True):
    dataset = tf.data.Dataset.from_tensor_slices(({
        'input_ids': encodings['input_ids'],
        'attention_mask': encodings['attention_mask']
    }, labels))
    if shuffle:
        dataset = dataset.shuffle(10000)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="Reviews.csv", help="CSV file with reviews")
    parser.add_argument("--text_col", default=None)
    parser.add_argument("--label_col", default=None)
    parser.add_argument("--model_name", default="bert-base-uncased")
    parser.add_argument("--output_dir", default="./bert_sentiment")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--max_len", type=int, default=128)
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

    # drop any remaining -1 labels
    keep = labels != -1
    texts = texts.loc[keep]
    labels = labels.loc[keep].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(texts, labels, test_size=0.1, random_state=42, stratify=labels)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    train_enc = tokenize_texts(tokenizer, X_train.tolist(), args.max_len)
    val_enc = tokenize_texts(tokenizer, X_val.tolist(), args.max_len)

    train_dataset = build_dataset(train_enc, y_train.values, args.batch_size, shuffle=True)
    val_dataset = build_dataset(val_enc, y_val.values, args.batch_size, shuffle=False)

    model = TFAutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)

    optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    model.fit(train_dataset, validation_data=val_dataset, epochs=args.epochs)

    os.makedirs(args.output_dir, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Saved model and tokenizer to", args.output_dir)


if __name__ == '__main__':
    main()
