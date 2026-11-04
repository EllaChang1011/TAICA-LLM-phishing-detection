import difflib
import json
import re
import unicodedata
from pathlib import Path

COT_PROMPT_TEMPLATE = """\
You are a cybersecurity SOC analyst.

Your task is to analyze an email and classify it as either:
- phishing
- legitimate

Think step-by-step internally, but ONLY output valid JSON.
DO NOT include explanations outside JSON.
{threat_intel_section}
Classification Rules:
1. If the email contains suspicious links, credential requests, account verification requests,
   financial scams, tax refund claims, inheritance claims, urgent security warnings, or
   impersonation, classify as phishing.
2. If multiple phishing indicators are identified, the final classification MUST be phishing.
3. If phishing indicators suggest phishing, the final classification cannot be legitimate.
4. Ensure consistency between reasoning and final decision.
5. Verify that risk score matches the final label.

Consistency Requirements:
- phishing -> risk_score >= 60
- legitimate -> risk_score <= 40

Keep every field concise (under 100 characters). For url_analysis, list at most 2 distinct URLs — do NOT repeat the same URL.

Return ONLY valid JSON:
{
  "phishing_indicators": ["..."],
  "urgency_tactics": "...",
  "impersonation": "...",
  "url_analysis": "...",
  "credential_harvesting": "...",
  "final": "phishing or legitimate",
  "risk_score": 0
}

EMAIL:
{email_text}
"""


def enforce_consistency(report: dict) -> dict:
    indicators = report.get("phishing_indicators", [])
    risk = report.get("risk_score", 0)
    if isinstance(risk, str):
        try:
            risk = int(risk)
        except ValueError:
            risk = 0
    if (len(indicators) >= 2 or risk >= 60) and report.get("final", "").lower() == "legitimate":
        report["final"] = "phishing"
    return report


def build_cot_prompt(email_text: str, threat_intel: str = "") -> str:
    if threat_intel:
        section = f"\nRELEVANT THREAT INTELLIGENCE (APWG / MITRE ATT&CK):\n{threat_intel}\n"
    else:
        section = ""
    return (COT_PROMPT_TEMPLATE
            .replace("{threat_intel_section}", section)
            .replace("{email_text}", email_text))


# ── Tactic-card analysis ──────────────────────────────────────────────────────
# Explanation-only: picks lures/techniques from tactics.json and quotes evidence
# from the email. Does NOT decide phishing vs legitimate — that is the
# fine-tuned classifier's job.

TACTICS_PATH = Path(__file__).with_name("tactics.json")
EVIDENCE_MATCH_THRESHOLD = 0.9

# Soft hyphen and zero-width characters that phishing emails insert inside words
# to dodge keyword filters (e.g. "Ke<U+00AD>ep S<U+00AD>am<U+00AD>e").
INVISIBLE_CHARS = re.compile('[\u00ad\u200b\u200c\u200d\ufeff]')

# Cyrillic / Greek letters that look like Latin letters, keyed by code point so
# the source stays readable. Mapped by SHAPE, not sound: Cyrillic U+0440 looks
# like "p" but transliterates to "r", so transliteration libraries such as
# unidecode are the wrong tool here.
HOMOGLYPHS = {
    # Cyrillic lowercase
    0x0430: 'a', 0x0435: 'e', 0x043E: 'o', 0x0440: 'p', 0x0441: 'c', 0x0445: 'x',
    0x0443: 'y', 0x0456: 'i', 0x0458: 'j', 0x0455: 's', 0x0501: 'd', 0x04BB: 'h',
    # Cyrillic uppercase
    0x0410: 'A', 0x0412: 'B', 0x0415: 'E', 0x041A: 'K', 0x041C: 'M', 0x041D: 'H',
    0x041E: 'O', 0x0420: 'P', 0x0421: 'C', 0x0422: 'T', 0x0425: 'X', 0x0423: 'Y',
    0x0406: 'I', 0x0408: 'J', 0x0405: 'S',
    # Greek
    0x03BF: 'o', 0x03B1: 'a', 0x03B9: 'i', 0x03BD: 'v', 0x03BA: 'k', 0x03C1: 'p',
    0x0391: 'A', 0x0392: 'B', 0x0395: 'E', 0x0396: 'Z', 0x0397: 'H', 0x0399: 'I',
    0x039A: 'K', 0x039C: 'M', 0x039D: 'N', 0x039F: 'O', 0x03A1: 'P', 0x03A4: 'T',
    0x03A5: 'Y', 0x03A7: 'X',
}
HOMOGLYPH_TABLE = str.maketrans(HOMOGLYPHS)

TACTIC_PROMPT_TEMPLATE = """\
You are a cybersecurity SOC analyst. Explain which phishing tactics an email uses.
You are NOT deciding whether the email is phishing. Only report tactics that are actually present.

LURES (the pretext of the email) — choose exactly ONE:
{lure_cards}

TECHNIQUES (how the email tries to get something from the reader) — choose ZERO OR MORE:
{technique_cards}

Rules:
1. "lure.id" must be one of the LURES ids. Each "techniques[].id" must be one of the
   TECHNIQUES ids. Do not invent new ids or mix the two lists.
2. For every lure and technique you choose, copy ONE sentence or phrase from the email
   as evidence, character-for-character. Do not paraphrase, translate, or fix typos.
   Keep each evidence under 30 words.
3. The evidence must show the tactic by itself. If you cannot find such a sentence,
   do not choose the tactic.
4. If the email makes no deceptive request, choose lure "none" with evidence "" and
   return an empty techniques list. Ordinary business, personal, and newsletter
   emails are "none".
5. The sign-off at the end of an email (sender name, job title, company) is never
   evidence for impersonation. Only choose impersonation when the email body claims
   to come from a specific trusted brand, bank, agency, or the reader's IT team.

Return ONLY valid JSON:
{{
  "lure": {{"id": "...", "evidence": "..."}},
  "techniques": [{{"id": "...", "evidence": "..."}}]
}}

EMAIL:
{email_text}
"""


def load_tactics(path: Path = TACTICS_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _render_cards(cards: list[dict]) -> str:
    lines = []
    for c in cards:
        line = f"- {c['id']}: {c['name_en']} — {c['description']}"
        if c.get("keywords"):
            line += f" Typical phrases: {', '.join(repr(k) for k in c['keywords'])}."
        lines.append(line)
    return "\n".join(lines)


def build_tactic_prompt(email_text: str, tactics: dict) -> str:
    return TACTIC_PROMPT_TEMPLATE.format(
        lure_cards=_render_cards(tactics["lures"]),
        technique_cards=_render_cards(tactics["techniques"]),
        email_text=email_text,
    )


def extract_json(raw: str) -> dict | None:
    """Strip <think> blocks and markdown fences, then parse the first balanced JSON object."""
    cleaned = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)  # unclosed <think>
    cleaned = re.sub(r'```json\s*|```\s*', '', cleaned).strip()

    start = cleaned.find('{')
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(cleaned[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(cleaned[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def find_homoglyph_words(text: str) -> list[dict]:
    """Words that mix Latin letters with Cyrillic/Greek look-alikes, e.g. "P\u0430ssword"
    with a Cyrillic "\u0430". Real mail almost never does this inside one word, so it is
    a deterministic phishing signal that needs no model. Words written entirely in
    Cyrillic or Greek (real Russian / Greek text) are not flagged."""
    found, seen = [], set()
    for word in re.findall(r'\w+', INVISIBLE_CHARS.sub('', text)):
        has_latin = any('a' <= c.lower() <= 'z' for c in word)
        has_spoof = any(ord(c) in HOMOGLYPHS for c in word)
        if has_latin and has_spoof and word not in seen:
            seen.add(word)
            found.append({"word": word, "looks_like": word.translate(HOMOGLYPH_TABLE),
                          "spoofed_chars": sorted({f"U+{ord(c):04X}" for c in word if ord(c) in HOMOGLYPHS})})
    return found


def _normalize(text: str) -> str:
    # NFKC folds full-width chars; invisible chars are dropped and look-alike
    # letters mapped back to Latin so quotes still match emails that use them
    # to dodge filters.
    text = unicodedata.normalize("NFKC", text)
    text = INVISIBLE_CHARS.sub('', text)
    text = text.translate(HOMOGLYPH_TABLE)
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    return re.sub(r'\s+', ' ', text).strip().lower()


def evidence_score(evidence: str, email_text: str) -> float:
    """1.0 if evidence appears verbatim (after normalization); otherwise the best
    similarity against any word window of the email whose length is within one
    word of the evidence (so "mail box" vs "mailbox" still lines up)."""
    ev = _normalize(evidence)
    body = _normalize(email_text)
    if not ev:
        return 0.0
    if ev in body:
        return 1.0
    body_words = body.split(' ')
    n = len(ev.split(' '))
    best = 0.0
    for size in (n - 1, n, n + 1):
        if size < 1:
            continue
        for start in range(max(1, len(body_words) - size + 1)):
            window = ' '.join(body_words[start:start + size])
            best = max(best, difflib.SequenceMatcher(None, ev, window).ratio())
    return best


def build_summary(lure: dict | None, techniques: list[dict]) -> str:
    """Summary assembled from verified picks only, so it cannot say anything the
    evidence does not back up."""
    if lure is None:
        if not techniques:
            return "無法確認這封信使用的招數。"
        head = "誘餌無法確認"
    elif lure["id"] == "none":
        return "未發現可疑招數。"
    else:
        head = f"以「{lure['card']['name']}」為藉口"
    if not techniques:
        return f"{head}。"
    return f"{head}，搭配{'、'.join(t['card']['name'] for t in techniques)}。"


def verify_tactic_report(report: dict, email_text: str, tactics: dict,
                         threshold: float = EVIDENCE_MATCH_THRESHOLD) -> dict:
    """Keep only picks whose id exists in tactics.json and whose evidence is found
    in the email. Rejected picks are kept under "rejected" with the reason, so
    hallucinations can be counted during evaluation.

    Limitation: this only catches made-up quotes. It cannot tell whether a real
    quote actually supports the chosen tactic (e.g. "Dear customer" as evidence
    for legal_threat passes) — that needs human review."""
    lure_cards = {c["id"]: c for c in tactics["lures"]}
    tech_cards = {c["id"]: c for c in tactics["techniques"]}
    rejected = []

    def check(pick, cards, kind):
        if not isinstance(pick, dict):
            rejected.append({"kind": kind, "pick": pick, "reason": "malformed"})
            return None
        tid, evidence = pick.get("id"), pick.get("evidence") or ""
        if tid not in cards:
            rejected.append({"kind": kind, "pick": pick, "reason": "unknown_id"})
            return None
        if tid == "none":
            return {"id": tid, "evidence": "", "card": cards[tid], "score": None}
        score = evidence_score(evidence, email_text)
        if score < threshold:
            rejected.append({"kind": kind, "pick": pick, "reason": "evidence_not_found",
                             "score": round(score, 3)})
            return None
        return {"id": tid, "evidence": evidence, "card": cards[tid], "score": round(score, 3)}

    lure = check(report.get("lure"), lure_cards, "lure")
    techniques = []
    seen = set()
    for pick in report.get("techniques") or []:
        if lure is not None and lure["id"] == "none":
            # "none" means no tactic at all; techniques alongside it contradict that
            rejected.append({"kind": "technique", "pick": pick, "reason": "lure_is_none"})
            continue
        verified = check(pick, tech_cards, "technique")
        if verified and verified["id"] not in seen:
            techniques.append(verified)
            seen.add(verified["id"])

    return {
        "lure": lure,
        "techniques": techniques,
        "summary": build_summary(lure, techniques),
        "rejected": rejected,
    }
