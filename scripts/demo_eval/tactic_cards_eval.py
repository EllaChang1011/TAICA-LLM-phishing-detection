"""Side-by-side comparison of the old free-form CoT report vs the new tactic-card
analysis (demo/tactics.json) on a small hand-reviewable sample of test emails.

Checks three things:
  1. Are the chosen tactics right?          -> human review (fill in the .md report)
  2. Is the quoted evidence really in the email? -> automatic (verify_tactic_report)
  3. Are legitimate emails tagged with tactics?   -> automatic

Usage:
  python scripts/demo_eval/tactic_cards_eval.py              # 20 emails (10 phishing / 10 legitimate)
  python scripts/demo_eval/tactic_cards_eval.py --limit 2    # quick sanity check

Outputs (eval_results/tactic_cards/):
  tactic_cards_results.json   raw outputs of both versions
  tactic_cards_review.md      side-by-side report for manual review
"""

import argparse
from collections import Counter
import json
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "legacy"))
from legacy_cot import build_cot_prompt, enforce_consistency  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "demo"))
from CoT_Module import build_tactic_prompt, extract_json, load_tactics, verify_tactic_report  # noqa: E402

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phishing-detector-14b"
TEST_PATH  = Path("data/test/data.json")
OUT_DIR    = Path("eval_results/tactic_cards")
SEED       = 42

# (label, source) -> count. More LLM-written legitimate emails: that is where the
# old CoT produced the most false phishing indicators.
SAMPLE_PLAN = {
    ("phishing", "human"): 5,
    ("phishing", "llm"): 5,
    ("legitimate", "human"): 4,
    ("legitimate", "llm"): 6,
}


def query_ollama(prompt: str, options: dict) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False, "options": options},
        timeout=300,
    )
    response.raise_for_status()
    return response.json().get("response", "")


# Old version: same call settings as demo/app.py model_fn
OLD_OPTIONS = {"temperature": 0.0, "num_predict": 1024,
               "repeat_penalty": 1.5, "frequency_penalty": 0.5}
# New version: no repetition penalties — they push the model to paraphrase,
# which breaks verbatim evidence quoting.
NEW_OPTIONS = {"temperature": 0.0, "num_predict": 1024}


def run_old(email: str) -> dict:
    raw = query_ollama(build_cot_prompt(email), OLD_OPTIONS)
    report = extract_json(raw)
    if report is None:
        return {"raw": raw, "parse_error": True}
    return {"raw": raw, "report": enforce_consistency(report)}


def run_new(email: str, tactics: dict) -> dict:
    raw = query_ollama(build_tactic_prompt(email, tactics), NEW_OPTIONS)
    report = extract_json(raw)
    if report is None:
        return {"raw": raw, "parse_error": True}
    verified = verify_tactic_report(report, email, tactics)
    for pick in [verified["lure"], *verified["techniques"]]:
        if pick:
            pick.pop("card", None)  # keep the json small
    return {"raw": raw, "report": report, "verified": verified}


def sample_emails() -> list[dict]:
    records = json.loads(TEST_PATH.read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    sample = []
    for (label, source), count in SAMPLE_PLAN.items():
        pool = [(i, r) for i, r in enumerate(records)
                if r["label"] == label and r["source"] == source]
        for idx, r in rng.sample(pool, count):
            sample.append({"test_index": idx, "label": label, "source": source,
                           "email": r["input"][:6000]})
    return sample


def summarize(results: list[dict]) -> dict:
    legit = [r for r in results if r["label"] == "legitimate"]
    new_ok = [r for r in results if not r["new"].get("parse_error")]
    old_ok = [r for r in results if not r["old"].get("parse_error")]

    picks = sum(1 + len(r["new"]["report"].get("techniques") or []) for r in new_ok)
    rejected = [x for r in new_ok for x in r["new"]["verified"]["rejected"]]

    def old_tags_legit(r):
        rep = r["old"].get("report", {})
        return bool([i for i in rep.get("phishing_indicators", []) if i and i != "..."])

    def new_tags_legit(r):
        v = r["new"].get("verified")
        if not v:
            return False
        return (v["lure"] is not None and v["lure"]["id"] != "none") or bool(v["techniques"])

    return {
        "n_emails": len(results),
        "parse_errors": {"old": len(results) - len(old_ok), "new": len(results) - len(new_ok)},
        "new_picks_total": picks,
        "new_picks_rejected": len(rejected),
        "new_rejected_by_reason": dict(Counter(x["reason"] for x in rejected)),
        "legit_tagged": {
            "n_legit": len(legit),
            "old_has_phishing_indicators": sum(old_tags_legit(r) for r in legit),
            "old_final_phishing": sum(r["old"].get("report", {}).get("final", "").lower() == "phishing"
                                      for r in legit),
            "new_has_tactic": sum(new_tags_legit(r) for r in legit),
        },
    }


def write_review(results: list[dict], summary: dict, tactics: dict, path: Path):
    names = {c["id"]: c["name"] for c in tactics["lures"] + tactics["techniques"]}
    lt = summary["legit_tagged"]
    lines = [
        "# 招數卡測試：舊版 CoT vs 新版招數卡",
        "",
        "## 自動統計",
        "",
        "| 項目 | 舊版 | 新版 |",
        "|---|---|---|",
        f"| JSON 解析失敗 | {summary['parse_errors']['old']} | {summary['parse_errors']['new']} |",
        f"| 正常信被套上可疑特徵（共 {lt['n_legit']} 封） | {lt['old_has_phishing_indicators']} | {lt['new_has_tactic']} |",
        f"| 正常信被判成 phishing | {lt['old_final_phishing']} | （新版不判斷） |",
        f"| 模型選的招數總數 | — | {summary['new_picks_total']} |",
        f"| 被丟掉：id 不在清單 | — | {summary['new_rejected_by_reason'].get('unknown_id', 0)} |",
        f"| 被丟掉：證據不在信裡 | — | {summary['new_rejected_by_reason'].get('evidence_not_found', 0)} |",
        f"| 被丟掉：選了 none 又選手法 | — | {summary['new_rejected_by_reason'].get('lure_is_none', 0)} |",
        "",
        "## 人工檢查：招數選得對不對",
        "",
        "每封信讀完後，在「你的判斷」寫：✅ 對 / ❌ 錯（寫正確的招數）/ ⚠️ 部分對",
        "",
        "程式只能確認引用的句子真的在信裡，不能確認這句話支持這個招數，所以要特別看：",
        "",
        "- 證據句能不能單獨證明這個招數（例如「Dear customer」不能證明法律恐嚇）",
        "- 帳號到期 / 安全警告 / 信箱錯誤 三類有沒有選錯（記下被混淆的次數）",
        "",
    ]
    for n, r in enumerate(results, 1):
        lines += [f"---\n\n## #{n}  {r['label']} / {r['source']}  (test index {r['test_index']})", "",
                  "<details><summary>信件內容</summary>", "", "```", r["email"][:2000], "```", "",
                  "</details>", ""]

        lines.append("### 舊版 CoT")
        old = r["old"]
        if old.get("parse_error"):
            lines.append(f"解析失敗。原始輸出：`{old['raw'][:300]!r}`")
        else:
            rep = old["report"]
            lines += [f"- final: **{rep.get('final')}**, risk_score: {rep.get('risk_score')}",
                      f"- phishing_indicators: {rep.get('phishing_indicators')}",
                      f"- urgency_tactics: {rep.get('urgency_tactics')}",
                      f"- impersonation: {rep.get('impersonation')}",
                      f"- credential_harvesting: {rep.get('credential_harvesting')}"]
        lines.append("")

        lines.append("### 新版招數卡")
        new = r["new"]
        if new.get("parse_error"):
            lines.append(f"解析失敗。原始輸出：`{new['raw'][:300]!r}`")
        else:
            v = new["verified"]
            lure = v["lure"]
            lines.append(f"- 誘餌：**{names.get(lure['id'], lure['id']) if lure else '（被丟掉）'}**"
                         + (f" — \"{lure['evidence']}\"" if lure and lure["evidence"] else ""))
            for t in v["techniques"]:
                lines.append(f"- 手法：**{names[t['id']]}** — \"{t['evidence']}\" (score {t['score']})")
            for x in v["rejected"]:
                lines.append(f"- ❌ 丟掉（{x['reason']}，score {x.get('score', '-')}）：`{x['pick']}`")
            lines.append(f"- 摘要：{v['summary']}")
        lines += ["", "> **你的判斷：** ", ""]

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N sampled emails")
    args = parser.parse_args()

    tactics = load_tactics()
    sample = sample_emails()
    if args.limit:
        sample = sample[:args.limit]

    OUT_DIR.mkdir(exist_ok=True)
    results = []
    for n, item in enumerate(sample, 1):
        print(f"[{n}/{len(sample)}] {item['label']}/{item['source']} idx={item['test_index']}", flush=True)
        item["old"] = run_old(item["email"])
        item["new"] = run_new(item["email"], tactics)
        results.append(item)

    summary = summarize(results)
    (OUT_DIR / "tactic_cards_results.json").write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    write_review(results, summary, tactics, OUT_DIR / "tactic_cards_review.md")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
