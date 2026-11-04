"""Scam-alert retrieval: find FTC consumer alerts that match an email.

Setting validated once on held-out emails (eval_results/alert_rag/validation/report.md):
query with the raw email, skip when the tactic analysis says lure "none", show
alerts with cosine similarity >= 0.600, at most 3. Validation: specific alert
found 7/10, correct "no alert" 5/6 — so the demo labels this a preliminary setting.

The evaluation scripts import index_text / QUERY_PREFIX from here, so the demo
and the evaluation always use the same index.
"""

import json
import os
from pathlib import Path

DEFAULT_ALERTS_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "scam_alerts.json"
ALERTS_PATH = Path(os.environ.get("ALERTS_PATH", DEFAULT_ALERTS_PATH))

EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
# bge-v1.5 query instruction for retrieval (passages are embedded without it)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
INDEX_TOKEN_BUDGET = 256     # title + leading paragraphs; the tail of every alert is the same generic advice
MAX_QUERY_CHARS = 6000
THRESHOLD = 0.600
TOP_K = 3


def index_text(alert: dict, tokenizer) -> str:
    """Title + leading paragraphs until the token budget; never cut mid-paragraph."""
    text = alert["title"]
    for para in [p for p in alert["text"].split("\n\n") if p.strip()]:
        candidate = f"{text}\n\n{para}"
        if text != alert["title"] and len(tokenizer(candidate)["input_ids"]) > INDEX_TOKEN_BUDGET:
            break
        text = candidate
    return text


class AlertIndex:
    def __init__(self, embed_model, alerts_path: Path = ALERTS_PATH):
        self.model = embed_model
        self.alerts = json.loads(Path(alerts_path).read_text(encoding="utf-8"))
        self.embeddings = embed_model.encode([index_text(a, embed_model.tokenizer) for a in self.alerts],
                                             normalize_embeddings=True)

    def search(self, email_text: str) -> list[dict]:
        """Top-k alerts above the threshold, each with its similarity score."""
        query = self.model.encode([QUERY_PREFIX + email_text[:MAX_QUERY_CHARS]], normalize_embeddings=True)[0]
        scores = self.embeddings @ query
        hits = []
        for i in scores.argsort()[::-1][:TOP_K]:
            if scores[i] < THRESHOLD:
                break
            hits.append({**self.alerts[i], "score": float(scores[i])})
        return hits
