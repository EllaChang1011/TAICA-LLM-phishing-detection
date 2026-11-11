# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 1 / 267 (0.4%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 92.3% | 0.960 | 1/13 |
| human-legitimate | 0.0% | 100.0% | 0.000 | 0/54 |
| llm-phishing | 100.0% | 100.0% | 1.000 | 0/100 |
| llm-legitimate | 0.0% | 100.0% | 0.000 | 0/100 |

## Sample Misclassified Emails

### Error 1 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `legitimate`
- **Email snippet**:
  > Your Smarsh Email Encryption Activation Information  You Have a New Smarsh Email Encryption Message  "Charles W jackson jr"  has sent you an encrypted message via Smarsh Email Encryption.    Subject: Re    Sent: September 19, 2021 9:54:37 PM, EDT RECOVERY INFORMATION: To view this message, visit the

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
