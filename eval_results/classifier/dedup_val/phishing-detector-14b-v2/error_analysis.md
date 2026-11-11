# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 56 / 244 (23.0%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 100.0% | 1.000 | 0/6 |
| human-legitimate | 0.0% | 97.4% | 0.000 | 1/38 |
| llm-phishing | 100.0% | 100.0% | 1.000 | 0/100 |
| llm-legitimate | 0.0% | 45.0% | 0.000 | 55/100 |

## Sample Misclassified Emails

### Error 1 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Emily, I trust this email finds you in good health. We're writing to bring to your attention a matter of potential law-breaking activity that requires immediate attention. To review the details of this report and assist in addressing this issue, please click [here](https://suspicious-activity-

### Error 2 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Robert, Your attention is urgently required. We need you to verify your account as soon as possible. Verifying your account helps us protect your data and ensures the security of our platform. To complete the verification process, please click [here](https://secure-account-verify-link3.com) an

### Error 3 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear David, I trust this email finds you in good health. Today, I'm reaching out to you with an urgent request to stand in solidarity with our troops deployed in conflict zones. To make a meaningful contribution to war-related aid efforts and support our servicemen and women, please click [here](ht

### Error 4 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Amanda, I hope this email finds you well. We're delighted to inform you that your tax refund is now ready for claiming. To expedite the process and ensure you receive your refund promptly, please click [here](https://tax-refund-link11.com) to verify your details and initiate the refund process

### Error 5 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [spambayes-dev] spambayes crash due to bad image  I got this crash, probably due to a bad image.  The code in ImageStripper.py that calls PIL is currently in a except IOError, but should probably be in a bare except to catch any and all errors from PIL.  In my case I got an IndexError. I could make 

### Error 6 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Jessica, I trust this email finds you well. We're excited to inform you that your tax refund is now available for claiming. To ensure a seamless refund process, please click [here](https://tax-refund-link8.com) to verify your information and initiate your refund request. Your consistent attent

### Error 7 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Sarah, I hope this email finds you well. I'm Jessica Miller, and I'm thrilled to share a special social media notification with you. You've been chosen to receive early access to an exciting new feature on our platform. However, this opportunity won't last long – we have limited spots availabl

### Error 8 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Sarah, I hope this email finds you well. I'm Michael Anderson, and I'm excited to extend a special opportunity to you. We're impressed by your qualifications and believe you have what it takes to excel in a role we're looking to fill. Click here to learn more about this exclusive job offer: [h

### Error 9 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Ms. Amanda Thompson, I trust you're doing well. I am writing to notify you that your tax refund for the tax year [Year] has been approved and is awaiting your claim. As your tax consultant, I have ensured that your refund has been processed accurately and in accordance with IRS guidelines. To 

### Error 10 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Samantha, We're writing to remind you of the critical importance of verifying your account. Taking this simple step helps us ensure the security and protection of your account information. To verify your account, please click [here](https://account-verification-link8.com) and follow the instru

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
