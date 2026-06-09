"""Extract text from the RAG knowledge sources (APWG PDF reports + MITRE ATT&CK
technique pages) and split it into semantic chunks for embedding.

Output: knowledge_base/chunks.json — list of {text, source, section, page}
"""

import json
import re
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

KB_DIR = Path("knowledge_base")
CHUNK_SIZE = 450      # target chunk length in characters
CHUNK_OVERLAP = 50
MIN_PARAGRAPH_LEN = 50


# ── Cleaning ──────────────────────────────────────────────────────────────────

def clean_apwg_text(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d+", stripped):                     # page numbers
            continue
        if "apwg.org" in stripped.lower():                     # footer banner
            continue
        if re.fullmatch(r"(table of contents|contents)", stripped, re.I):
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned)


def merge_short_paragraphs(paragraphs):
    merged = []
    for p in paragraphs:
        if merged and len(p) < MIN_PARAGRAPH_LEN:
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return merged


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_paragraphs(paragraphs, source, section, page=None):
    """Greedily pack paragraphs into ~CHUNK_SIZE windows with overlap."""
    chunks = []
    buffer = ""
    for para in paragraphs:
        if buffer and len(buffer) + len(para) + 1 > CHUNK_SIZE:
            chunks.append(buffer.strip())
            overlap = buffer[-CHUNK_OVERLAP:]
            buffer = overlap + " " + para
        else:
            buffer = (buffer + " " + para).strip()
    if buffer.strip():
        chunks.append(buffer.strip())

    return [
        {"text": c, "source": source, "section": section, "page": page}
        for c in chunks if len(c) >= MIN_PARAGRAPH_LEN
    ]


# ── APWG PDF extraction ───────────────────────────────────────────────────────

def process_apwg_pdf(path: Path):
    doc = fitz.open(path)
    chunks = []
    for page_num, page in enumerate(doc, start=1):
        text = clean_apwg_text(page.get_text())
        if not text.strip():
            continue
        paragraphs = merge_short_paragraphs(
            [p.strip() for p in re.split(r"\n{1,}", text) if p.strip()]
        )
        chunks.extend(chunk_paragraphs(paragraphs, source=path.stem, section="report body", page=page_num))
    return chunks


# ── MITRE ATT&CK extraction ───────────────────────────────────────────────────

def process_mitre_html(path: Path):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    technique_id = path.stem
    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else technique_id
    source = f"MITRE ATT&CK {technique_id} — {title}"

    chunks = []

    desc = soup.select_one("div.description-body")
    if desc:
        paragraphs = merge_short_paragraphs(
            [p.get_text(" ", strip=True) for p in desc.find_all(["p", "li"]) if p.get_text(strip=True)]
        )
        if not paragraphs:
            paragraphs = [desc.get_text(" ", strip=True)]
        chunks.extend(chunk_paragraphs(paragraphs, source=source, section="Description"))

    for heading_text, section_id in [("Mitigations", "mitigations"), ("Detection Strategy", "detection")]:
        section = soup.select_one(f"#{section_id}")
        if not section:
            continue
        rows = section.select("table tr")
        paragraphs = []
        for row in rows:
            cells = [c.get_text(" ", strip=True) for c in row.select("td, th")]
            cells = [c for c in cells if c]
            if cells:
                paragraphs.append(" — ".join(cells))
        paragraphs = merge_short_paragraphs(paragraphs)
        chunks.extend(chunk_paragraphs(paragraphs, source=source, section=heading_text))

    return chunks


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    all_chunks = []

    for pdf_path in sorted((KB_DIR / "apwg").glob("*.pdf")):
        c = process_apwg_pdf(pdf_path)
        print(f"{pdf_path.name}: {len(c)} chunks")
        all_chunks.extend(c)

    for html_path in sorted((KB_DIR / "mitre").glob("*.html")):
        c = process_mitre_html(html_path)
        print(f"{html_path.name}: {len(c)} chunks")
        all_chunks.extend(c)

    out_path = KB_DIR / "chunks.json"
    out_path.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")

    lengths = [len(c["text"]) for c in all_chunks]
    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Avg length : {sum(lengths) / len(lengths):.1f}")
    print(f"Min / Max  : {min(lengths)} / {max(lengths)}")
    print(f"Saved to   : {out_path}")


if __name__ == "__main__":
    main()
