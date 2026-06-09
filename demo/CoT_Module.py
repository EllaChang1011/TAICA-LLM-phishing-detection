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
