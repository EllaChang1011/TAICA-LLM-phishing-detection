#!/usr/bin/env python3
"""
Chain-of-Thought evaluation on the test set.

Usage:
  python cot_evaluate.py --mode baseline             # Ollama: qwen3.6:latest
  python cot_evaluate.py --mode finetuned            # HF: results/lora_adapter
  python cot_evaluate.py --mode baseline --limit 20  # quick test
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import argparse
import json
import re
import sys
from pathlib import Path

import requests
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "demo"))
from CoT_Module import build_cot_prompt

# ── Config ────────────────────────────────────────────────────────────────────
TEST_PATH    = "data/test/data.json"
OLLAMA_URL   = "http://localhost:11434/api/generate"
BASELINE_MODEL  = "qwen3:14b"
FINETUNED_ADAPTER = "training_runs/results/lora_adapter"
MAX_SEQ_LENGTH   = 2048

# ── Inference helpers ─────────────────────────────────────────────────────────
def query_ollama(model: str, prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": False, "num_predict": 300},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def load_hf_model():
    """Load fine-tuned model via unsloth (lazy, called once)."""
    from unsloth import FastLanguageModel
    import torch
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=FINETUNED_ADAPTER,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
        dtype=None,
    )
    FastLanguageModel.for_inference(model)
    if hasattr(tokenizer, "tokenizer"):
        tokenizer = tokenizer.tokenizer
    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    tokenizer.eos_token    = "<|im_end|>"
    tokenizer.eos_token_id = im_end_id
    if tokenizer.pad_token is None:
        tokenizer.pad_token    = "<|im_end|>"
        tokenizer.pad_token_id = im_end_id
    return model, tokenizer


def query_hf(model, tokenizer, prompt: str) -> str:
    import torch
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=False,
            temperature=1.0,
            use_cache=True,
        )
    return tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )


# ── Parsing ───────────────────────────────────────────────────────────────────
def extract_prediction(response: str):
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    try:
        data = json.loads(response)
        label = data.get("final", "").lower()
        if "phishing" in label: return 1
        if "legitimate" in label: return 0
    except (json.JSONDecodeError, AttributeError):
        pass

    m = re.search(r'\{.*?"final"\s*:\s*"([^"]+)"', response, re.DOTALL)
    if m:
        label = m.group(1).lower()
        if "phishing" in label: return 1
        if "legitimate" in label: return 0

    m = re.search(r'\b(phishing|legitimate)\b', response.lower())
    if m:
        return 1 if m.group(1) == "phishing" else 0
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",  choices=["baseline", "finetuned"], required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    # Setup inference function
    hf_model = hf_tok = None
    if args.mode == "baseline":
        try:
            requests.get("http://localhost:11434", timeout=5).raise_for_status()
        except Exception:
            sys.exit("ERROR: Ollama is not running.")
        infer = lambda prompt: query_ollama(BASELINE_MODEL, prompt)
        model_label = BASELINE_MODEL
    else:
        print("Loading fine-tuned model via HF (this takes ~30s)...")
        hf_model, hf_tok = load_hf_model()
        infer = lambda prompt: query_hf(hf_model, hf_tok, prompt)
        model_label = FINETUNED_ADAPTER

    print(f"Mode  : {args.mode}")
    print(f"Model : {model_label}")

    with open(TEST_PATH, encoding="utf-8") as f:
        test_data = json.load(f)
    if args.limit:
        test_data = test_data[:args.limit]
    print(f"Test samples: {len(test_data)}\n")

    y_true, y_pred, details = [], [], []

    for i, sample in enumerate(test_data):
        email_text = sample["input"]
        true_label = sample["output"].strip().lower()
        true_int    = 1 if true_label == "phishing" else 0
        prompt = build_cot_prompt(email_text)

        try:
            response = infer(prompt)
            pred     = extract_prediction(response)
        except Exception as e:
            print(f"[{i+1}] ERROR: {e}")
            continue

        if pred is None:
            print(f"[{i+1}] PARSE FAIL — skipped")
            continue

        y_true.append(true_int)
        y_pred.append(pred)
        correct = "✓" if pred == true_int else "✗"
        print(f"[{i+1:3d}/{len(test_data)}] {correct}  true={true_label:<10} pred={'phishing' if pred else 'legitimate'}")

        details.append({
            "index":    i,
            "label":    true_label,
            "source":   sample.get("source", ""),
            "pred":     "phishing" if pred else "legitimate",
            "correct":  pred == true_int,
            "response": response,
        })

        # checkpoint after every sample
        out_stem = f"cot_{args.mode}"
        out_dir = Path("eval_results")
        out_dir.mkdir(exist_ok=True)
        (out_dir / f"{out_stem}_details.json").write_text(
            json.dumps(details, indent=2, ensure_ascii=False))
        (out_dir / f"{out_stem}_metrics.json").write_text(json.dumps({
            "mode":      args.mode,
            "model":     model_label,
            "n_samples": len(y_true),
            "accuracy":  accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall":    recall_score(y_true, y_pred, zero_division=0),
            "f1":        f1_score(y_true, y_pred, zero_division=0),
            "partial":   True,
        }, indent=2))

    if not y_true:
        sys.exit("No predictions collected.")

    print("\n" + "="*50)
    print(f"Results — {args.mode} / {model_label}")
    print("="*50)
    metrics = {
        "mode":      args.mode,
        "model":     model_label,
        "n_samples": len(y_true),
        "accuracy":  accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
    }
    for k, v in metrics.items():
        print(f"  {k:<12}: {v:.4f}" if isinstance(v, float) else f"  {k:<12}: {v}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print()
    print(classification_report(y_true, y_pred, target_names=["legitimate", "phishing"]))

    out_stem = f"cot_{args.mode}"
    out_dir = Path("eval_results")
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{out_stem}_metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / f"{out_stem}_details.json").write_text(
        json.dumps(details, indent=2, ensure_ascii=False))
    print(f"Saved: eval_results/{out_stem}_metrics.json  eval_results/{out_stem}_details.json")



if __name__ == "__main__":
    main()
