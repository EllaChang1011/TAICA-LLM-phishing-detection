#!/usr/bin/env python3
"""
Compare plain direct classification vs few-shot exemplar-RAG direct classification
on the phishing email test set.

Few-shot RAG retrieves the k most similar LABELED emails from the training set
(embedded into the "phishing_examples" ChromaDB collection by
build_rag_chroma_examples.py) and injects them as in-context examples into the
classification prompt.

Usage:
  python scripts/fewshot_rag_eval.py               # all 400 emails
  python scripts/fewshot_rag_eval.py --limit 40    # quick sanity check
  python scripts/fewshot_rag_eval.py --k 5         # number of few-shot examples (default 3)

Output (saved to eval_results/):
  fewshot_rag_results.json
  fewshot_rag_summary.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

OLLAMA_URL      = "http://localhost:11434/api/generate"
MODEL_NAME      = "phishing-detector-14b"
TEST_PATH       = "data/test/data.json"
OUT_DIR         = Path("eval_results")
CHROMA_DB_PATH  = "demo/chroma_db"
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

PLAIN_PROMPT_TEMPLATE = """/no_think
Classify the following email as phishing or legitimate. Reply with a single word: phishing or legitimate.

### Email:
{EMAIL_TEXT}

### Classification:
"""


def build_plain_prompt(email: str) -> str:
    return PLAIN_PROMPT_TEMPLATE.replace("{EMAIL_TEXT}", email)


def build_fewshot_prompt(email: str, examples: list[dict]) -> str:
    blocks = []
    for ex in examples:
        blocks.append(f"### Example Email:\n{ex['text']}\n### Classification: {ex['label']}\n")
    examples_section = "\n".join(blocks)
    return (
        "/no_think\n"
        "Classify the following email as phishing or legitimate. "
        "Reply with a single word: phishing or legitimate.\n\n"
        "Here are some labeled examples for reference:\n\n"
        + examples_section
        + "\n### Email:\n"
        + email
        + "\n### Classification:\n"
    )


def load_examples_components():
    import chromadb
    from sentence_transformers import SentenceTransformer
    print(f"Loading embedding model {EMBEDDING_MODEL}...")
    embed_model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection("phishing_examples")
    print(f"Few-shot example pool ready — {collection.count()} labeled emails.\n")
    return embed_model, collection


def retrieve_fewshot_examples(email: str, embed_model, collection, k: int) -> list[dict]:
    query_emb = embed_model.encode(email).tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    examples = []
    for i in range(len(results["documents"][0])):
        examples.append({
            "text": results["documents"][0][i],
            "label": results["metadatas"][0][i]["label"],
            "distance": results["distances"][0][i],
        })
    return examples


def query_ollama(prompt: str, num_predict: int = 16) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0, "num_predict": num_predict},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def classify(raw: str) -> str:
    t = raw.lower()
    if "phishing" in t:
        return "phishing"
    if "legitimate" in t:
        return "legitimate"
    return "phishing"  # safer default for security tasks


def metrics(details: list, method: str) -> dict:
    y_true = [1 if d["true_label"] == "phishing" else 0 for d in details]
    y_pred = [1 if d[f"pred_{method}"] == "phishing" else 0 for d in details]
    return {
        "accuracy":  accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall":    recall_score(y_true, y_pred, zero_division=0),
        "f1":        f1_score(y_true, y_pred, zero_division=0),
    }


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


def print_table(details: list):
    for method, label in [("plain", "Direct (no examples)"), ("fewshot", "Direct + Few-shot RAG")]:
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
    agree = sum(1 for d in details if d["pred_plain"] == d["pred_fewshot"])
    print(f"  Plain == Few-shot: {agree}/{len(details)} ({agree/len(details)*100:.1f}%)")
    disagree = [d for d in details if d["pred_plain"] != d["pred_fewshot"]]
    plain_wins   = sum(1 for d in disagree if d["pred_plain"]   == d["true_label"])
    fewshot_wins = sum(1 for d in disagree if d["pred_fewshot"] == d["true_label"])
    print(f"  On disagreements ({len(disagree)} emails):")
    print(f"    Plain correct: {plain_wins}  |  Few-shot correct: {fewshot_wins}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="Evaluate only first N emails (default: all 400)")
    parser.add_argument("--k", type=int, default=3,
                        help="Number of few-shot examples to retrieve (default: 3)")
    args = parser.parse_args()

    try:
        requests.get("http://localhost:11434", timeout=5)
    except Exception:
        sys.exit("ERROR: Ollama is not running.")

    embed_model, collection = load_examples_components()

    test_data = json.loads(Path(TEST_PATH).read_text(encoding="utf-8"))
    if args.limit:
        test_data = test_data[:args.limit]
    print(f"Evaluating {len(test_data)} emails | model: {MODEL_NAME} | k={args.k}")
    print("This will run PLAIN then FEW-SHOT RAG classification for each email.\n")

    OUT_DIR.mkdir(exist_ok=True)
    details = []
    t_start = time.time()

    for i, sample in enumerate(test_data):
        email      = sample["input"]
        true_label = sample["label"].strip().lower()
        source     = sample.get("source", "unknown")

        # --- Plain direct ---
        try:
            raw_plain  = query_ollama(build_plain_prompt(email))
            pred_plain = classify(raw_plain)
        except Exception as e:
            print(f"[{i+1:3d}] PLAIN ERROR: {e}")
            pred_plain = "phishing"

        # --- Few-shot RAG ---
        try:
            examples     = retrieve_fewshot_examples(email, embed_model, collection, args.k)
            raw_fewshot  = query_ollama(build_fewshot_prompt(email, examples))
            pred_fewshot = classify(raw_fewshot)
        except Exception as e:
            print(f"[{i+1:3d}] FEWSHOT ERROR: {e}")
            examples, pred_fewshot = [], "phishing"

        ok_p = "✓" if pred_plain == true_label else "✗"
        ok_f = "✓" if pred_fewshot == true_label else "✗"
        elapsed = time.time() - t_start
        avg_s   = elapsed / (i + 1)
        eta_s   = avg_s * (len(test_data) - i - 1)
        print(f"[{i+1:3d}/{len(test_data)}] plain:{ok_p}({pred_plain:<10}) "
              f"fewshot:{ok_f}({pred_fewshot:<10}) true:{true_label:<10} "
              f"ETA {eta_s/60:.0f}m")

        details.append({
            "index":          i,
            "source":         source,
            "true_label":     true_label,
            "pred_plain":     pred_plain,
            "pred_fewshot":   pred_fewshot,
            "fewshot_labels": [ex["label"] for ex in examples],
        })

        # checkpoint
        (OUT_DIR / "fewshot_rag_results.json").write_text(
            json.dumps({"details": details, "n_completed": i + 1}, indent=2, ensure_ascii=False)
        )

    print_table(details)

    summary = {
        "model":     MODEL_NAME,
        "k":         args.k,
        "n_samples": len(details),
        "plain":     {**metrics(details, "plain"),   **{"per_category": per_category_accuracy(details, "plain")}},
        "fewshot":   {**metrics(details, "fewshot"), **{"per_category": per_category_accuracy(details, "fewshot")}},
        "agreement": sum(1 for d in details if d["pred_plain"] == d["pred_fewshot"]) / len(details),
    }
    result_path  = OUT_DIR / "fewshot_rag_results.json"
    summary_path = OUT_DIR / "fewshot_rag_summary.json"
    result_path.write_text(
        json.dumps({"summary": summary, "details": details}, indent=2, ensure_ascii=False)
    )
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSaved: {result_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
