"""Embed the chunks in knowledge_base/chunks.json and store them in a
persistent ChromaDB collection ("phishing_knowledge") for the RAG demo.

This is the "threat intelligence" RAG design — see build_rag_chunks_threat_intel.py
for context. For the alternative "few-shot exemplar" RAG design, see
build_rag_chroma_examples.py."""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("knowledge_base/chunks.json")
CHROMA_DB_PATH = "./demo/chroma_db"
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"
BATCH_SIZE = 32


def main():
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    try:
        client.delete_collection("phishing_knowledge")
    except Exception:
        pass
    collection = client.create_collection(
        name="phishing_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.add(
            ids=[f"chunk-{start + i}" for i in range(len(batch))],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {"source": c["source"], "section": c.get("section") or "", "page": c.get("page") or 0}
                for c in batch
            ],
        )
        print(f"  embedded {start + len(batch)}/{len(chunks)}")

    print(f"\nCollection count: {collection.count()}")
    print(f"Embedding dim   : {len(model.encode(['test']).tolist()[0])}")
    print(f"Saved to        : {CHROMA_DB_PATH}")


if __name__ == "__main__":
    main()
