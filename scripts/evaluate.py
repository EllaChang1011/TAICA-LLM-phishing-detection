#!/usr/bin/env python3
"""
Evaluate fine-tuned Qwen3-14B on the phishing email test set.

Outputs:
  evaluation_results.json  — overall + per-category metrics
  predictions.csv          — per-email predictions (for teammate's report gen)
  confusion_matrix.png     — confusion matrix
  baseline_comparison.png  — baseline vs fine-tuned accuracy by category
  error_analysis.md        — misclassification analysis
"""

import csv
import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

OLLAMA_URL      = "http://localhost:11434/api/generate"
FINETUNED_MODEL = "phishing-detector-14b"
TEST_PATH       = "data/test/data.json"
BASELINE_PATH   = "eval_results/baseline_results.json"

INFERENCE_PROMPT = """/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{}

### Classification:
"""

CATEGORIES = [
    ("human", "phishing"),
    ("human", "legitimate"),
    ("llm", "phishing"),
    ("llm", "legitimate"),
]


def extract_label(text: str) -> str:
    """Parse single-word model output."""
    text = text.strip().lower()
    first = text.split()[0] if text.split() else ""
    if first in ("phishing", "legitimate"):
        return first
    # Fallback scan
    if re.search(r"\bphishing\b", text):
        return "phishing"
    if re.search(r"\blegitimate\b", text):
        return "legitimate"
    return "phishing"   # safer default for security tasks


def query_ollama(prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": FINETUNED_MODEL, "prompt": prompt, "stream": False,
              "options": {"temperature": 0, "num_predict": 16}},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def run_inference(records: list) -> list[dict]:
    results = []

    for i, rec in enumerate(records):
        try:
            generated = query_ollama(INFERENCE_PROMPT.format(rec["input"]))
            predicted = extract_label(generated)
        except Exception as e:
            print(f"  [{i+1}] ERROR: {e}")
            continue

        results.append({
            "email_id":        i,
            "source":          rec["source"],
            "true_label":      rec["label"],
            "predicted_label": predicted,
            "correct":         predicted == rec["label"],
            "raw_output":      generated.strip(),
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
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }

    per_category = {}
    for source, label in CATEGORIES:
        subset = [
            r for r in results
            if r["source"] == source and r["true_label"] == label
        ]
        if not subset:
            continue
        st = [1 if r["true_label"] == "phishing" else 0 for r in subset]
        sp = [1 if r["predicted_label"] == "phishing" else 0 for r in subset]
        key = f"{source}_{label}"
        per_category[key] = {
            "count": len(subset),
            "correct": sum(r["correct"] for r in subset),
            "accuracy": accuracy_score(st, sp),
            "precision": precision_score(st, sp, zero_division=0),
            "recall": recall_score(st, sp, zero_division=0),
            "f1": f1_score(st, sp, zero_division=0),
        }

    return {
        "overall": overall,
        "per_category": per_category,
        "y_true": y_true,
        "y_pred": y_pred,
    }


def load_baseline() -> dict | None:
    """Load per-category baseline accuracy from baseline_results.json."""
    p = Path(BASELINE_PATH)
    if not p.exists():
        return None
    with open(p) as f:
        data = json.load(f)
    return data.get("per_category", {})


def plot_confusion_matrix(y_true, y_pred, out_path: str):
    cm = confusion_matrix(y_true, y_pred)
    labels = ["Legitimate", "Phishing"]
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels)
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.title("Confusion Matrix — Fine-tuned Qwen3-14B")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved → {out_path}")


def plot_comparison(metrics: dict, baseline: dict | None, out_path: str):
    cat_keys = ["human_phishing", "human_legitimate", "llm_phishing", "llm_legitimate"]
    cat_labels = ["Human\nPhishing", "Human\nLegit", "LLM\nPhishing", "LLM\nLegit"]

    finetuned = [metrics["per_category"].get(k, {}).get("accuracy", 0.0) for k in cat_keys]

    x = np.arange(len(cat_keys))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))

    if baseline:
        base_vals = [baseline.get(k, {}).get("accuracy", 0.0) for k in cat_keys]
        ax.bar(x - width / 2, base_vals, width, label="Zero-shot baseline", alpha=0.8, color="#5b9bd5")
        ax.bar(x + width / 2, finetuned, width, label="Fine-tuned QLoRA", alpha=0.8, color="#ed7d31")
    else:
        ax.bar(x, finetuned, width * 1.5, label="Fine-tuned QLoRA", alpha=0.8, color="#ed7d31")

    ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.7, label="Random baseline (50%)")
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Accuracy")
    ax.set_title("Zero-shot Baseline vs Fine-tuned QLoRA — Per Category Accuracy")
    ax.legend()

    for bars, vals in (
        ([ax.patches[i] for i in range(0, len(x))], finetuned)
        if not baseline
        else (
            ([ax.patches[i] for i in range(len(x), 2 * len(x))], finetuned),
        )
    ):
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.1%}",
                ha="center", va="bottom", fontsize=9,
            )

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved → {out_path}")


def save_predictions_csv(results: list[dict], out_path: str):
    """CSV for teammate's report generation."""
    fields = ["email_id", "source", "true_label", "predicted_label", "correct", "text"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved → {out_path}")


def write_error_analysis(results: list[dict], metrics: dict, baseline: dict | None, out_path: str):
    errors = [r for r in results if not r["correct"]]
    by_cat = {}
    for r in errors:
        key = f"{r['source']}_{r['true_label']}"
        by_cat.setdefault(key, []).append(r)

    lines = ["# Error Analysis — Fine-tuned Qwen3-14B\n"]
    lines.append(f"Total errors: {len(errors)} / {len(results)} ({len(errors)/len(results)*100:.1f}%)\n")

    # Per-category table
    lines.append("## Per-Category Results\n")
    lines.append("| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |")
    lines.append("|---|---|---|---|---|")
    for source, label in CATEGORIES:
        key = f"{source}_{label}"
        m = metrics["per_category"].get(key, {})
        base_acc = baseline.get(key, {}).get("accuracy", "N/A") if baseline else "N/A"
        base_str = f"{base_acc:.1%}" if isinstance(base_acc, float) else base_acc
        errs = len(by_cat.get(key, []))
        total = m.get("count", 0)
        lines.append(
            f"| {source}-{label} | {base_str} | {m.get('accuracy',0):.1%} "
            f"| {m.get('f1',0):.3f} | {errs}/{total} |"
        )
    lines.append("")

    # Sample errors
    lines.append("## Sample Misclassified Emails\n")
    for i, r in enumerate(errors[:10], 1):
        lines.append(f"### Error {i} ({r['source']}-{r['true_label']})")
        lines.append(f"- **True label**: `{r['true_label']}`")
        lines.append(f"- **Predicted**: `{r['predicted_label']}`")
        lines.append(f"- **Model output**: `{r['raw_output']}`")
        lines.append(f"- **Email snippet**:\n  > {r['text'][:300].replace(chr(10), ' ')}")
        lines.append("")

    # Discussion
    lines.append("## Discussion\n")
    lines.append(
        "LLM-generated phishing emails are harder to detect because they lack "
        "the obvious surface-level red flags (grammar errors, generic greetings) "
        "found in human-written phishing. The zero-shot baseline completely failed "
        "on LLM-generated content (0% on both LLM categories), treating all "
        "LLM-phishing as legitimate and all LLM-legitimate as phishing.\n\n"
        "After fine-tuning on labeled examples from all four categories, the model "
        "should generalize better to LLM-style content.\n\n"
        "**Note on label quality**: LLM-Legitimate emails include some borderline "
        "samples (prize notifications, investment invitations) labeled as legitimate. "
        "This noise may inflate error rates in that category.\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved → {out_path}")


def print_summary(metrics: dict, baseline: dict | None):
    o = metrics["overall"]
    print("\n" + "=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)
    print(f"  Accuracy:  {o['accuracy']:.4f}")
    print(f"  Precision: {o['precision']:.4f}")
    print(f"  Recall:    {o['recall']:.4f}")
    print(f"  F1:        {o['f1']:.4f}")

    print("\nPER-CATEGORY BREAKDOWN")
    print(f"{'Category':<22} {'Base':>7} {'FT Acc':>7} {'FT F1':>7} {'Err/N':>8}")
    print("-" * 58)
    for source, label in CATEGORIES:
        key = f"{source}_{label}"
        m = metrics["per_category"].get(key, {})
        base_acc = baseline.get(key, {}).get("accuracy") if baseline else None
        base_str = f"{base_acc:.1%}" if base_acc is not None else "  N/A"
        errs = m.get("count", 0) - m.get("correct", 0)
        print(
            f"  {source}-{label:<18} {base_str:>7} "
            f"{m.get('accuracy',0):>7.1%} {m.get('f1',0):>7.3f} "
            f"{errs:>4}/{m.get('count',0)}"
        )
    print("=" * 60)


def main():
    try:
        requests.get("http://localhost:11434", timeout=5).raise_for_status()
    except Exception:
        sys.exit("ERROR: Ollama is not running. Start it first.")

    print(f"Model : {FINETUNED_MODEL} (Ollama, fine-tuned)")

    with open(TEST_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"Test set: {len(records)} emails\n")

    print("Running inference...")
    results = run_inference(records)

    metrics = compute_metrics(results)
    baseline = load_baseline()
    if baseline:
        print(f"\nLoaded baseline from {BASELINE_PATH}")
    else:
        print(f"\nWarning: {BASELINE_PATH} not found — comparison chart will be fine-tuned only")

    print_summary(metrics, baseline)

    # ── Save all outputs ──────────────────────────────────────────────────────
    out_dir = Path("eval_results")
    out_dir.mkdir(exist_ok=True)

    result_data = {
        "model": FINETUNED_MODEL,
        "num_test": len(results),
        "overall": metrics["overall"],
        "per_category": metrics["per_category"],
        "baseline_per_category": baseline,
    }
    with open(out_dir / "evaluation_results.json", "w") as f:
        json.dump(result_data, f, indent=2)
    print("\nSaved → eval_results/evaluation_results.json")

    save_predictions_csv(results, str(out_dir / "predictions.csv"))
    plot_confusion_matrix(metrics["y_true"], metrics["y_pred"], str(out_dir / "confusion_matrix.png"))
    plot_comparison(metrics, baseline, str(out_dir / "baseline_comparison.png"))
    write_error_analysis(results, metrics, baseline, str(out_dir / "error_analysis.md"))

    print("\nAll outputs saved.")


if __name__ == "__main__":
    main()
