"""Clean the scam-alert knowledge base for the alert RAG.

Input : knowledge_base/scam_alerts_raw.jsonl  (one alert per line: title, date, url, source, text;
        text copied from FTC consumer alerts — US government works, public domain)
Output: knowledge_base/scam_alerts.json       (same fields + id, markdown stripped)

One alert = one retrieval unit; alerts are short, so they are not chunked.
"""

import json
import re
from pathlib import Path

RAW_PATH = Path("knowledge_base/scam_alerts_raw.jsonl")
OUT_PATH = Path("knowledge_base/scam_alerts.json")


def strip_markdown(text: str) -> str:
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)          # images
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)      # [label](url) -> label
    text = re.sub(r'\*\*|__', '', text)                       # bold
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', text)     # _italic_
    text = re.sub(r'^\s*[*-]\s+', '- ', text, flags=re.M)     # unify bullets
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def make_id(url: str) -> str:
    # https://consumer.ftc.gov/consumer-alerts/2024/09/dont-take-bait-phishing-scams -> ftc-2024-09-dont-take-bait-phishing-scams
    m = re.search(r'/consumer-alerts/(\d{4})/(\d{2})/([^/?#]+)', url)
    if not m:
        raise ValueError(f"unexpected alert url: {url}")
    return f"ftc-{m.group(1)}-{m.group(2)}-{m.group(3)}"


def main():
    alerts = []
    for line in RAW_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        a = json.loads(line)
        alerts.append({
            "ref": f"A{len(alerts) + 1:02d}",   # short id used on the answer sheet
            "id": make_id(a["url"]),
            "title": a["title"],
            "date": a["date"],
            "source": a["source"],
            "url": a["url"],
            "text": strip_markdown(a["text"]),
        })
    ids = [a["id"] for a in alerts]
    assert len(ids) == len(set(ids)), "duplicate alert ids"
    OUT_PATH.write_text(json.dumps(alerts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(alerts)} alerts to {OUT_PATH}")
    for a in alerts:
        print(f"  {a['ref']}  {a['date']}  {len(a['text']):5d} chars  {a['id']}")


if __name__ == "__main__":
    main()
