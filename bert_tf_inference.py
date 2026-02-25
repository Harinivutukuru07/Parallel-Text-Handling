"""Run inference with a fine-tuned TensorFlow BERT sentiment model.

Examples:
python bert_tf_inference.py --model_dir ./bert_sentiment --text "This product is great!"
python bert_tf_inference.py --model_dir ./bert_sentiment --texts_dir texts
"""
import argparse
import os
import numpy as np
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import tensorflow as tf


def predict_texts(model, tokenizer, texts, max_len=128, batch_size=32):
    enc = tokenizer(list(texts), padding=True, truncation=True, max_length=max_len, return_tensors="tf")
    inputs = {
        'input_ids': enc['input_ids'],
        'attention_mask': enc['attention_mask']
    }
    logits = model(inputs, training=False).logits
    probs = tf.nn.softmax(logits, axis=-1).numpy()
    preds = np.argmax(probs, axis=1)
    return preds, probs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default="./bert_sentiment")
    parser.add_argument("--text", default=None)
    parser.add_argument("--texts_dir", default=None)
    parser.add_argument("--max_len", type=int, default=128)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    model = TFAutoModelForSequenceClassification.from_pretrained(args.model_dir)

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

    preds, probs = predict_texts(model, tokenizer, inputs, max_len=args.max_len)
    for t, p, prob in zip(inputs, preds, probs):
        label = 'positive' if p == 1 else 'negative'
        print(f"Prediction: {label} (probabilities: {prob.tolist()})\nText: {t[:200]}\n---")


if __name__ == '__main__':
    main()
