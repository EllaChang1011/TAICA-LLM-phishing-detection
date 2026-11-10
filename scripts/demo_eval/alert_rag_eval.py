"""Scam-alert RAG evaluation: which query finds the right FTC alert?

Rules (grading levels, what "no alert" means, how long alerts are embedded) are
fixed in eval_results/alert_rag/rules.md, written before labeling.

Usage:
  python scripts/demo_eval/alert_rag_eval.py build   # sample 20 test emails, write the answer sheet
  python scripts/demo_eval/alert_rag_eval.py run     # after labeling: compare queries A / B / C / D

Files (eval_results/alert_rag/):
  answers.md     answer sheet — lure / specific / general alerts per email
  results.json   retrieval results per query (written by `run`)
  report.md      scores (written by `run`)
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tactic_cards_eval import TEST_PATH, sample_emails  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "demo"))
from CoT_Module import load_tactics  # noqa: E402
from alert_rag import EMBEDDING_MODEL, QUERY_PREFIX, index_text  # noqa: E402,F401  (shared with the demo)

ALERTS_PATH  = Path("knowledge_base/scam_alerts.json")
OUT_DIR      = Path("eval_results/alert_rag")
ANSWERS_PATH = OUT_DIR / "answers.md"
EXAM_ANSWERS = Path("eval_results/tactic_exam/answers.md")
SEED         = 7
PLAN = {
    ("phishing", "human"): 7,
    ("phishing", "llm"): 7,
    ("legitimate", "human"): 3,
    ("legitimate", "llm"): 3,
}
SELF_LABEL_COUNT = 10        # R01..R10 are left blank for the author to label from scratch
GENERAL_ALERTS = {"A03", "A11"}
TARGETED_COUNT = 10        # T01..T10, hand-picked per rules.md section 5

ENTRY_RE = re.compile(
    r"^## ([RT]\d+)\s+\(test index (\d+)\).*?"
    r"^> lure:(.*?)$\s*^> specific:(.*?)$\s*^> general:(.*?)$\s*^> labeled_by:(.*?)$",
    re.S | re.M,
)


def used_test_indices() -> set[int]:
    dev = {item["test_index"] for item in sample_emails()}
    exam = set(map(int, re.findall(r"test index (\d+)", EXAM_ANSWERS.read_text(encoding="utf-8"))))
    return dev | exam


def build():
    if ANSWERS_PATH.exists():
        sys.exit(f"{ANSWERS_PATH} already exists — refusing to overwrite your labels.")
    used = used_test_indices()
    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    sample = []
    for (label, source), count in PLAN.items():
        pool = [(i, r) for i, r in enumerate(records)
                if r["label"] == label and r["source"] == source and i not in used]
        sample.extend(rng.sample(pool, count))
    rng.shuffle(sample)

    alerts = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    lure_ids = ", ".join(c["id"] for c in load_tactics()["lures"])
    lines = [
        "# 詐騙警示 RAG 評測題：標準答案", "",
        "規則見 [rules.md](rules.md)。**在看到任何檢索結果之前標完。**", "",
        f"- R01～R{SELF_LABEL_COUNT:02d}：留空，請自己從頭標（labeled_by 填 author）",
        f"- R{SELF_LABEL_COUNT + 1:02d}～R20：Claude 預標，請複核（同意就把 labeled_by 改成 claude+author）", "",
        "每封填：",
        "- `lure:` 這封信的正確誘餌 id（查詢 D 會用到）",
        "- `specific:` 專屬警示編號，逗號分隔，沒有就留空",
        "- `general:` 通用警示，只能是 A03、A11，沒有就留空", "",
        f"誘餌 id：{lure_ids}", "",
        "## 警示清單", "",
        "| 編號 | 日期 | 標題 |", "|---|---|---|",
    ]
    lines += [f"| {a['ref']}{'（通用）' if a['ref'] in GENERAL_ALERTS else ''} | {a['date']} | {a['title']} |"
              for a in alerts]
    lines.append("")
    for n, (idx, r) in enumerate(sample, 1):
        lines += [
            "---", "",
            f"## R{n:02d}  (test index {idx})  資料集標籤：{r['label']} / {r['source']}", "",
            "```", r["input"][:3000].strip(), "```", "",
            "> lure: ", "> specific: ", "> general: ",
            f"> labeled_by: {'' if n <= SELF_LABEL_COUNT else 'claude'}", "",
        ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ANSWERS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(sample)} emails to {ANSWERS_PATH}")


def parse_answers() -> list[dict]:
    alerts = {a["ref"] for a in json.loads(ALERTS_PATH.read_text(encoding="utf-8"))}
    lure_ids = {c["id"] for c in load_tactics()["lures"]}
    text = ANSWERS_PATH.read_text(encoding="utf-8")
    answers, problems = [], []
    for rid, idx, lure, specific, general, labeled_by in ENTRY_RE.findall(text):
        lure = lure.strip()
        specific = [x.strip() for x in specific.split(",") if x.strip()]
        general = [x.strip() for x in general.split(",") if x.strip()]
        if lure not in lure_ids:
            problems.append(f"{rid}: lure {lure!r} is not a lure id")
        for x in specific:
            if x not in alerts or x in GENERAL_ALERTS:
                problems.append(f"{rid}: specific alert {x!r} must be one of A01..A23 except A03/A11")
        for x in general:
            if x not in GENERAL_ALERTS:
                problems.append(f"{rid}: general alert {x!r} must be A03 or A11")
        if lure == "none" and (specific or general):
            problems.append(f"{rid}: lure is none but alerts are filled in")
        if "author" not in labeled_by:
            problems.append(f"{rid}: labeled_by does not include author — not reviewed yet")
        answers.append({"rid": rid, "group": "random" if rid.startswith("R") else "targeted",
                        "test_index": int(idx), "lure": lure,
                        "specific": specific, "general": general, "labeled_by": labeled_by.strip()})
    n_random = sum(a["rid"].startswith("R") for a in answers)
    n_targeted = sum(a["rid"].startswith("T") for a in answers)
    if n_random != sum(PLAN.values()) or n_targeted != TARGETED_COUNT:
        problems.append(f"found {n_random} random + {n_targeted} targeted entries, "
                        f"expected {sum(PLAN.values())} + {TARGETED_COUNT}")
    if problems:
        sys.exit("Answer sheet is not complete:\n  " + "\n  ".join(problems))
    return answers


TOP_K = 3
THRESHOLDS = [round(0.50 + 0.025 * i, 3) for i in range(13)]   # 0.50 .. 0.80
QUERIES = {
    "A": "信件原文",
    "B": "模型判斷的誘餌說明",
    "C": "誘餌說明＋證據原句",
    "D": "正確誘餌說明（人工標註）",
}


def lure_query(lure_id: str | None, cards: dict) -> str | None:
    if not lure_id or lure_id == "none":
        return None
    card = cards[lure_id]
    return f"{card['name_en']}: {card['description']}"


def build_queries(email: str, gold_lure: str, tactic: dict, cards: dict) -> dict:
    verified = tactic.get("verified") or {"lure": None, "techniques": []}
    pred_lure = verified["lure"]["id"] if verified["lure"] else None
    b = lure_query(pred_lure, cards)
    evidence = [p["evidence"] for p in [verified["lure"], *verified["techniques"]] if p and p.get("evidence")]
    c = f"{b}\nEvidence from the email: " + " / ".join(evidence) if b and evidence else b
    return {"A": email, "B": b, "C": c, "D": lure_query(gold_lure, cards), "_pred_lure": pred_lure}


def score_group(rows: list[dict], q: str, threshold: float | None) -> dict:
    any_hit = any_n = spec_hit = spec_n = none_ok = none_n = 0
    for r in rows:
        ranking = r["rankings"].get(q)          # None when the query was skipped (lure = none)
        shown = [x["ref"] for x in (ranking or [])[:TOP_K]
                 if threshold is None or x["score"] >= threshold]
        g = r["gold"]
        relevant = set(g["specific"]) | set(g["general"])
        if relevant:
            any_n += 1
            any_hit += bool(relevant & set(shown))
        if g["specific"]:
            spec_n += 1
            spec_hit += bool(set(g["specific"]) & set(shown))
        else:
            none_n += 1
            none_ok += set(shown) <= set(g["general"])   # nothing shown, or only its general alerts
    return {"any_hit": [any_hit, any_n], "specific_hit": [spec_hit, spec_n], "no_alert_ok": [none_ok, none_n]}


def frac(pair: list[int]) -> str:
    return f"{pair[0]}/{pair[1]}" if pair[1] else "—"


def write_report(results: list[dict], path: Path):
    groups = {"random": [r for r in results if r["gold"]["group"] == "random"],
              "targeted": [r for r in results if r["gold"]["group"] == "targeted"]}
    lines = ["# 詐騙警示 RAG：四種查詢比較", "",
             "規則見 [rules.md](rules.md)。隨機組與針對組分開報告，不合併。", "",
             "## 不套門檻（只看前 3 名）", ""]
    for name, rows in groups.items():
        label = "隨機組（20 封）" if name == "random" else "針對組（10 封，刻意挑選）"
        lines += [f"### {label}", "", "| 查詢 | 任一命中@3 | 專屬命中@3 |", "|---|---|---|"]
        for q, desc in QUERIES.items():
            s = score_group(rows, q, None)
            lines.append(f"| {q} {desc} | {frac(s['any_hit'])} | {frac(s['specific_hit'])} |")
        lines.append("")
    n_spec = sum(bool(r["gold"]["specific"]) for r in groups["random"])
    lines += [f"隨機組中有專屬警示的信：{n_spec}/{len(groups['random'])}", "",
              "## 門檻掃描", "",
              "每個門檻下：針對組的專屬命中@3，以及隨機組「沒有專屬警示的信」正確回答找不到的比例。", ""]
    for q, desc in QUERIES.items():
        lines += [f"### {q} {desc}", "", "| 門檻 | 針對組 專屬命中@3 | 隨機組 正確回答找不到 |", "|---|---|---|"]
        for t in THRESHOLDS:
            st = score_group(groups["targeted"], q, t)
            sr = score_group(groups["random"], q, t)
            lines.append(f"| {t:.3f} | {frac(st['specific_hit'])} | {frac(sr['no_alert_ok'])} |")
        lines.append("")
    lines += ["## 逐封結果（前 3 名）", "",
              "| # | 正確誘餌 | 模型誘餌 | 專屬 | 通用 | " + " | ".join(QUERIES) + " |",
              "|---|---|---|---|---|" + "---|" * len(QUERIES)]
    for r in results:
        g = r["gold"]
        cells = []
        for q in QUERIES:
            ranking = r["rankings"].get(q)
            cells.append("（不查）" if ranking is None else
                         ", ".join(f"{x['ref']} {x['score']:.2f}" for x in ranking[:TOP_K]))
        lines.append(f"| {g['rid']} | {g['lure']} | {r['pred_lure']} | {', '.join(g['specific']) or '—'} | "
                     f"{', '.join(g['general']) or '—'} | " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    answers = parse_answers()
    from sentence_transformers import SentenceTransformer
    from tactic_cards_eval import run_new

    tactics = load_tactics()
    cards = {c["id"]: c for c in tactics["lures"]}
    alerts = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))

    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    passages = [index_text(a, model.tokenizer) for a in alerts]
    alert_emb = model.encode(passages, normalize_embeddings=True)

    results = []
    for n, gold in enumerate(answers, 1):
        print(f"[{n}/{len(answers)}] {gold['rid']} idx={gold['test_index']}", flush=True)
        email = records[gold["test_index"]]["input"][:6000]
        tactic = run_new(email, tactics)
        queries = build_queries(email, gold["lure"], tactic, cards)
        rankings = {}
        for q in QUERIES:
            if queries[q] is None:
                rankings[q] = None
                continue
            emb = model.encode([QUERY_PREFIX + queries[q]], normalize_embeddings=True)[0]
            scores = alert_emb @ emb
            order = scores.argsort()[::-1]
            rankings[q] = [{"ref": alerts[i]["ref"], "score": round(float(scores[i]), 4)} for i in order]
        results.append({"gold": gold, "pred_lure": queries["_pred_lure"],
                        "queries": {q: queries[q] for q in QUERIES}, "rankings": rankings,
                        "tactic_raw": tactic.get("raw")})

    (OUT_DIR / "results.json").write_text(json.dumps({"index_texts": dict(zip([a["ref"] for a in alerts], passages)),
                                                      "results": results}, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    write_report(results, OUT_DIR / "report.md")
    print(f"Wrote {OUT_DIR / 'report.md'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "run"])
    args = parser.parse_args()
    build() if args.command == "build" else run()


if __name__ == "__main__":
    main()
