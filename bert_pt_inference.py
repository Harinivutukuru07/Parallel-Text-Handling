"""Run inference with a fine-tuned PyTorch BERT sentiment model.

Usage:
python bert_pt_inference.py --model_dir ./bert_sentiment_pt --text "This product is great!"
"""
import argparse
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def predict_texts(model, tokenizer, texts, max_len=128, device=None):
    enc = tokenizer(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors='pt')
    input_ids = enc['input_ids'].to(device)
    attention_mask = enc['attention_mask'].to(device)
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()
        preds = probs.argmax(axis=1)
    return preds, probs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default="./bert_sentiment_pt")
    parser.add_argument("--text", default=None)
    parser.add_argument("--texts_dir", default=None)
    parser.add_argument("--max_len", type=int, default=128)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = AutoModelForSequenceClassification.from_pretrained(args.model_dir).to(device)

    inputs = []
    if args.text:
        inputs.append(args.text)
    if args.texts_dir:
        for fname in os.listdir(args.texts_dir):
            path = os.path.join(args.texts_dir, fname)
            if os.path.isfile(path):
                with open(path, encoding='utf-8', errors='ignore') as f:
                    inputs.append(f.read())

    if not inputs:
        print("No input texts provided. Use --text or --texts_dir")
        return

    preds, probs = predict_texts(model, tokenizer, inputs, max_len=args.max_len, device=device)
    for t, p, prob in zip(inputs, preds, probs):
        label = 'positive' if p == 1 else 'negative'
        print(f"Prediction: {label} (probabilities: {prob.tolist()})\nText: {t[:200]}\n---")


if __name__ == '__main__':
    main()
