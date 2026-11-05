"""Generation step: turn the retrieved FTC alerts into advice for this email.

Runs only when at least one alert passed the retrieval threshold. The model sees
the FULL alert text (the "what to do" part sits in the tail, which the index
deliberately leaves out) and must ground every sentence:

- match:  how this email resembles an alert — quotes the email AND the alert
- advice: what to do — each item quotes the alert it comes from

verify_advice() keeps only items whose alert was actually shown and whose quotes
are found in the email / alert text (same evidence_score() as the tactic
analysis). Like the tactic check, it catches invented quotes but cannot tell
whether the Chinese sentence faithfully reflects the quote — that needs review.
"""

import json
import re

from CoT_Module import EVIDENCE_MATCH_THRESHOLD, evidence_score, extract_json

MAX_EMAIL_CHARS = 3000
CJK = re.compile(r"[\u4e00-\u9fff]")

ADVICE_PROMPT_TEMPLATE = """\
/no_think
You help a reader decide what to do about a suspicious email. Use ONLY the FTC
consumer alerts below. Do not add advice that is not written in these alerts.

ALERTS:
{alerts}

EMAIL:
{email}

Tasks:
1. "match": explain in one Traditional Chinese sentence how this email uses the same
   scam as ONE of the alerts. Give the alert ref, one sentence copied character-for-character
   from the EMAIL, and one sentence copied character-for-character from that ALERT.
2. "advice": 2 to 4 things the reader should do or know, each in one Traditional Chinese
   sentence. Every item must name the alert ref it comes from and copy, character-for-character,
   the sentence in that alert that says it. If the alerts do not say something, do not write it.
3. Quotes must be complete sentences copied exactly. Never shorten a quote with "..." or "…".
4. Alert refs are written like A14, without brackets.

Return ONLY valid JSON:
{{
  "match": {{"alert": "A..", "email_quote": "...", "alert_quote": "...", "text": "..."}},
  "advice": [{{"alert": "A..", "quote": "...", "text": "..."}}]
}}
"""


def build_advice_prompt(email_text: str, alerts: list[dict]) -> str:
    blocks = "\n\n".join(f"[{a['ref']}] {a['title']} ({a['source']}, {a['date']})\n{a['text']}" for a in alerts)
    return ADVICE_PROMPT_TEMPLATE.format(alerts=blocks, email=email_text[:MAX_EMAIL_CHARS])


def verify_advice(report: dict, email_text: str, alerts: list[dict],
                  threshold: float = EVIDENCE_MATCH_THRESHOLD) -> dict:
    by_ref = {a["ref"]: a for a in alerts}
    rejected = []

    def check_alert_quote(item, kind):
        ref = str(item.get("alert") or "").strip().strip("[]").strip()   # tolerate "[A14]"
        quote = item.get("quote") or item.get("alert_quote") or ""
        if ref not in by_ref:
            rejected.append({"kind": kind, "item": item, "reason": "alert_not_shown"})
            return None
        score = evidence_score(quote, by_ref[ref]["text"])
        if score < threshold:
            rejected.append({"kind": kind, "item": item, "reason": "quote_not_in_alert", "score": round(score, 3)})
            return None
        return by_ref[ref]

    def is_chinese(item, kind):
        if CJK.search(str(item.get("text") or "")):
            return True
        rejected.append({"kind": kind, "item": item, "reason": "not_chinese"})
        return False

    match = report.get("match") if isinstance(report.get("match"), dict) else None
    if match is not None and not is_chinese(match, "match"):
        match = None
    if match is not None:
        alert = check_alert_quote(match, "match")
        if alert is None:
            match = None
        else:
            score = evidence_score(match.get("email_quote") or "", email_text)
            if score < threshold:
                rejected.append({"kind": "match", "item": match, "reason": "quote_not_in_email", "score": round(score, 3)})
                match = None
            else:
                match = {**match, "alert": alert["ref"], "alert_title": alert["title"], "alert_url": alert["url"]}

    advice = []
    for item in report.get("advice") or []:
        if not isinstance(item, dict) or not item.get("text"):
            rejected.append({"kind": "advice", "item": item, "reason": "malformed"})
            continue
        if not is_chinese(item, "advice"):
            continue
        alert = check_alert_quote(item, "advice")
        if alert is not None:
            advice.append({**item, "alert": alert["ref"], "alert_title": alert["title"], "alert_url": alert["url"]})

    return {"match": match, "advice": advice, "rejected": rejected}


def generate_advice(email_text: str, alerts: list[dict], call_fn) -> dict:
    """call_fn(prompt) -> raw model text. Returns the verified advice plus the raw output."""
    raw = call_fn(build_advice_prompt(email_text, alerts))
    report = extract_json(raw)
    if report is None:
        return {"parse_error": True, "raw_output": raw, "match": None, "advice": [], "rejected": []}
    return {**verify_advice(report, email_text, alerts), "raw_output": raw}


def to_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)
