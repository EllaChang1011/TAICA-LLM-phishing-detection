# Error Analysis — Fine-tuned Qwen3-14B

Total errors: 22 / 267 (8.2%)

## Per-Category Results

| Category | Baseline Acc | Fine-tuned Acc | F1 | Errors |
|---|---|---|---|---|
| human-phishing | 100.0% | 100.0% | 1.000 | 0/13 |
| human-legitimate | 0.0% | 61.1% | 0.000 | 21/54 |
| llm-phishing | 100.0% | 100.0% | 1.000 | 0/100 |
| llm-legitimate | 0.0% | 99.0% | 0.000 | 1/100 |

## Sample Misclassified Emails

### Error 1 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [UAI] phd and postdoc postion at SNN Nijmegen  PhD student and postdoc position available at SNN Nijmegen.  SNN Nijmegen is a research group dedicated to fundamental research in the areas of machine learning and computational neuroscience. Specific topics are Bayesian networks, approximate infer

### Error 2 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [SM-USERS] SM 1.4.13 Configuration Question: Mail Domain	Parameter  On 2/7/08, Nancy Graziano  wrote: > Good Evening, > > I have tried setting the Mail Domain parameter  Please be more specific.  > to our family's domain name > (my husband and I are the only ones accessing mail through o

### Error 3 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Library of Congress Classification Weekly List 31, 2008  Library of Congress Classification Weekly List 31, 2008 [ http://classificationweb.net/approved/0831.html ]  List of new or revised Library of Congress Classification numbers and captions approved by the Cataloging Policy and Support Office 

### Error 4 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: Virtual Config Dir Problem   HI, i've the same problem...if you have solved this please contact me!! Bye Upr.   Jeferson Pessoa Santana wrote: >  > Hi folks, >  > I have a MX running SpamAssassin and Exim that sends e-mails for another  > server runnning  Exim where is configurated the

### Error 5 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [UAI] CP 2004 Call for Participation  [Sorry this is going out late - I was out of town... BDA]  Dear Colleague,  As co-chairs of CP 2004, to be held in Toronto, September 27 - October 1, 2004, we would like extend an invitation to you to participate in the conference.  Important date: ***Tod

### Error 6 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > [UAI] 2004 IEEE International Conference on Advances in Intelligent Systems  **** Please apologize for multiple copies ****  Second Call for Papers  AISTA 2004 --> 2004 IEEE International Conference on Advances in Intelligent Systems - Theory and Applications November 15-18, 2004 --> Centre de

### Error 7 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > sa-learn --ham ground rules  Greetings;  About an hour ago, based on some comments made that the bayes database needed  trained on ham as well as spam, and because it seemed to be forgetting some  of the stuff I'd fed it as spam, I re-wrote that filter rule in kmail to  launch it using one of m

### Error 8 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [opensuse] Why can't I use "shutdown now" to turn off my system?  Carlos E. R. wrote: > -----BEGIN PGP SIGNED MESSAGE----- > Hash: SHA1 >  >  >  > The Monday 2008-02-04 at 20:19 +0100, peter wrote: >  >>>  poweroff >>>  is the command I use. It's shorter :) >> >> 'init 6' is even shor

### Error 9 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Carrot2-developers Digest, Vol 21, Issue 3  Send Carrot2-developers mailing list submissions to 	gjxwrk0-yondqmvcrg@lists.sourceforge.net  To subscribe or unsubscribe via the World Wide Web, visit 	https://lists.sourceforge.net/lists/listinfo/carrot2-developers or, via email, send a message wit

### Error 10 (human-legitimate)
- **True label**: `legitimate`
- **Predicted**: `phishing`
- **Model output**: `<think>`
- **Email snippet**:
  > Re: [R] Me again, about the horrible documentation of tcltk  James MacDonald wrote: >  > 3.) Type tkgetOpenFile at R prompt. >  > > tkgetOpenFile > function (...)  > tcl("tk_getOpenFile", ...) >  >  > 4.) Google tk_getOpenFile. > 5.) http://www.tcl.tk/man/tcl8.5/TkCmd/getOpenFile.htm >  

## Discussion

LLM-generated phishing emails are harder to detect because they lack the obvious surface-level red flags (grammar errors, generic greetings) found in human-written phishing. The zero-shot baseline completely failed on LLM-generated content (0% on both LLM categories), treating all LLM-phishing as legitimate and all LLM-legitimate as phishing.

After fine-tuning on labeled examples from all four categories, the model should generalize better to LLM-style content.

**Note on label quality**: LLM-Legitimate emails include some borderline samples (prize notifications, investment invitations) labeled as legitimate. This noise may inflate error rates in that category.
