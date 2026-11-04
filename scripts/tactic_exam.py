"""Held-out "exam" set for the tactic-card analysis.

The 20 emails in tactic_cards_eval.py are the practice (dev) set used to tune the
prompt. This exam set is sampled from the rest of the test split, hand-labeled
once, and run ONCE at the end — its numbers are the official result.

Usage:
  python scripts/tactic_exam.py build    # sample emails, write the answer sheet to label
  python scripts/tactic_exam.py run      # after labeling: run the model once and score it

Files (eval_results/tactic_exam/):
  answers.md      answer sheet — fill in lure / techniques / exclude for every email
  results.json    raw model outputs + scores (written by `run`)
  report.md       score summary + per-email table (written by `run`)
"""

import argparse
import json
import random
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tactic_cards_eval import TEST_PATH, run_new, run_old, sample_emails  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "demo"))
from CoT_Module import load_tactics  # noqa: E402

EXAM_DIR     = Path("eval_results/tactic_exam")
ANSWERS_PATH = EXAM_DIR / "answers.md"
RESULTS_PATH = EXAM_DIR / "results.json"
REPORT_PATH  = EXAM_DIR / "report.md"
EXAM_SEED    = 2026
EXAM_PLAN = {
    ("phishing", "human"): 12,
    ("phishing", "llm"): 12,
    ("legitimate", "human"): 12,
    ("legitimate", "llm"): 12,
}
# Lures that all end in "log in to fix your account" and are hard to tell apart
LOGIN_LURES = {"account_expiry", "security_alert", "mailbox_error"}

ENTRY_RE = re.compile(
    r"^## (E\d+)\s+\(test index (\d+)\).*?"
    r"^> lure:(.*?)$\s*^> techniques:(.*?)$\s*^> exclude:(.*?)$",
    re.S | re.M,
)


def build():
    if ANSWERS_PATH.exists():
        sys.exit(f"{ANSWERS_PATH} already exists — refusing to overwrite your labels.")

    dev_indices = {item["test_index"] for item in sample_emails()}
    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    rng = random.Random(EXAM_SEED)
    sample = []
    for (label, source), count in EXAM_PLAN.items():
        pool = [(i, r) for i, r in enumerate(records)
                if r["label"] == label and r["source"] == source and i not in dev_indices]
        sample.extend((i, r) for i, r in rng.sample(pool, count))
    rng.shuffle(sample)  # so labels are not grouped by class while labeling

    tactics = load_tactics()
    lure_ids = ", ".join(c["id"] for c in tactics["lures"])
    tech_ids = ", ".join(c["id"] for c in tactics["techniques"])
    lines = [
        "# 招數卡考試用資料：標準答案",
        "",
        "每封信填三行：",
        "",
        "- `lure:` 填 1 個誘餌 id",
        "- `techniques:` 填 0 到多個手法 id，用逗號分隔；沒有就留空",
        "- `exclude:` 資料集標籤明顯錯誤（例如感謝付款信被標成 phishing）就填 `yes`，這封不計分",
        "",
        f"誘餌 id：{lure_ids}",
        "",
        f"手法 id：{tech_ids}",
        "",
        "判斷依據是**信件內容**，不是資料集標籤。標籤只是給你參考，用來找出標錯的信。",
        "",
    ]
    for n, (idx, r) in enumerate(sample, 1):
        lines += [
            "---", "",
            f"## E{n:02d}  (test index {idx})  資料集標籤：{r['label']} / {r['source']}", "",
            "```", r["input"][:3000].strip(), "```", "",
            "> lure: ",
            "> techniques: ",
            "> exclude: no",
            "",
        ]
    EXAM_DIR.mkdir(parents=True, exist_ok=True)
    ANSWERS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(sample)} emails to {ANSWERS_PATH}")


def parse_answers(tactics: dict) -> list[dict]:
    lure_ids = {c["id"] for c in tactics["lures"]}
    tech_ids = {c["id"] for c in tactics["techniques"]}
    text = ANSWERS_PATH.read_text(encoding="utf-8")
    answers, problems = [], []
    for exam_id, idx, lure, techs, exclude in ENTRY_RE.findall(text):
        lure = lure.strip()
        techs = [t.strip() for t in techs.split(",") if t.strip()]
        exclude = exclude.strip().lower() in {"yes", "y", "true"}
        if not exclude:
            if lure not in lure_ids:
                problems.append(f"{exam_id}: lure {lure!r} is not a lure id")
            for t in techs:
                if t not in tech_ids:
                    problems.append(f"{exam_id}: technique {t!r} is not a technique id")
            if lure == "none" and techs:
                problems.append(f"{exam_id}: lure is none but techniques are filled in")
        answers.append({"exam_id": exam_id, "test_index": int(idx), "lure": lure,
                        "techniques": techs, "exclude": exclude})
    expected = sum(EXAM_PLAN.values())
    if len(answers) != expected:
        problems.append(f"found {len(answers)} entries, expected {expected} — check the '> ' lines")
    if problems:
        sys.exit("Answer sheet is not complete:\n  " + "\n  ".join(problems))
    return answers


def score(results: list[dict]) -> dict:
    scored = [r for r in results if not r["gold"]["exclude"]]
    lure_correct = 0
    tp = fp = fn = 0
    login_confusions = 0
    gold_none = tagged_none = old_flagged_none = 0
    picks = fabricated = 0

    for r in scored:
        gold = r["gold"]
        v = r["new"].get("verified") or {"lure": None, "techniques": [], "rejected": []}
        pred_lure = v["lure"]["id"] if v["lure"] else None
        pred_techs = {t["id"] for t in v["techniques"]}
        gold_techs = set(gold["techniques"])

        lure_correct += pred_lure == gold["lure"]
        tp += len(pred_techs & gold_techs)
        fp += len(pred_techs - gold_techs)
        fn += len(gold_techs - pred_techs)
        if gold["lure"] in LOGIN_LURES and pred_lure in LOGIN_LURES and pred_lure != gold["lure"]:
            login_confusions += 1

        if gold["lure"] == "none":
            gold_none += 1
            tagged_none += (pred_lure not in (None, "none")) or bool(pred_techs)
            old_rep = r["old"].get("report", {})
            old_flagged_none += bool([i for i in old_rep.get("phishing_indicators", []) if i and i != "..."])

        if not r["new"].get("parse_error"):
            picks += 1 + len(r["new"]["report"].get("techniques") or [])
            fabricated += sum(x["reason"] == "evidence_not_found" for x in v["rejected"])

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n_emails": len(results),
        "n_scored": len(scored),
        "n_excluded": len(results) - len(scored),
        "lure_accuracy": round(lure_correct / len(scored), 3) if scored else None,
        "technique_precision": round(precision, 3),
        "technique_recall": round(recall, 3),
        "technique_f1": round(2 * precision * recall / (precision + recall), 3) if precision + recall else 0.0,
        "login_lure_confusions": login_confusions,
        "no_tactic_emails": gold_none,
        "no_tactic_emails_tagged_new": tagged_none,
        "no_tactic_emails_flagged_old": old_flagged_none,
        "picks_total": picks,
        "picks_fabricated_evidence": fabricated,
        "parse_errors_new": sum(bool(r["new"].get("parse_error")) for r in results),
    }


def write_report(results: list[dict], s: dict):
    lines = [
        "# 招數卡考試結果（正式數字）", "",
        f"執行時間：{s['ran_at']}　計分 {s['n_scored']} 封（排除 {s['n_excluded']} 封標籤錯誤）", "",
        "| 指標 | 數值 |", "|---|---|",
        f"| 誘餌正確率 | {s['lure_accuracy']} |",
        f"| 手法 precision / recall / F1 | {s['technique_precision']} / {s['technique_recall']} / {s['technique_f1']} |",
        f"| 帳號到期 / 安全警告 / 信箱錯誤 互相混淆 | {s['login_lure_confusions']} 次 |",
        f"| 沒有招數的信被套上招數（新版） | {s['no_tactic_emails_tagged_new']} / {s['no_tactic_emails']} |",
        f"| 沒有招數的信被列出釣魚指標（舊版） | {s['no_tactic_emails_flagged_old']} / {s['no_tactic_emails']} |",
        f"| 引用的證據不在信裡 | {s['picks_fabricated_evidence']} / {s['picks_total']} |",
        f"| JSON 解析失敗（新版） | {s['parse_errors_new']} |",
        "", "## 逐封結果", "",
        "| # | 標準答案 | 模型 | 誘餌 |", "|---|---|---|---|",
    ]
    for r in results:
        g = r["gold"]
        if g["exclude"]:
            lines.append(f"| {g['exam_id']} | （排除） | | |")
            continue
        v = r["new"].get("verified") or {"lure": None, "techniques": []}
        pred_lure = v["lure"]["id"] if v["lure"] else "（無效）"
        gold_str = g["lure"] + (" + " + ", ".join(g["techniques"]) if g["techniques"] else "")
        pred_str = pred_lure + (" + " + ", ".join(t["id"] for t in v["techniques"]) if v["techniques"] else "")
        lines.append(f"| {g['exam_id']} | {gold_str} | {pred_str} | {'✅' if pred_lure == g['lure'] else '❌'} |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(force: bool):
    if RESULTS_PATH.exists() and not force:
        sys.exit(f"{RESULTS_PATH} already exists. The exam is meant to be run once; "
                 "pass --force only if the previous run failed.")
    tactics = load_tactics()
    answers = parse_answers(tactics)
    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))

    results = []
    for n, gold in enumerate(answers, 1):
        print(f"[{n}/{len(answers)}] {gold['exam_id']} idx={gold['test_index']}", flush=True)
        email = records[gold["test_index"]]["input"][:6000]
        results.append({"gold": gold, "old": run_old(email), "new": run_new(email, tactics)})

    s = score(results)
    s["ran_at"] = datetime.now().isoformat(timespec="seconds")
    RESULTS_PATH.write_text(json.dumps({"summary": s, "results": results}, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    write_report(results, s)
    print(json.dumps(s, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "run"])
    parser.add_argument("--force", action="store_true", help="re-run even if results already exist")
    args = parser.parse_args()
    build() if args.command == "build" else run(args.force)


if __name__ == "__main__":
    main()
