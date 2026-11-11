# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 20 / 244 (8.2%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 83.3% | 0.909 | 1/6 |
| human-legitimate | 0.0% | 63.2% | 0.000 | 14/38 |
| llm-phishing | 100.0% | 99.0% | 0.995 | 1/100 |
| llm-legitimate | 0.0% | 96.0% | 0.000 | 4/100 |

## Sample Misclassified Emails

### Error 1 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > "Dear Robert, Your attention is urgently required. We need you to verify your account as soon as possible. Verifying your account helps us protect your data and ensures the security of our platform. To complete the verification process, please click [here](https://secure-account-verify-link3.com) an

### Error 2 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > First Steps to Unified Communications and More     Webcast Alert            February 08, 2008  Published by   SearchNetworking.com                 Webcast Alert                           WEBCAST ROUNDUP           Dear SearchNetwork

### Error 3 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [spambayes-dev] spambayes crash due to bad image  I got this crash, probably due to a bad image.  The code in ImageStripper.py that calls PIL is currently in a except IOError, but should probably be in a bare except to catch any and all errors from PIL.  In my case I got an IndexError. I could make 

### Error 4 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: hardware options  -----BEGIN PGP SIGNED MESSAGE----- Hash: SHA1  On Thu, Jul 05, 2007 at 07:40:52PM -0400, Cody Hurst wrote: > the only thing I > didn't quite get is that the CD rom drive is on its side....hmmmm > wouldn't it fall out when trying to put one in? >   No. Those kinds of dr

### Error 5 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > "Dear Samantha, We're writing to remind you of the critical importance of verifying your account. Taking this simple step helps us ensure the security and protection of your account information. To verify your account, please click [here](https://account-verification-link8.com) and follow the instru

### Error 6 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [opensuse] openSuSe 10.3 hangs after kernel update  Thanks Jan for all your god suggestions!  While I did not have a live DVD of 10.3 on hand, I did have the regular install DVD. Since I had a "spare" partition on my harddisk, I just installed a new fresh 10.3 on that then mounted my origina

### Error 7 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > "Dear Amanda, We hope you're doing well. We wanted to remind you about the importance of protecting your account from unauthorized access. Your account security is our top priority, and we're here to assist you in keeping it safe. To review and update your security settings, please click [here](http

### Error 8 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [Spambayes-checkins] spambayes/scripts sb_server.py,1.51,1.52  Update of /cvsroot/spambayes/spambayes/scripts In directory sc8-pr-cvs8.sourceforge.net:/tmp/cvs-serv30139/scripts  Modified Files: 	sb_server.py  Log Message: Assign None to a Message instance's message_info_db  Index: sb_server

### Error 9 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `<think>

</think>

legitimate`
- **Email snippet**:
  > Tired Of Searching For Love In All The Wrong Places?  date.net - html letter

### Error 10 (llm-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > "Dear Emily, We hope you're doing well. We wanted to emphasize the importance of strengthening your account security. Your account contains sensitive information, and taking proactive steps to enhance security is crucial. To review and update your security settings, please click [here](https://accou

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
