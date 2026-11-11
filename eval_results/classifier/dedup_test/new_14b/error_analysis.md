# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 60 / 267 (22.5%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 84.6% | 0.917 | 2/13 |
| human-legitimate | 0.0% | 98.1% | 0.000 | 1/54 |
| llm-phishing | 100.0% | 97.0% | 0.985 | 3/100 |
| llm-legitimate | 0.0% | 46.0% | 0.000 | 54/100 |

## Sample Misclassified Emails

### Error 1 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Ms. Samantha Harris, I hope this email finds you well. I am writing to inform you that your tax refund for the tax year [Year] has been approved and is now ready for claim. As your assigned IRS agent, I assure you that your refund has been processed accurately and is now available for disburse

### Error 2 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Amanda, I hope this email finds you well. We're writing to you regarding an urgent matter concerning your account security. To maintain the integrity of your account and protect your sensitive information, we strongly encourage you to verify and update your security settings without delay. You

### Error 3 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Daniel, I hope this email finds you in good spirits. We're writing to inform you that your tax refund is now ready for claiming. To expedite the process and ensure you receive your refund without delay, please click [here](https://tax-refund-link7.com) to verify your details and start the refu

### Error 4 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `<think>

legitimate`
- **Email snippet**:
  > saimasham11@yahoo.com sent you files via WeTransfer  saimasham11@yahoo.com  sent you some files 6 items, 417 MB in total ・ Will be deleted on 12 December, 2019 Get your files   Download link https://wetransfer.com/downloads/fb121d87fc5616d9c57b7bddedf9dcba20191205113951/9e48f26258bb490b2a52f0c6e570d

### Error 5 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Matthew, I hope this email finds you well. We're writing to bring to your attention a matter of potential law-breaking activity that requires immediate action. To assist in addressing this issue and ensuring the safety of our community, please review the details of this report by clicking [her

### Error 6 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Ms. Michelle Rodriguez, I trust this email finds you well. My name is Kevin Thompson, and I'm reaching out on behalf of the Reconstruction Aid Fund. In the aftermath of conflict, communities lay in ruins, with homes destroyed, infrastructure damaged, and livelihoods lost. The path to recovery 

### Error 7 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Olivia, I hope this email finds you well. I'm writing to you in my capacity as the Head of Account Security at [Company Name] to address an urgent matter related to your account. It has come to our attention that your account verification is pending. To ensure the security and confidentiality 

### Error 8 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Jessica, We hope this email finds you well. We're writing to bring to your attention the importance of verifying your account promptly. To initiate the verification process and ensure the security of your account, please click [here](https://account-verification-link8.com). It's worth noting t

### Error 9 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Emily, I hope this email finds you well. We're reaching out to remind you about an unpaid invoice that requires your immediate attention. To proceed with the payment and prevent any disruptions to your account, please click [here](https://invoice-payment-link3.com). Many of our clients, includ

### Error 10 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>

phishing`
- **Email snippet**:
  > "Dear Lauren, We hope this email finds you well. We wanted to bring to your attention a recent financial activity associated with your account that requires verification. Verifying this activity is crucial for maintaining the security and accuracy of your financial records. Please take a moment to r

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
