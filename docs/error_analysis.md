# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 45 / 400 (11.2%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 94.0% | 0.969 | 6/100 |
| human-legitimate | 0.0% | 62.0% | 0.000 | 38/100 |
| llm-phishing | 100.0% | 100.0% | 1.000 | 0/100 |
| llm-legitimate | 0.0% | 99.0% | 0.000 | 1/100 |

## Sample Misclassified Emails

### Error 1 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Science CiteTrack: Editors' Choice: Highlights of the recent literature     Science Online Editors' Choice Alert: 319 (5864)           - - - - - miRNAs and Cancer Webinar brought to you by  Science - - - - -  Join us February 20, 2008, at 12 noon Eastern Standard Time (9am  PST, 5pm

### Error 2 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [UAI] phd and postdoc postion at SNN Nijmegen  PhD student and postdoc position available at SNN Nijmegen.  SNN Nijmegen is a research group dedicated to fundamental research in the areas of machine learning and computational neuroscience. Specific topics are Bayesian networks, approximate infer

### Error 3 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [SM-USERS] SM 1.4.13 Configuration Question: Mail Domain	Parameter  On 2/7/08, Nancy Graziano  wrote: > Good Evening, > > I have tried setting the Mail Domain parameter  Please be more specific.  > to our family's domain name > (my husband and I are the only ones accessing mail through o

### Error 4 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `<think>

legitimate`
- **Email snippet**:
  > =?UTF-8?B?TmV0ZmxpeCBBbGVydDpQbGVhc2UgQ29uZmlybSBZb3VyIFtOZXRmbGl4XSBQcm9maWxlLg==?=  Dear Customer  Netflix Account Closure! -  09/05/2020   Your profile has been listed for deactivation due to incomplete account update.  To continue using your account Click the button below to validate your detail

### Error 5 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [Python-Dev] Python-Dev Summary Draft (April 1-15, 2007)  On 4/24/07, Talin  wrote: > Calvin Spealman wrote: > > I have not gotten any replies about this. No comments, suggestions for > > not skipping any missed threads, or corrections. Is everyone good with > > this or should I give it anot

### Error 6 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Library of Congress Classification Weekly List 31, 2008  Library of Congress Classification Weekly List 31, 2008 [ http://classificationweb.net/approved/0831.html ]  List of new or revised Library of Congress Classification numbers and captions approved by the Cataloging Policy and Support Office 

### Error 7 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [Bug 4104] Several useful URI rules  http://issues.apache.org/SpamAssassin/show_bug.cgi?id=4104   user7@gvc.ceas-challenge.cc changed:             What    |Removed                     |Added ----------------------------------------------------------------------------              Status|ASSIG

### Error 8 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: Virtual Config Dir Problem   HI, i've the same problem...if you have solved this please contact me!! Bye Upr.   Jeferson Pessoa Santana wrote: >  > Hi folks, >  > I have a MX running SpamAssassin and Exim that sends e-mails for another  > server runnning  Exim where is configurated the

### Error 9 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [UAI] CP 2004 Call for Participation  [Sorry this is going out late - I was out of town... BDA]  Dear Colleague,  As co-chairs of CP 2004, to be held in Toronto, September 27 - October 1, 2004, we would like extend an invitation to you to participate in the conference.  Important date: ***Tod

### Error 10 (human-phishing)
- **True label**: `phishing`
- **Predicted**: `legitimate`
- **Model output**: `<think>

</think>

legitimate`
- **Email snippet**:
  > We're having some trouble with your current billing information   NETFLIX Dear Customer, We're having some trouble with your current billing information. We'll try again, but in the meantime you may want to update your payment details.                                                  UPDATE YOUR DET

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
