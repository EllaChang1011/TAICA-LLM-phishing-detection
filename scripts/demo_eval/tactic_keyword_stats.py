"""Count how often each tactic-card keyword appears in phishing vs legitimate
training emails. Keywords are shown to the model in the tactic prompt, so a
phrase that is common in legitimate mail (e.g. "free") nudges the model to tag
legitimate emails. Only phrases that are almost exclusive to phishing are kept.

Usage:
  python scripts/demo_eval/tactic_keyword_stats.py                    # all keywords in demo/tactics.json
  python scripts/demo_eval/tactic_keyword_stats.py "invoice is overdue" "relief fund"   # candidate phrases
"""

import json
import re
import sys
from pathlib import Path

TRAIN_PATH   = Path("data/train/data.json")
TACTICS_PATH = Path("demo/tactics.json")
MIN_SHARE    = 0.9   # fraction of matching emails that are phishing
MIN_PHISHING = 2     # phrase must appear in at least this many phishing emails


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower())


def count(phrase: str, emails: list[str]) -> int:
    # word boundaries so "IRS" does not match "first"
    pattern = re.compile(r'(?<!\w)' + re.escape(normalize(phrase)) + r'(?!\w)')
    return sum(bool(pattern.search(e)) for e in emails)


def main():
    records = json.loads(TRAIN_PATH.read_text(encoding="utf-8"))
    phishing = [normalize(r["input"]) for r in records if r["label"] == "phishing"]
    legit    = [normalize(r["input"]) for r in records if r["label"] == "legitimate"]

    if len(sys.argv) > 1:
        rows = [("candidate", p) for p in sys.argv[1:]]
    else:
        tactics = json.loads(TACTICS_PATH.read_text(encoding="utf-8"))
        rows = [(c["id"], k) for c in tactics["lures"] + tactics["techniques"] for k in c["keywords"]]

    print(f"{'card':18s} {'phrase':45s} {'phish':>5s} {'legit':>5s} share  keep")
    for card, phrase in rows:
        p, l = count(phrase, phishing), count(phrase, legit)
        share = p / (p + l) if p + l else 0.0
        keep = share >= MIN_SHARE and p >= MIN_PHISHING
        print(f"{card:18s} {phrase[:45]:45s} {p:5d} {l:5d} {share:5.2f}  {'Y' if keep else '-'}")


if __name__ == "__main__":
    main()
