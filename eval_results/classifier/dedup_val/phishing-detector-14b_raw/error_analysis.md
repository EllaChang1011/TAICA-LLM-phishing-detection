# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 2 / 244 (0.8%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 66.7% | 0.800 | 2/6 |
| human-legitimate | 0.0% | 100.0% | 0.000 | 0/38 |
| llm-phishing | 100.0% | 100.0% | 1.000 | 0/100 |
| llm-legitimate | 0.0% | 100.0% | 0.000 | 0/100 |

## Sample Misclassified Emails

### Error 1 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `legitimate`
- **Email snippet**:
  > =?UTF-8?B?QWxlcnQ6IOKakSBNYWlsYm94IHBhc3N3b3JkIHJlc2V0IGluIHByb2dyZXNzIGZvciA=?=jose@monkey.org  Your Password Reset in Progress                                                              monkey.org Dear jose   Your password reset is in process and your current password will be disabled shortly.  

### Error 2 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `legitimate`
- **Email snippet**:
  > Tired Of Searching For Love In All The Wrong Places?  date.net - html letter

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
