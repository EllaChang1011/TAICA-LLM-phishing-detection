#!/usr/bin/env python3
"""
Zero-shot baseline using Qwen3-14B via Ollama (no LoRA adapter).

Outputs:
  baseline_results.json  — overall + per-category metrics
  baseline_results.csv   — per-email predictions
"""

import csv
import json
import re
import sys
from pathlib import Path

import requests
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"
TEST_PATH    = "data/test/data.json"

INFERENCE_PROMPT = """/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{}

### Classification:
"""

CATEGORIES = [
    ("human", "phishing"),
    ("human", "legitimate"),
    ("llm",   "phishing"),
    ("llm",   "legitimate"),
]


def query_ollama(prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0, "num_predict": 16}},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def extract_label(text: str) -> str:
    text = text.strip().lower()
    first = text.split()[0] if text.split() else ""
    if first in ("phishing", "legitimate"):
        return first
    if re.search(r"\bphishing\b", text):
        return "phishing"
    if re.search(r"\blegitimate\b", text):
        return "legitimate"
    return "phishing"


def run_inference(records: list) -> list[dict]:
    results = []
    for i, rec in enumerate(records):
        try:
            raw = query_ollama(INFERENCE_PROMPT.format(rec["input"]))
            predicted = extract_label(raw)
        except Exception as e:
            print(f"  [{i+1}] ERROR: {e}")
            continue

        results.append({
            "email_id":        i,
            "source":          rec["source"],
            "true_label":      rec["label"],
            "predicted_label": predicted,
            "correct":         predicted == rec["label"],
            "raw_output":      raw.strip(),
            "text":            rec["input"],
        })

        if (i + 1) % 20 == 0:
            acc = sum(r["correct"] for r in results) / len(results)
            print(f"  [{i+1:3d}/{len(records)}] running accuracy: {acc:.3f}")

    return results


def compute_metrics(results: list[dict]) -> dict:
    y_true = [1 if r["true_label"] == "phishing" else 0 for r in results]
    y_pred = [1 if r["predicted_label"] == "phishing" else 0 for r in results]

    overall = {
        "accuracy":  accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
    }

    per_category = {}
    for source, label in CATEGORIES:
        subset = [r for r in results if r["source"] == source and r["true_label"] == label]
        if not subset:
            continue
        st = [1 if r["true_label"] == "phishing" else 0 for r in subset]
        sp = [1 if r["predicted_label"] == "phishing" else 0 for r in subset]
        key = f"{source}_{label}"
        per_category[key] = {
            "count":   len(subset),
            "correct": sum(r["correct"] for r in subset),
            "accuracy":  accuracy_score(st, sp),
            "precision": precision_score(st, sp, zero_division=0),
            "recall":    recall_score(st, sp, zero_division=0),
            "f1":        f1_score(st, sp, zero_division=0),
        }

    return {"overall": overall, "per_category": per_category,
            "y_true": y_true, "y_pred": y_pred}


def print_summary(metrics: dict):
    o = metrics["overall"]
    print("\n" + "=" * 60)
    print("BASELINE RESULTS (Qwen3-14B, no LoRA)")
    print("=" * 60)
    print(f"  Accuracy:  {o['accuracy']:.4f}")
    print(f"  Precision: {o['precision']:.4f}")
    print(f"  Recall:    {o['recall']:.4f}")
    print(f"  F1:        {o['f1']:.4f}")
    print(f"\n{'Category':<22} {'Acc':>7} {'F1':>7} {'Err/N':>8}")
    print("-" * 48)
    for source, label in CATEGORIES:
        key = f"{source}_{label}"
        m = metrics["per_category"].get(key, {})
        errs = m.get("count", 0) - m.get("correct", 0)
        print(f"  {source}-{label:<18} {m.get('accuracy',0):>7.1%} "
              f"{m.get('f1',0):>7.3f} {errs:>4}/{m.get('count',0)}")
    print("=" * 60)


def main():
    try:
        requests.get("http://localhost:11434", timeout=5).raise_for_status()
    except Exception:
        sys.exit("ERROR: Ollama is not running. Start it first.")

    print(f"Model : {OLLAMA_MODEL} (Ollama, zero-shot)")

    with open(TEST_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"Test set: {len(records)} emails\n")

    print("Running inference...")
    results = run_inference(records)

    metrics = compute_metrics(results)
    print_summary(metrics)

    out_dir = Path("eval_results")
    out_dir.mkdir(exist_ok=True)

    output = {
        "model":        OLLAMA_MODEL,
        "lora":         False,
        "num_test":     len(results),
        "overall":      metrics["overall"],
        "per_category": metrics["per_category"],
    }
    with open(out_dir / "baseline_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("\nSaved → eval_results/baseline_results.json")

    fields = ["email_id", "source", "true_label", "predicted_label", "correct", "text"]
    with open(out_dir / "baseline_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print("Saved → eval_results/baseline_results.csv")


if __name__ == "__main__":
    main()
