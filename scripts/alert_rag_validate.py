"""Held-out validation of the frozen scam-alert RAG setting (rules.md section 7).

The setting was chosen after looking at the practice set (alert_rag_eval.py):
  query = raw email, skipped when the tactic analysis says lure = none,
  show alerts with similarity >= 0.600, at most 3.
This script checks it ONCE on emails from the val split that no experiment has used.

Usage:
  python scripts/alert_rag_validate.py build   # write the answer sheet
  python scripts/alert_rag_validate.py run     # after labeling: run the frozen setting once

Files (eval_results/alert_rag/validation/):
  answers.md, results.json, report.md
"""

import argparse
import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alert_rag_eval import (ALERTS_PATH, EMBEDDING_MODEL, GENERAL_ALERTS, QUERY_PREFIX,  # noqa: E402
                            TOP_K, frac, index_text, score_group)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "demo"))
from CoT_Module import load_tactics  # noqa: E402

VAL_PATH     = Path("data/val/data.json")
OUT_DIR      = Path("eval_results/alert_rag/validation")
ANSWERS_PATH = OUT_DIR / "answers.md"
RESULTS_PATH = OUT_DIR / "results.json"
REPORT_PATH  = OUT_DIR / "report.md"

# Frozen setting — do not change after the validation set is built
THRESHOLD = 0.600
SEED = 11
RANDOM_PLAN = {
    ("phishing", "human"): 3,
    ("phishing", "llm"): 3,
    ("legitimate", "human"): 2,
    ("legitimate", "llm"): 2,
}
# val index -> category, picked by reading the content (rules.md section 5 criteria)
TARGETED = {
    223: "包裹運費", 138: "包裹運費", 98: "發票催款", 58: "中獎", 155: "退稅",
    74: "求職", 390: "投資", 18: "慈善捐款", 32: "法律恐嚇", 49: "帳單付款",
}

ENTRY_RE = re.compile(
    r"^## ([VW]\d+)\s+\(val index (\d+)\).*?"
    r"^> lure:(.*?)$\s*^> specific:(.*?)$\s*^> general:(.*?)$\s*^> labeled_by:(.*?)$",
    re.S | re.M,
)


def build():
    if ANSWERS_PATH.exists():
        sys.exit(f"{ANSWERS_PATH} already exists — refusing to overwrite your labels.")
    records = json.loads(VAL_PATH.read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    random_part = []
    for (label, source), count in RANDOM_PLAN.items():
        pool = [i for i, r in enumerate(records)
                if r["label"] == label and r["source"] == source and i not in TARGETED]
        random_part.extend(rng.sample(pool, count))
    rng.shuffle(random_part)

    alerts = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    lure_ids = ", ".join(c["id"] for c in load_tactics()["lures"])
    lines = [
        "# 詐騙警示 RAG 驗證集：標準答案", "",
        "規則見 [../rules.md](../rules.md) 第 7 節。設定已凍結，**標完才跑，只跑一次，結果不好也不調整。**", "",
        "來源：data/val（這些實驗都沒用過的切分）。V＝隨機、W＝針對。", "",
        "- `lure:` 正確誘餌 id",
        "- `specific:` 專屬警示編號，逗號分隔，沒有就留空",
        "- `general:` 通用警示，只能是 A03、A11，沒有就留空", "",
        f"誘餌 id：{lure_ids}", "",
        "| 編號 | 日期 | 標題 |", "|---|---|---|",
    ]
    lines += [f"| {a['ref']}{'（通用）' if a['ref'] in GENERAL_ALERTS else ''} | {a['date']} | {a['title']} |"
              for a in alerts]
    lines.append("")
    entries = [("V", i, "") for i in random_part] + [("W", i, cat) for i, cat in TARGETED.items()]
    counters = {"V": 0, "W": 0}
    for prefix, idx, cat in entries:
        counters[prefix] += 1
        r = records[idx]
        tail = f"  挑選類別：{cat}" if cat else ""
        lines += [
            "---", "",
            f"## {prefix}{counters[prefix]:02d}  (val index {idx})  資料集標籤：{r['label']} / {r['source']}{tail}", "",
            "```", r["input"][:3000].strip(), "```", "",
            "> lure: ", "> specific: ", "> general: ", "> labeled_by: ", "",
        ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ANSWERS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(entries)} emails to {ANSWERS_PATH}")


def parse_answers() -> list[dict]:
    alerts = {a["ref"] for a in json.loads(ALERTS_PATH.read_text(encoding="utf-8"))}
    lure_ids = {c["id"] for c in load_tactics()["lures"]}
    answers, problems = [], []
    for rid, idx, lure, specific, general, labeled_by in ENTRY_RE.findall(ANSWERS_PATH.read_text(encoding="utf-8")):
        lure = lure.strip()
        specific = [x.strip() for x in specific.split(",") if x.strip()]
        general = [x.strip() for x in general.split(",") if x.strip()]
        if lure not in lure_ids:
            problems.append(f"{rid}: lure {lure!r} is not a lure id")
        problems += [f"{rid}: specific alert {x!r} must be one of A01..A23 except A03/A11"
                     for x in specific if x not in alerts or x in GENERAL_ALERTS]
        problems += [f"{rid}: general alert {x!r} must be A03 or A11" for x in general if x not in GENERAL_ALERTS]
        if lure == "none" and (specific or general):
            problems.append(f"{rid}: lure is none but alerts are filled in")
        if "author" not in labeled_by:
            problems.append(f"{rid}: labeled_by does not include author — not reviewed yet")
        answers.append({"rid": rid, "group": "random" if rid.startswith("V") else "targeted",
                        "val_index": int(idx), "lure": lure, "specific": specific, "general": general,
                        "labeled_by": labeled_by.strip()})
    if len(answers) != sum(RANDOM_PLAN.values()) + len(TARGETED):
        problems.append(f"found {len(answers)} entries, expected {sum(RANDOM_PLAN.values()) + len(TARGETED)}")
    if problems:
        sys.exit("Answer sheet is not complete:\n  " + "\n  ".join(problems))
    return answers


def run(force: bool):
    if RESULTS_PATH.exists() and not force:
        sys.exit(f"{RESULTS_PATH} already exists. Validation runs once; pass --force only if the previous run crashed.")
    answers = parse_answers()
    from sentence_transformers import SentenceTransformer
    from tactic_cards_eval import run_new

    tactics = load_tactics()
    alerts = json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
    records = json.loads(VAL_PATH.read_text(encoding="utf-8"))
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    alert_emb = model.encode([index_text(a, model.tokenizer) for a in alerts], normalize_embeddings=True)

    results = []
    for n, gold in enumerate(answers, 1):
        print(f"[{n}/{len(answers)}] {gold['rid']} val idx={gold['val_index']}", flush=True)
        email = records[gold["val_index"]]["input"][:6000]
        tactic = run_new(email, tactics)
        lure = (tactic.get("verified") or {}).get("lure")
        pred_lure = lure["id"] if lure else None
        if pred_lure in (None, "none"):
            ranking = None                           # gate: no tactic -> no retrieval
        else:
            emb = model.encode([QUERY_PREFIX + email], normalize_embeddings=True)[0]
            scores = alert_emb @ emb
            ranking = [{"ref": alerts[i]["ref"], "score": round(float(scores[i]), 4)} for i in scores.argsort()[::-1]]
        results.append({"gold": gold, "pred_lure": pred_lure, "rankings": {"final": ranking}})

    groups = {g: [r for r in results if r["gold"]["group"] == g] for g in ("random", "targeted")}
    summary = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "threshold": THRESHOLD,
        "random": score_group(groups["random"], "final", THRESHOLD),
        "targeted": score_group(groups["targeted"], "final", THRESHOLD),
        "random_no_threshold": score_group(groups["random"], "final", None),
        "targeted_no_threshold": score_group(groups["targeted"], "final", None),
    }
    RESULTS_PATH.write_text(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    s = summary
    lines = [
        "# 詐騙警示 RAG 驗證結果（正式數字）", "",
        f"執行時間：{s['ran_at']}　設定：原文查詢＋招數分析把關，門檻 {THRESHOLD:.3f}（rules.md 第 7 節，事先凍結）", "",
        "| 指標 | 門檻 0.600 | 不套門檻 | 練習集（門檻 0.600，同一套設定） |", "|---|---|---|---|",
        f"| 針對組 專屬命中@3 | {frac(s['targeted']['specific_hit'])} | {frac(s['targeted_no_threshold']['specific_hit'])} | 10/10 |",
        f"| 隨機組 正確回答找不到 | {frac(s['random']['no_alert_ok'])} | {frac(s['random_no_threshold']['no_alert_ok'])} | 12/16 |",
        f"| 隨機組 任一命中@3 | {frac(s['random']['any_hit'])} | {frac(s['random_no_threshold']['any_hit'])} | — |",
        "", "## 逐封結果", "",
        "| # | 正確誘餌 | 模型誘餌 | 專屬 | 通用 | 顯示的警示（≥ 門檻） | 前 3 名 |", "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        g, ranking = r["gold"], r["rankings"]["final"]
        top = "（不查）" if ranking is None else ", ".join(f"{x['ref']} {x['score']:.2f}" for x in ranking[:TOP_K])
        shown = "—" if ranking is None else ", ".join(x["ref"] for x in ranking[:TOP_K] if x["score"] >= THRESHOLD) or "（無）"
        lines.append(f"| {g['rid']} | {g['lure']} | {r['pred_lure']} | {', '.join(g['specific']) or '—'} | "
                     f"{', '.join(g['general']) or '—'} | {shown} | {top} |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "run"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build() if args.command == "build" else run(args.force)


if __name__ == "__main__":
    main()
