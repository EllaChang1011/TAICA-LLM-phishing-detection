#!/usr/bin/env python3
"""
Compare direct classification (with /no_think) vs CoT + enforce_consistency
on the phishing email test set.

Usage:
  python scripts/cot_vs_direct_eval.py               # CoT without RAG
  python scripts/cot_vs_direct_eval.py --rag         # CoT with RAG threat intel
  python scripts/cot_vs_direct_eval.py --limit 40    # quick sanity check

Output (saved to eval_results/):
  cot_vs_direct_results.json      / cot_vs_direct_rag_results.json
  cot_vs_direct_summary.json      / cot_vs_direct_rag_summary.json
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

sys.path.insert(0, str(Path(__file__).parent.parent / "demo"))
from CoT_Module import build_cot_prompt, enforce_consistency

OLLAMA_URL          = "http://localhost:11434/api/generate"
MODEL_NAME          = "phishing-detector-14b"
TEST_PATH           = "data/test/data.json"
OUT_DIR             = Path("eval_results")
CHROMA_DB_PATH      = "demo/chroma_db"
EMBEDDING_MODEL     = "BAAI/bge-large-en-v1.5"

DIRECT_PROMPT = """/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{}

### Classification:
"""


def load_rag_components():
    import chromadb
    from sentence_transformers import SentenceTransformer
    print(f"Loading embedding model {EMBEDDING_MODEL}...")
    embed_model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection("phishing_knowledge")
    print(f"RAG ready — {collection.count()} chunks in knowledge base.\n")
    return embed_model, collection


def retrieve_threat_intel(email: str, embed_model, collection, top_k: int = 3) -> str:
    query_emb = embed_model.encode(email).tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    snippets = []
    for i in range(len(results["documents"][0])):
        if results["distances"][0][i] > 0.6:
            continue
        source = results["metadatas"][0][i].get("source", "unknown")
        text   = results["documents"][0][i].strip()
        snippets.append(f"[{source}] {text}")
    return "\n\n".join(snippets)


def query_ollama(prompt: str, num_predict: int) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0, "num_predict": num_predict},
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def classify_direct(email: str) -> str:
    raw = query_ollama(DIRECT_PROMPT.format(email), num_predict=16)
    t = raw.lower()
    if "phishing" in t:
        return "phishing"
    if "legitimate" in t:
        return "legitimate"
    return "phishing"  # safer default for security tasks


def classify_cot(email: str, threat_intel: str = "") -> tuple[str, dict]:
    """Returns (label, parsed_report). Label is 'phishing'/'legitimate'/'unknown'."""
    raw = query_ollama(build_cot_prompt(email, threat_intel=threat_intel), num_predict=300)

    report = {}
    try:
        cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
        cleaned = re.sub(r'```json\s*|```\s*', '', cleaned).strip()
        m = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if m:
            report = json.loads(m.group())
            report = enforce_consistency(report)
            label = report.get("final", "").lower()
            if "phishing" in label:
                return "phishing", report
            if "legitimate" in label:
                return "legitimate", report
    except Exception:
        pass

    # fallback: scan raw text
    m = re.search(r'\b(phishing|legitimate)\b', raw.lower())
    if m:
        return m.group(1), report

    return "phishing", report  # safer default


def per_category_accuracy(details: list, method: str) -> dict:
    cats = [
        ("human", "phishing"),
        ("human", "legitimate"),
        ("llm", "phishing"),
        ("llm", "legitimate"),
    ]
    result = {}
    for source, label in cats:
        subset = [d for d in details if d["source"] == source and d["true_label"] == label]
        if not subset:
            continue
        correct = sum(1 for d in subset if d[f"pred_{method}"] == label)
        result[f"{source}-{label}"] = correct / len(subset)
    return result


def metrics(details: list, method: str) -> dict:
    y_true = [1 if d["true_label"] == "phishing" else 0 for d in details]
    y_pred = [1 if d[f"pred_{method}"] == "phishing" else 0 for d in details]
    return {
        "accuracy":  accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
    }


def print_table(details: list):
    for method, label in [("direct", "Direct (/no_think)"), ("cot", "CoT + enforce_consistency")]:
        m = metrics(details, method)
        cat = per_category_accuracy(details, method)
        print(f"\n{'='*52}")
        print(f"  {label}")
        print(f"{'='*52}")
        print(f"  Accuracy : {m['accuracy']:.4f}   F1: {m['f1']:.4f}")
        print(f"  Precision: {m['precision']:.4f}   Recall: {m['recall']:.4f}")
        print(f"\n  Per-category accuracy:")
        for k, v in cat.items():
            print(f"    {k:<22}: {v*100:.1f}%")

    print(f"\n{'='*52}")
    print(f"  Email-level agreement")
    print(f"{'='*52}")
    agree = sum(1 for d in details if d["pred_direct"] == d["pred_cot"])
    print(f"  Direct == CoT   : {agree}/{len(details)} ({agree/len(details)*100:.1f}%)")
    disagree = [d for d in details if d["pred_direct"] != d["pred_cot"]]
    direct_wins = sum(1 for d in disagree if d["pred_direct"] == d["true_label"])
    cot_wins    = sum(1 for d in disagree if d["pred_cot"]    == d["true_label"])
    print(f"  On disagreements ({len(disagree)} emails):")
    print(f"    Direct correct: {direct_wins}  |  CoT correct: {cot_wins}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="Evaluate only first N emails (default: all 400)")
    parser.add_argument("--rag", action="store_true",
                        help="Feed RAG threat intel into CoT prompt")
    args = parser.parse_args()

    try:
        requests.get("http://localhost:11434", timeout=5)
    except Exception:
        sys.exit("ERROR: Ollama is not running.")

    embed_model = collection = None
    if args.rag:
        embed_model, collection = load_rag_components()

    tag = "rag" if args.rag else "no_rag"
    test_data = json.loads(Path(TEST_PATH).read_text(encoding="utf-8"))
    if args.limit:
        test_data = test_data[:args.limit]
    print(f"Evaluating {len(test_data)} emails | model: {MODEL_NAME} | CoT mode: {tag}")
    print("This will run DIRECT then COT for each email.\n")

    OUT_DIR.mkdir(exist_ok=True)
    details = []
    t_start = time.time()

    for i, sample in enumerate(test_data):
        email      = sample["input"]
        true_label = sample["label"].strip().lower()
        source     = sample.get("source", "unknown")

        # --- Direct ---
        try:
            pred_direct = classify_direct(email)
        except Exception as e:
            print(f"[{i+1:3d}] DIRECT ERROR: {e}")
            pred_direct = "phishing"

        # --- RAG retrieval (only when --rag) ---
        threat_intel = ""
        if args.rag and embed_model is not None:
            try:
                threat_intel = retrieve_threat_intel(email, embed_model, collection)
            except Exception:
                pass

        # --- CoT ---
        try:
            pred_cot, cot_report = classify_cot(email, threat_intel=threat_intel)
        except Exception as e:
            print(f"[{i+1:3d}] COT ERROR: {e}")
            pred_cot, cot_report = "phishing", {}

        ok_d = "✓" if pred_direct == true_label else "✗"
        ok_c = "✓" if pred_cot    == true_label else "✗"
        elapsed = time.time() - t_start
        avg_s   = elapsed / (i + 1)
        eta_s   = avg_s * (len(test_data) - i - 1)
        print(f"[{i+1:3d}/{len(test_data)}] direct:{ok_d}({pred_direct:<10}) "
              f"cot:{ok_c}({pred_cot:<10}) true:{true_label:<10} "
              f"ETA {eta_s/60:.0f}m")

        details.append({
            "index":        i,
            "source":       source,
            "true_label":   true_label,
            "pred_direct":  pred_direct,
            "pred_cot":     pred_cot,
            "cot_report":   cot_report,
            "rag_used":     bool(threat_intel),
        })

        # checkpoint
        (OUT_DIR / f"cot_vs_direct_{tag}_results.json").write_text(
            json.dumps({"details": details, "n_completed": i + 1}, indent=2, ensure_ascii=False)
        )

    # Final summary
    print_table(details)

    summary = {
        "model":     MODEL_NAME,
        "rag":       args.rag,
        "n_samples": len(details),
        "direct":    {**metrics(details, "direct"), **{"per_category": per_category_accuracy(details, "direct")}},
        "cot":       {**metrics(details, "cot"),    **{"per_category": per_category_accuracy(details, "cot")}},
        "agreement": sum(1 for d in details if d["pred_direct"] == d["pred_cot"]) / len(details),
    }
    result_path  = OUT_DIR / f"cot_vs_direct_{tag}_results.json"
    summary_path = OUT_DIR / f"cot_vs_direct_{tag}_summary.json"
    result_path.write_text(
        json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False)
    )
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSaved: {result_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
