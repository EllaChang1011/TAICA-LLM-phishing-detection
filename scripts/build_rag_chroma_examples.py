"""Embed the training set emails (data/train/data.json) into a persistent
ChromaDB collection ("phishing_examples") for few-shot exemplar retrieval.

This is the "few-shot exemplar" RAG design — an alternative to the threat-intel
RAG (build_rag_chroma_threat_intel.py). Instead of retrieving general phishing
documentation, this retrieves the k most similar LABELED training emails and
injects them as in-context examples into the classification prompt
(see scripts/fewshot_rag_eval.py).
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

TRAIN_PATH = Path("data/train/data.json")
CHROMA_DB_PATH = "./demo/chroma_db"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"
BATCH_SIZE = 32


def main():
    records = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(records)} training emails")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    try:
        client.delete_collection("phishing_examples")
    except Exception:
        pass
    collection = client.create_collection(
        name="phishing_examples",
        metadata={"hnsw:space": "cosine"},
    )

    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]
        texts = [r["input"] for r in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.add(
            ids=[f"example-{start + i}" for i in range(len(batch))],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {"label": r["label"], "source": r.get("source", "unknown")}
                for r in batch
            ],
        )
        print(f"  embedded {start + len(batch)}/{len(records)}")

    print(f"\nCollection count: {collection.count()}")
    print(f"Saved to        : {CHROMA_DB_PATH}")


if __name__ == "__main__":
    main()
