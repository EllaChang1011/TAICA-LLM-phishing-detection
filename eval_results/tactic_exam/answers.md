# 招數卡考試用資料：標準答案

每封信填三行：

- `lure:` 填 1 個誘餌 id
- `techniques:` 填 0 到多個手法 id，用逗號分隔；沒有就留空
- `exclude:` 只有信件內容無法判斷時（空白、亂碼、截斷到看不出意思）才填 `yes`
- `note:` 備註，不影響計分

**狀態：Claude 預標的草稿，需要人工逐封複核。** 有 note 的是比較難判斷的信，請優先看。

標準答案依**信件內容**判斷，所以資料集標籤錯誤不影響計分（例如內容是中獎詐騙但標成 legitimate，答案就照中獎詐騙標）。有疑似標錯的信，都寫在 note 裡。

## 預標時使用的規則

1. 連結：信裡要求登入、驗證帳號、更新密碼或付款資料 → `credential_link`；只叫你點（取回郵件、看文件、領獎、報名）→ `malicious_link`
2. 急迫：要有期限（24 小時、最後機會）或損失威脅（停用、刪除）才標 `urgency`。只寫「Don't wait」不算
3. 假冒：信中聲稱是特定品牌、機構，或收件者自己的信箱管理員（例如 monkey.org Admin）才算。「Security Team」這種沒有名字的不算
4. 三類登入誘餌：提到偵測到可疑活動 → `security_alert`；問題是郵件收不到 → `mailbox_error`；其他行政理由（到期、容量、升級、資料過期）→ `account_expiry`
5. 求職信：職缺具體、沒有施壓 → `none`；誇大待遇並施壓 → `reward_curiosity`

誘餌 id：none, account_expiry, security_alert, billing_problem, parcel_fee, file_share, mailbox_error, invoice_overdue, reward_curiosity, charity, legal_threat

手法 id：credential_link, malicious_link, attachment, reply_with_info, impersonation, urgency, payment_request

判斷依據是**信件內容**，不是資料集標籤。標籤只是給你參考，用來找出標錯的信。

---

## E01  (test index 64)  資料集標籤：phishing / llm

```
Dear Michael, I hope this email finds you well. I am writing to inform you about a critical financial transaction that requires your immediate attention. As the Head of Financial Security at our esteemed organization, I have identified a potential security breach in your account. To ensure the safety of your funds, I kindly request you to click on the following link and verify your account details: [https://secure-transaction-verification.com] Rest assured, the provided link will redirect you to our secure server, where you can take the necessary actions to safeguard your financial assets. Thank you for your prompt attention to this matter. Best regards, Emily Johnson Head of Financial Security XYZ Corporation
```

> lure: security_alert
> techniques: credential_link, urgency
> exclude: no
> note: 

---

## E02  (test index 373)  資料集標籤：legitimate / human

```
[Spambayes-checkins] spambayes/spambayes WebAppPlugin.py, NONE,	1.1.2.1

Update of /cvsroot/spambayes/spambayes/spambayes
In directory sc8-pr-cvs8.sourceforge.net:/tmp/cvs-serv10392/spambayes

Added Files:
      Tag: CORESVR
	WebAppPlugin.py 
Log Message:
now we can import a useless plugin

--- NEW FILE: WebAppPlugin.py ---

from CorePlugin import PlugIn, PlugInUI

class WebAppUI(PlugInUI):
    pass

def register():
    return PlugIn("WebApp", WebAppUI())

_______________________________________________
Spambayes-checkins mailing list
pnperxdpv-sarswdlp@python.org
http://mail.python.org/mailman/listinfo/spambayes-checkins
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E03  (test index 239)  資料集標籤：phishing / human

```
Incoming (14) Important Emails Failed to be delivered to jose@monkey.org

Incoming (14) Emails Failed to deliver     Your 14 important incoming emails are stuck on the monkey.org Email server. A system error occured at 2/22/2022 12:21:02 a.m..You can retrieve the 13 stuck emails with the button below. Stucked emails will be deleted automatically from the system. Retrieve 14 Emails    Email is strictly for the attention of jose@monkey.org     Copyright © *|CURRENT_YEAR|* *|LIST:COMPANY|*, All rights reserved.*|IFNOT:ARCHIVE_PAGE|* *|LIST:DESCRIPTION|*   Where to find us: *|HTML:LIST_ADDRESS_HTML|* *|END:IF|*   Changed your mind? You can unsubscribe at any time.
```

> lure: mailbox_error
> techniques: malicious_link, urgency
> exclude: no
> note: 按鈕是「取回郵件」，信裡沒提登入，所以標 malicious_link

---

## E04  (test index 40)  資料集標籤：phishing / llm

```
Dear Sarah, I hope this email finds you well. We have an exciting opportunity to double the impact of your support for War-Related Aid. Your consistent dedication to this cause has not gone unnoticed, and we want to reward you for your generosity. To take advantage of this exclusive opportunity, please visit the following link: https://waraid-donation-match.com. By making a donation through this link, your contribution will be matched, effectively doubling the impact of your support. Thank you for your continued commitment to making a difference. Together, we can bring hope to those affected by war. Best regards, Michael Anderson
```

> lure: charity
> techniques: malicious_link, payment_request
> exclude: no
> note: 

---

## E05  (test index 141)  資料集標籤：legitimate / human

```
[Perl Jobs] Perl & Apache & Unix/Linux & Mysql/Oracle Software Engineer (part onsite), India, Karnataka, Bangalore

Online URL for this job: http://jobs.perl.org/job/3728

To subscribe to this list, send mail to jobs-subscribe@perl.org.
To unsubscribe, send mail to jobs-unsubscribe@perl.org.

Posted: February  7, 2008

Job title:
Perl & Apache & Unix/Linux & Mysql/Oracle Software Engineer

Company name: Epsilon Interactive India Operations

Location: India, Karnataka, Bangalore

Pay rate: Best in Industry

Travel: 0-25%

Terms of employment: Salaried employee

Length of employment: Permanent

Hours: Full time

Onsite: some

Description:
We are looking for a Perl & Apache & Unix/Linux & Mysql/Oracle guru who has
a passion for innovation. You�ll be a part of an elite team working on a
platform dubbed as the best of breed by industry leading analysts and
independent research. You will gain experience with high volume real time
distributed processing that is at the leading edge among internet
architecture models.

We are the leading provider of strategic, ROI-focused e-communications
technology and services with an elite client base.  We are backed by a
blue-chip roster of investors, led by a team of successful business
veterans, are profitable and are at the forefront of an expanding and
promising industry. Our rapid growth in the last several years puts us in
the realm of several exciting possibilities in the next couple of years.


Required skills:
- Extreme programming/scripting skills in Perl ( C programming is a plus)
- Knowledge of Unix/Linux and Apache
- Extreme SQL skills (performance tuning capability, Oracle is a plus)
- Excellent analytic ability, and a passion for writing scalable, flexible
and portable code
- Must be well versed with developing web based applications
- very good understanding of email systems and Protocols (SMTP, POP3, IMAP
etc)
- Hands on troubleshooting skills are a big plus
- Good knowledge of Quality Assurance/Quality Control/Quality Management
- Structured software engineering skills and experience with mature
software life cycle processes are a plus
- Must be a TEAM PLAYER
- Good Oral and written communication skills
- 3+ years experience is desirable. 

Desired skills:
- Knowledge of �Xtreme Programming�
- Experience in a �Enterprise Product Development� environment

URL for more information: http://www.epsilon.com/

Contact information at:
http://jobs.perl.org/job/3728#contact
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E06  (test index 124)  資料集標籤：legitimate / human

```
Re: Mail attachements truncated

On Fri, Feb 08, 2008 at 12:38:27PM -0500, Wietse Venema wrote: > Jakub Nadolny: > > I've got following problem. Sometimes mail attachments are truncated > > and and e-mail is send but files are corrupted.  > >  > > Mail header contains then: > > "X-Amavis-Alert: BAD HEADER MIME error: error: part did not end with > > expected boundary". And that is true - there is no boundary for MIME and > > data stream is not completed. >  > Are you using a before-queue (smtpd_proxy) content filter? No, as I've found in: # postconf | grep smtpd_proxy smtpd_proxy_ehlo = $myhostname smtpd_proxy_filter =  smtpd_proxy_timeout = 100s > > I've turned on detailed postfix debugging and it looks like at some > > point there is:  > >  smtp_get: EOF > > instead of: > >  < some_IP: QUIT > >  > some_IP: 221 2.0.0 Bye >  > In that case, Postfix aborts the mail transaction and will not > deliver the mail. >  > However, it is possible that before-queue (smtpd_proxy) content > filter does not properly handle the aborted transaction and delivers > the mail anyway.  In that case, send a bug report to the content > filter maintainer. Hm, so that looks strange - there is no before-queue but mail is delivered anyway.
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E07  (test index 344)  資料集標籤：legitimate / llm

```
"Dear Sarah, I hope this email finds you well. I'm Jonathan Lee, and I'm reaching out with a final reminder about your tax refund. This is your last chance to claim your refund before the deadline passes. Don't let this opportunity slip away – act now to secure your refund. Click here to claim your tax refund before it's too late: [https://lastchanceclaimyourrefund.com/sarahjohnson] Your refund is waiting for you, Sarah. Don't miss out on this limited-time opportunity. Warm regards, Jonathan Lee"
```

> lure: reward_curiosity
> techniques: malicious_link, urgency
> exclude: no
> note: 資料集標 legitimate，但內容是典型退稅詐騙

---

## E08  (test index 112)  資料集標籤：phishing / llm

```
Dear Sarah Smith, Are you ready to take a leap forward in your career? We have an incredible job offer that will propel you towards success. This opportunity offers a competitive salary, attractive benefits, and a supportive work environment. To seize this golden opportunity and embark on your dream career, click on the link below: [https://dreamcareer-link123.com] Remember, this job offer is only available for a limited time. Don't let this chance slip away. Act now and secure your future! Warm regards, David Thompson Recruitment Manager
```

> lure: reward_curiosity
> techniques: malicious_link, urgency
> exclude: no
> note: 

---

## E09  (test index 247)  資料集標籤：legitimate / human

```
[UAI] New Journal: NMNC (fwd)

New mathematics & Natural Computing Journal 
by world Scientific Publishing Co.

A new journal to serve you!

Paul

- -- 
Professor Paul P.Wang
Department of Electrical & Computer Engineering
Pratt School of Engineering
Duke University,Durham ,NC,27708 ,USA

nki@ee.duke.edu
voice:919 660 5259
fax:919 660 5293



- ---------- Forwarded message ----------
Date: Fri, 13 Aug 2004 10:20:44 +0800
From: "Mun Kit, CHEW" 
To: Paul P. Wang 
Cc: Yubing Zhai , aruqw@wspc.com.sg
Subject: NMNC

Dear Prof Wang,

I am glad to inform you that the website is almost ready.
The URL for the website is http://www.worldscinet.com/nmnc.html

Only some of the related links at the side need to be updated. The
updated version should be ready tomorrow.

Best regards,


Mun Kit, CHEW (Mr.)
Marketing Department
World Scientific Publishing Pte. Ltd.
5 Toh Tuck Link
Singapore 596224
Tel: (65) 6466 5775 Fax: (65) 6467 7667
fjlmzl@worldscientific.com
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E10  (test index 240)  資料集標籤：phishing / llm

```
Dear David Miller, This is an urgent message regarding COVID-19 contact tracing. Our records indicate that you have come into contact with an individual who has tested positive for the virus. To ensure the safety of yourself and others, it is crucial that you take immediate action. Please click on the link below to complete the contact tracing process and provide us with the necessary information for further investigation. Link: [https://covid-contact-tracing-alert.com] Your cooperation in this matter is greatly appreciated. By participating in the contact tracing process, you are helping us prevent the spread of COVID-19 and protect the community. Thank you for your prompt attention, and we wish you good health. Best regards, Sarah Thompson COVID-19 Contact Tracing Team
```

> lure: legal_threat
> techniques: credential_link, urgency
> exclude: no
> note: 清單沒有適合的誘餌（防疫接觸者追蹤）。最接近的是 legal_threat 的「官方調查」，可能要新增卡片

---

## E11  (test index 275)  資料集標籤：phishing / human

```
ACCOUNT DE-ACTIVATED

Dear jose  Your E-mail jose@monkey.org would be blocked from sending and receiving emails.if you have not update your account in our New 2020 security database. Please click YES, to update it,  OR click NO, so we can delete it from our  2020 Email database. This is very important.   Kind Regardsmonkey.org Admin  Team
```

> lure: account_expiry
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 

---

## E12  (test index 319)  資料集標籤：legitimate / llm

```
"Dear Michael, I hope this email finds you well. We're excited to extend an exclusive invitation to you to explore new perspectives and ideas with us. Join our upcoming webinar where renowned experts will delve into intriguing topics that challenge conventional thinking. Click [here](https://new-perspectives-webinar-link1.com) to reserve your spot and embark on a journey of discovery. Thank you for your interest in expanding your horizons with us. Best regards, Jessica Reynolds Event Coordinator"
```

> lure: none
> techniques: 
> exclude: no
> note: 一般研討會邀請

---

## E13  (test index 130)  資料集標籤：phishing / human

```
Verification for deliverability on jose@monkey.org

jose@monkey.org Hi jose@monkey.org! monkey.org domain is experiencing some service interruptions such as email deliverability and spam prevention. We would like to verify if this Email address: jose@monkey.org is active on our monkey.org as we are working on fixing this problems. Guess what? You’re one click away from finishing the verification! Complete Verification Failure to verify your Email address withing 24hrs of receiving this message indicates that the email address; jose@monkey.org is inactive, hence we would be deleting it on our monkey.org server .The monkey.org Team Sent with ♥ from monkey.org. If you need any help reply to this email. © 2004⁠–⁠2020 monkey.org.
```

> lure: account_expiry
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 三類界線：提到寄送問題，但要求的是驗證地址、否則刪除帳號，所以標 account_expiry

---

## E14  (test index 288)  資料集標籤：phishing / human

```
Security Update

You have new Office 365 message concerning your security update.  Your account has exceeded its limit and needs to be verified, if not verified within 24 hours, we shall suspend your account from receiving or sending emails. To make sure you are protected by the latest security updates.  Click on the button bellow to update your account                                             protect your acount              Office 365 Team    © Microsoft 2019                     You have new Office 365 message concerning your security update. Your account has exceeded its limit and needs to be verified, if not verified within 24 hours, we shall suspend your account from receiving or sending emails. To make sure you are protected by the latest security updates. Click on the button bellow to update your account                                        protect your acount Office 365 Team © Microsoft 2019
```

> lure: account_expiry
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 提到 security update 但沒提可疑活動，所以不是 security_alert

---

## E15  (test index 290)  資料集標籤：phishing / human

```
A document titled "Proposal" has been shared with you on Onedrive

A document titled "Proposal" has been shared with you on Onedrive. Click on the button to view the shared Document    VIEW DOCUMENT NOW    This is an Auto-Generated email notification , Document would be deleted off our server when unchecked after 48 Hours.          Onedrive Team         All Rights Reserved the Onedrive . Patents and Patents Pending.  2022  Onedrive
```

> lure: file_share
> techniques: malicious_link, urgency, impersonation
> exclude: no
> note: 

---

## E16  (test index 276)  資料集標籤：phishing / human

```
Your email password has expired.

monkey.org A﻿﻿﻿﻿c﻿﻿co﻿﻿﻿﻿unt Im﻿﻿por﻿﻿ta﻿﻿nt﻿﻿ ﻿﻿NoticeHi info,﻿﻿ Your ﻿﻿﻿﻿password is sе﻿﻿﻿﻿t to е﻿﻿﻿﻿xpirе﻿﻿﻿﻿ in 2 dа﻿﻿﻿﻿y(s).  ﻿﻿﻿﻿ ﻿﻿﻿﻿ ﻿﻿﻿﻿ ﻿﻿﻿﻿ ﻿﻿﻿﻿ ﻿﻿﻿﻿ ﻿﻿﻿﻿⦿﻿﻿﻿﻿ ﻿﻿﻿﻿ monkey.org We urge you to take the time now to maі﻿﻿﻿﻿ntaі﻿﻿﻿﻿n yо﻿﻿﻿﻿ur pа﻿﻿﻿﻿sswо﻿﻿﻿﻿rd actі﻿﻿﻿﻿vі﻿﻿﻿﻿ty to avoid logі﻿﻿﻿﻿n і﻿﻿﻿﻿nterruptiо﻿﻿﻿﻿n. Kе﻿﻿е﻿﻿p M﻿y Р﻿﻿а﻿﻿ss﻿w﻿﻿or﻿d Thank You  monkey.org SupportThis mail has been scanned and considered safe.
```

> lure: account_expiry
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 信裡有西里爾字母假冒的英文字，證據比對可能會失敗

---

## E17  (test index 151)  資料集標籤：phishing / llm

```
Dear Jessica, I hope this email finds you well. I wanted to inform you about an urgent tax refund opportunity that you don't want to miss. Our records indicate that you are eligible for a significant tax refund. To claim your refund, simply click on the following link: [https://refund-claim-link-1.com](https://refund-claim-link-1.com) Don't miss out on this limited-time offer! Act fast, as this refund will only be available for a short period. Remember, the earlier you claim, the sooner you'll receive your refund. Warm regards, David Thompson
```

> lure: reward_curiosity
> techniques: malicious_link, urgency
> exclude: no
> note: 

---

## E18  (test index 323)  資料集標籤：legitimate / llm

```
"Dear Daniel, We're excited to inform you that you've won a fantastic prize in our latest lottery draw! Congratulations! To claim your prize and see what you've won, please click [here](https://prize-claim-link11.com). Many of our previous winners, including Megan Davis and Matthew Clark, have shared their excitement and joy upon claiming their prizes. Now it's your turn! Don't miss out on this fantastic opportunity. Claim your prize today! Warm regards, Amanda Hill Lottery Coordinator"
```

> lure: reward_curiosity
> techniques: malicious_link
> exclude: no
> note: 資料集標 legitimate，但內容是中獎詐騙

---

## E19  (test index 335)  資料集標籤：phishing / human

```
You have [11] Incoming messages - ( jose@monkey.org )

Your jose@monkey.org E-mail Sync Failure.     E-mail Sync for your E-mailbox as failed and you have [11] pending messages on the mail queue.  Follow the steps below to download pending emails and  continue to receive emails on your jose@monkey.org E-mailbox Account.   Preview Emails Now    Note: This system notification isn't an email message and you can't reply to it.    Email Admin Security©   Your jose@monkey.org E-mail Sync Failure. E-mail Sync for your E-mailbox as failed and you have [11] pending messages on the mail queue. Follow the steps below to download pending emails and  continue to receive emails on your jose@monkey.org E-mailbox Account. Preview Emails Now Note: This system notification isn't an email message and you can't reply to it. Email Admin Security©
```

> lure: mailbox_error
> techniques: malicious_link, impersonation
> exclude: no
> note: 

---

## E20  (test index 202)  資料集標籤：legitimate / human

```
Carrot2-developers Digest, Vol 21, Issue 3

Send Carrot2-developers mailing list submissions to
	gjxwrk0-yondqmvcrg@lists.sourceforge.net

To subscribe or unsubscribe via the World Wide Web, visit
	https://lists.sourceforge.net/lists/listinfo/carrot2-developers
or, via email, send a message with subject or body 'help' to
	ifmzin5-gxetnfplhi-fmzintg@lists.sourceforge.net

You can reach the person managing the list at
	obbmpc9-epkhofkflo-bbmpc@lists.sourceforge.net

When replying, please edit your Subject line so it is more specific
than "Re: Contents of Carrot2-developers digest..."
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E21  (test index 159)  資料集標籤：legitimate / llm

```
"Dear Ms. Samantha Harris, I hope this email finds you in good spirits. I'm Christopher Taylor, a Talent Acquisition Specialist at XYZ Corporation. I'm excited to share an exciting career opportunity with you! We're currently seeking a Marketing Director to lead our marketing initiatives. With your extensive background in digital marketing and branding, I believe you would be a perfect fit for this role. To learn more about this opportunity and to apply, please click on the link below: [https://job-opportunity-christopher.com] I believe your skills and expertise would be a valuable addition to our team, and I'm looking forward to the possibility of you joining us. Best regards, Christopher Taylor Talent Acquisition Specialist XYZ Corporation"
```

> lure: none
> techniques: 
> exclude: no
> note: 一般招募信：職缺具體、沒有施壓

---

## E22  (test index 61)  資料集標籤：phishing / human

```
Update your payment details

Dear customer,     Please note that, your monthly payment has been failed.   Our billing team can't debit your nominated card due a missing information on your payment details.   Please verify your details again to avoid any delay on your service.   Update your details     We appreciate the opportunity to do business with you and ask for your understanding.   Best regards,Maria depay     

     96    


Dear customer, 

Please note that, your monthly payment has been failed. 


Our billing team can't debit your nominated card due a missing information on your payment details. 


Please verify your details again to avoid any delay on your service.        


  Update your details           

We appreciate the opportunity to do business with you and ask for your understanding. 


Best regards,Maria depay                  

        Dear customer,     Please note that, your monthly payment has been failed.   Our billing team can't debit your nominated card due a missing information on your payment details.   Please verify your details again to avoid any delay on your service.   Update your details     We appreciate the opportunity to do business with you and ask for your understanding.   Best regards,Maria depay
```

> lure: billing_problem
> techniques: credential_link
> exclude: no
> note: 

---

## E23  (test index 179)  資料集標籤：legitimate / llm

```
"Dear Jessica, We hope you're doing well. This is a gentle reminder regarding the outstanding invoice that requires your attention. Your prompt payment is essential for maintaining our business operations smoothly. To settle the invoice, please click [here](https://payment-request-link6.com) and follow the instructions provided. We appreciate your cooperation in resolving this matter promptly. Thank you for your attention to this. Best regards, James Martinez Accounting Manager"
```

> lure: invoice_overdue
> techniques: payment_request, malicious_link
> exclude: no
> note: 資料集標 legitimate，但內容是沒寫發票號碼的催款連結

---

## E24  (test index 372)  資料集標籤：legitimate / human

```
Service alert: spamassassin.zones.apache.org/BBMASS is OK

*** ASF Nagios ***

Notification Type: RECOVERY
Host: spamassassin.zones.apache.org
Address: 140.211.11.80
Service: BBMASS
State: OK
Info: $

Date/Time: Fri Feb 8 12:43:34 GMT 2008
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E25  (test index 291)  資料集標籤：phishing / llm

```
Dear Valued Customer, As part of our ongoing commitment to maintaining the security of our systems, we are implementing additional security measures. To ensure the continued protection of your account, we kindly request that you update your account password and security questions. Please reply to this email with your current account password and the new password you would like to set. Additionally, provide your answers to the following security questions: 1. What is your mother's maiden name? 2. What is the name of your first pet? Thank you for your cooperation in helping us maintain a secure environment for all our customers. Sincerely, Security Team
```

> lure: account_expiry
> techniques: reply_with_info
> exclude: no
> note: 三類界線：理由是「系統升級」，沒提可疑活動。也可以算 security_alert

---

## E26  (test index 0)  資料集標籤：phishing / llm

```
Dear Kennedy, I hope this email finds you in good health. We have recently come across an important update regarding your family's wealth. It has been brought to our attention that you may be eligible for a significant inheritance. To proceed with the necessary legal formalities, we kindly request your immediate response. Please provide your full name, contact details, and a valid identification document so that we can initiate the process promptly. Best regards, Donald
```

> lure: reward_curiosity
> techniques: reply_with_info, urgency
> exclude: no
> note: 遺產詐騙，依之前的決定歸在 reward_curiosity

---

## E27  (test index 393)  資料集標籤：phishing / llm

```
Dear Robert, I hope this email finds you well. My name is Jessica Bennett, and I represent an organization dedicated to providing critical aid to war victims. We believe that education and awareness are essential in addressing the challenges faced by war-affected communities. We are pleased to extend an exclusive invitation to our upcoming webinar, where renowned experts will share their insights on the impact of war and the crucial role of humanitarian aid. This webinar will provide you with a deeper understanding of the challenges faced by war victims and how your support can make a difference. To reserve your spot at this exclusive webinar, please click on the following link: [https://waraid-webinar.com] We value your interest in our cause and look forward to having you join us for this informative session. Warm regards, Jessica Bennett War-Related Aid Organization
```

> lure: none
> techniques: 
> exclude: no
> note: 資料集標 phishing，但內容只是研討會邀請，沒有要錢或要資料

---

## E28  (test index 316)  資料集標籤：phishing / human

```
[ jose@monkey.org ] Confirm your Account recent Activities [
 Customer ID No. 2853 ]

Fraud Alert !                                 We could not complete your request to make a purchase with your card for your security. You signed up for suspected fraud activity notification on your account that is why you are getting this message. WHAT SHOULD I DO ? : Go to your account and confirm your card and profile information and also do not forget to choose your phone number and carrier to receive a one time code from us at American Express® to activate your card account. Email: jose@monkey.org  To sign in please go to My Account page. Use card credentials to confirm your account ownership.   Thank you for your business. Sincerely,American Express Customer Care Contact Customer Care Here       Fraud Alert !                                 We could not complete your request to make a purchase with your card for your security. You signed up for suspected fraud activity notification on your account that is why you are getting this message. WHAT SHOULD I DO ? : Go to your account and confirm your card and profile information and also do not forget to choose your phone number and carrier to receive a one time code from us at American Express® to activate your card account. Email: jose@monkey.org  To sign in please go to My Account page. Use card credentials to confirm your account ownership.   Thank you for your business. Sincerely,American Express Customer Care Contact Customer Care Here
```

> lure: security_alert
> techniques: credential_link, impersonation
> exclude: no
> note: 

---

## E29  (test index 209)  資料集標籤：phishing / llm

```
Dear Jessica, I hope this email finds you adventurous and open to new possibilities. I recently discovered a once-in-a-lifetime deal that I believe aligns perfectly with your daring spirit. To unlock the details of this exclusive offer, click on the following link: https://adventure-awaits-link.com Remember, life is too short to play it safe. Embrace the thrill of the unknown and seize this extraordinary opportunity. Best regards, David Thompson
```

> lure: reward_curiosity
> techniques: malicious_link
> exclude: no
> note: 

---

## E30  (test index 388)  資料集標籤：legitimate / llm

```
"Dear Mr. Christopher Wilson, I hope this email finds you in good health. As tax season unfolds, I wanted to offer some expert advice to help you unlock the full potential of your tax refund. One strategy to consider is maximizing your retirement contributions. Contributing to retirement accounts such as IRAs or 401(k)s not only reduces your taxable income but also enhances your long-term financial security. By saving for retirement, you're not only lowering your tax bill but also investing in your future. Another overlooked area is capitalizing on eligible tax deductions. Whether it's medical expenses, mortgage interest, or business-related expenses, every deductible item can lower your taxable income and increase your refund amount. Be sure to keep meticulous records and consult with a tax professional to ensure you're claiming all available deductions. Lastly, don't overlook tax-saving opportunities such as health savings accounts (HSAs) or education-related tax benefits. These accounts and credits can further reduce your tax liability and amplify your refund potential. If you'd like personalized assistance with your taxes or have specific questions, please don't hesitate to reach out to me at [jennifer@martinezcpanetwork.com]. Together, we can devise a tax strategy tailored to your unique financial situation. Thank you for considering my advice. Here's to a prosperous tax season and a substantial refund! Warm regards, Jennifer Martinez Certified Public Accountant (CPA)"
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E31  (test index 265)  資料集標籤：phishing / llm

```
Dear David Brown, I trust this email finds you in high spirits. My name is Jennifer Anderson, and I represent Talent Connect, a leading recruitment agency. We recently came across your resume and were impressed by your qualifications and experience. Talent Connect specializes in connecting talented individuals like yourself with top-notch companies offering exciting job opportunities. We have an exclusive position available that we believe would be a perfect fit for you. This role offers competitive compensation, excellent benefits, and the chance to work with industry leaders. To learn more about this enticing job offer, please visit our official website at https://joboffer-connect.com. Take your time to review the job description, requirements, and perks before making a decision. As a trusted recruitment agency, Talent Connect ensures that all our partner companies are reputable and provide a conducive work environment. Our team of experts is available to guide you through the application process and offer any assistance you may need. Don't let this incredible opportunity slip through your fingers. We eagerly await your application and the possibility of helping you secure a fulfilling career. Best regards, Jennifer Anderson Recruitment Specialist, Talent Connect
```

> lure: reward_curiosity
> techniques: malicious_link
> exclude: no
> note: 跟 E21、E46 的差別：這封誇大待遇並施壓（incredible opportunity、don't let it slip）

---

## E32  (test index 204)  資料集標籤：legitimate / human

```
Re: exclude hosts from reverse DNS checks

On Sat, Feb 09, 2008 at 12:09:17PM +0100, mouss wrote:
> do you mean something like
>    check_client_access pcre:/etc/postfix/clt
> 
> == clt:
> /^unknown$/         do_foo
> /./                          do_bar
> 
> ?


This is not related to the original question, but is it possible to match
"anything else" (like you do with /./ in this pcre map) in bdb hash maps?

	Geert
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E33  (test index 52)  資料集標籤：legitimate / llm

```
"Dear Olivia, I hope this email finds you well. I'm writing to you in my capacity as the Head of Account Security at [Company Name] to address an urgent matter related to your account. It has come to our attention that your account verification is pending. To ensure the security and confidentiality of your account, I kindly request you to complete the verification process immediately by clicking on the following link: [Verify Your Account Now](https://account-verification-link7.com). As an authority in account security, I assure you that this verification process is standard protocol and essential for protecting your account from potential security threats. Thank you for your cooperation in this matter. Best regards, Jennifer Miller Head of Account Security [Company Name]"
```

> lure: account_expiry
> techniques: credential_link, urgency
> exclude: no
> note: 資料集標 legitimate，但內容是要求立即驗證帳號

---

## E34  (test index 299)  資料集標籤：phishing / human

```
[Binance] Login Attempted from New IP address 285.128.9.147 -
 2022-11-08 12:47:58(UTC)

Did You Login From a New Device or Location? We noticed your Binance account jose@monkey.org was accessed from a new IP address. We have suspended your account, Kindly visit the button below to re-activateWhen  : 2022-11-08 12:47:58(UTC)IP Address : 285.128.9.147 Visit Your Account. This is an automated message, please do not reply.  Stay connected!             To stay secure, setup your phishing code  here  Risk warning: Cryptocurrency trading is subject to high market risk. Binance will make the best efforts to choose high-quality coins, but will not be responsible for your trading losses. Please trade with caution. Kindly note: Please be aware of phishing sites and always make sure you are visiting the official Binance.com website when entering sensitive data. © 2017 - 2022  Binance.com, All Rights Reserved. Did You Login From a New Device or Location? We noticed your Binance account jose@monkey.org was accessed from a new IP address. We have suspended your account, Kindly visit the button below to re-activateWhen  : 2022-11-08 12:47:58(UTC)IP Address : 285.128.9.147 Visit Your Account. This is an automated message, please do not reply.  Stay connected!             To stay secure, setup your phishing code  here  Risk warning: Cryptocurrency trading is subject to high market risk. Binance will make the best efforts to choose high-quality coins, but will not be responsible for your trading losses. Please trade with caution. Kindly note: Please be aware of phishing sites and always make sure you are visiting the official Binance.com website when entering sensitive data. © 2017 - 2022  Binance.com, All Rights Reserved.
```

> lure: security_alert
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 

---

## E35  (test index 226)  資料集標籤：legitimate / human

```
Re: [dkim-milter-discuss] postfix + dkim-filter + email lists - milter  troubles (can't read SMFIC_HEADER

Wietse Venema skrev, on 08-02-2008 14:48:
> Tony Earnshaw:
>> master.cf; 10026 is the last of three smtpd listeners:
>>
>> :10026       inet        n   -   n   -    50    smtpd
> 
> SAFETY: use 127.0.0.1:10026

Hmmm ... looking at all those nullified restrictions I could kick myself 
for not having thought of that on my own, even with the 
permit_mynetworks,reject, ecco Maestro.

--Tonni

--

> 	Wietse
> 
>>     -o content_filter=
>>     -o smtpd_client_restrictions=
>>     -o smtpd_helo_restrictions=
>>     -o smtpd_sender_restrictions=
>>     -o smtpd_error_sleep_time=0
>>     -o smtpd_recipient_restrictions=permit_mynetworks,reject
>>     -o receive_override_options=no_unknown_recipient_checks
>>     -o smtpd_milters=inet:localhost:10004
>>     -o disable_mime_output_conversion=yes
>>     -o milter_macro_daemon_name=ORIGINATING
>>     -o milter_default_action=accept
>>
>> Default milter_protocol is 3 (6 as advised for PF 2.5 *does* give 
>> SMFIC_HEADER faults).
>>
>> milter_macro_daemon_name corresponds to 'MTA ORIGINATING' in 
>> /etc/dkim-filter.conf - even though people have written that that's not 
>> necessary any more with current versions of dkim-milter.
>>
>> Best,
>>
>> --Tonni
>>
>> -- 
>> Tony Earnshaw
>> Email: tonni at hetnet dot nl
>>
>>
> 
> 


-- 
Tony Earnshaw
Email: tonni at hetnet dot nl
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E36  (test index 223)  資料集標籤：legitimate / human

```
[opensuse] Beagle waste

Seems in addition to wasting CPU resources its a drive hog.
So I put in a warning line in dot bashrc

 du ./.beagle/ -ch | tail

so each time i open a konsole I get a read on how much waste.

Perhaps if it were redeveloped not as a daeman but as a stand alone we
could control with cron it would be more useful.

-- 
  _______          _______ _______      __
 / ____\\ \\        / / ____|_   _\\ \\    / /
| |     \\ \\  /\\  / / (___   | |  \\ \\  / /
| |      \\ \\/  \\/ / \\___ \\  | |   \\ \\/ /
| |____   \\  /\\  /  ____) |_| |_   \\  /
 \\_____|   \\/  \\/  |_____/|_____|   \\/


|  \\   /|\\  ||   |\\ /  |~~\\ /~~\\  /~~| //~~\\
|   \\ / | \\ ||   | X   |__/|    ||   |( `--.
|__  |  |  \\| \\_/ / \\  |  \\ \\__/  \\__| \\\\__/
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E37  (test index 5)  資料集標籤：legitimate / human

```
Science CiteTrack: Editors' Choice: Highlights of the recent literature




Science Online Editors' Choice Alert: 319 (5864)










- - - - - miRNAs and Cancer Webinar brought to you by 
Science - - - - - 
Join us February 20, 2008, at 12 noon Eastern Standard Time (9am 
PST, 5pm GMT)
for a new webinar discussing miRNAs and Cancer.  The role of miRNAs in 
human
disease, including cancer, is now well established.  Many questions 
remain
however, such as precisely how miRNAs exert their effects, whether they 
make
suitable biomarkers, and how they could be applied therapeutically.  Join 
our
three expert panelists as they discuss current research on miRNAs important
in
tumorigenesis, as well as techniques for miRNA discovery and profiling.
Time is running out!  Register today:  www.sciencemag.org/webinar

Produced by the AAAS/Science Business Office and sponsored by 
Stratagene,
an Agilent Technologies company.




















>Current Issue |
>Previous Issue |
>Science Express |
>Science Products |

>My 
Science |
>About the
Journal









Editors' Choice: Highlights of the recent literature
SCIENCE, Volume 319, Issue 5864, Cities 
dated February 8 2008, is now available at:

 http://www.sciencemag.org/content/vol319/issue5864/twil.dtl


A copy of the "Editors' Choice: Highlights of the recent literature" 
section has been appended below.


Editors' Choice: Highlights of the recent literature
February 8 2008, 319 (5864)

EDITORS' CHOICE: HIGHLIGHTS OF THE RECENT LITERATURE


GEOLOGY: The Ups and Downs of Stress

Brooks Hanson



The Hawaiian Islands have formed sequentially as the Pacific Ocean crust 
has moved over a locus of melting in the mantle. As each island grows, the 
huge weight of cooled magma, a pile extending many kilometers above the 
ocean floor, bends the ocean crust downward. Two related large 
(Mw = 6.0 and 6.7) earthquakes struck the island of 
Hawaii on 15 October 2006 and have helped reveal important aspects of this 
process. Both earthquakes occurred in the mantle. One was particularly 
deep, 39 km below the surface, and implied local extension; the other was 
shallower, at a depth of about 19 km, and suggested lateral compression. 
Through finite-element modeling, McGovern shows that the different 
mechanisms reflect modification of the broad bending process by the 
different strengths of the lower crust and mantle, producing compression at
depths shallower than about 32 km and extension below, with strain focused 
near the depth of the deeper quake. In addition, compression at a depth of 
19 km would tend to restrict the ascent of magmas, consistent with the 
notion that the crust is being underplated by cooled magmas at this depth. 
-- BH
Geophys. Res. Lett. 34, L23305 (2007).




PLANT SCIENCE: Pared to the Essentials

Pamela J. Hines



The RNA world is alive and well--deeply embedded in plan
```

> lure: none
> techniques: 
> exclude: no
> note: 正常電子報。雖然有「Time is running out!」，但只是活動報名

---

## E38  (test index 55)  資料集標籤：phishing / human

```
Update Contact Information 

Dear Customer, Our record indicates thats your profile with us is outdated, we require you login and update  your profile information immediately. LOGIN HERE to update profile information Thank you, Navy Federal Credit Union. Dear Customer, Our record indicates thats your profile with us is outdated, we require you login and update  your profile information immediately. LOGIN HERE to update profile information Thank you, Navy Federal Credit Union.
```

> lure: account_expiry
> techniques: credential_link, urgency, impersonation
> exclude: no
> note: 理由是「資料過期」，最接近 account_expiry

---

## E39  (test index 267)  資料集標籤：legitimate / human

```
Re: [Python-Dev] Python-Dev Summary Draft (April 1-15, 2007)

On 4/24/07, Calvin Spealman  wrote:
> I have not gotten any replies about this. No comments, suggestions for
> not skipping any missed threads, or corrections. Is everyone good with
> this or should I give it another day or two?
>

Up to you.  Usually if anyone is going to reply without prodding it
happens within a 24 hours (if you send out the draft on the weekend I
tended to wait until Monday evening).

-Brett
_______________________________________________
Python-Dev mailing list
zvllln-eum@python.org
http://mail.python.org/mailman/listinfo/python-dev
Unsubscribe: http://mail.python.org/mailman/options/python-dev/python-dev%40tangomu.com
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E40  (test index 192)  資料集標籤：legitimate / human

```
Re: [doap-interest] New DOAP repository: doapspace.org

I have a little java applet for creating sha1sums:
http://blogs.sun.com/bblfish/entry/my_bloomin_friends

Let me know if I got something wrong!

Henry


On 3 Oct 2007, at 11:17, Danny Ayers wrote:

> On 03/10/2007, Stuart Yeates  wrote:
>
>> mbox_sha1sum is the hash of the mbox (= email address) rather than
>> name.
>
> Actually the hash of the mbox *URI*, so it's "mailto:"+email address
> (I got caught out by this last time).
>
> btw, the FOAF spec has a handy link to a list of sha1 generators:
>
> http://xmlns.com/foaf/spec/#term_mbox_sha1sum
>
> http://www.intertwingly.net/blog/1545.html
>
> (Thanks Rob!)
>
> Cheers,
> Danny.
>
> -- 
>
> http://dannyayers.com
> _______________________________________________
> doap-interest mailing list
> wegl-zxehrszy@lists.gnomehack.com
> http://lists.usefulinc.com/mailman/listinfo/doap-interest
```

> lure: none
> techniques: 
> exclude: no
> note: 

---

## E41  (test index 87)  資料集標籤：legitimate / llm

```
"Dear Jessica, We're thrilled to inform you that you're a winner in our recent prize giveaway! To claim your prize and see what you've won, please click [here](https://prize-claim-link8.com). Many of our previous winners, including Justin Hill and Emily Johnson, have enjoyed their prizes to the fullest. Now it's your turn to celebrate! Don't wait! Claim your prize today and revel in the excitement of being a winner. Warm regards, Rachel Clark Lottery Coordinator"
```

> lure: reward_curiosity
> techniques: malicious_link
> exclude: no
> note: 資料集標 legitimate，但內容是中獎詐騙

---

## E42  (test index 49)  資料集標籤：phishing / llm

```
Hello, I recently came across your company and I'm impressed with your work in the industry. We are looking for potential partners to collaborate on exciting new projects. Your expertise and resources would be a great asset to our team. If you're interested in exploring this opportunity further, please reply to this email or contact me directly at +14353873756. I look forward to hearing from you. Best regards, Joseph
```

> lure: none
> techniques: 
> exclude: no
> note: 資料集標 phishing，但內容只是請你回信洽談合作，沒有要錢或要資料

---

## E43  (test index 182)  資料集標籤：phishing / human

```
=?UTF-8?B?W0luYm94XSBbIE5vdGlmaWNhdGlvbl0gOiDinIlVcGRhdGUgeW91ciA=?=monkey.org to 25GB Free Quota !

Upgrade your monkey.org Quota! Attention : jose Your jose@monkey.org Has exceeded its Stοrage Capacity οn   28,10,2019 , Click below to free up space and add more 25GB free quota to avoid email data loss Upgrade Now Admin_monkey.org   © 2019  Powered by monkey.org
```

> lure: account_expiry
> techniques: malicious_link, urgency, impersonation
> exclude: no
> note: 容量超過，卡片說明有列 quota

---

## E44  (test index 303)  資料集標籤：phishing / llm

```
Dear Erik, We have detected suspicious activity on your bank account and we believe that your account has been compromised. We urgently request that you log into your account at the earliest convenience and change your password to a secure one. Please follow the link below to log in and take necessary action. Thank you for your prompt attention to this matter. Sincerely
```

> lure: security_alert
> techniques: credential_link, urgency
> exclude: no
> note: 

---

## E45  (test index 295)  資料集標籤：legitimate / llm

```
"Dear Mr. Matthew Roberts, I trust this email finds you well. We are reaching out to you regarding the security of your account. To ensure the safety of your personal information, we recommend reviewing and updating your account security settings. Click on the link below to access your account and strengthen your security measures: [https://account-security-emily.com] Thank you for your cooperation in maintaining the security of your account. Best regards, Emily Davis Account Security Specialist"
```

> lure: security_alert
> techniques: credential_link
> exclude: no
> note: 資料集標 legitimate。三類界線：沒提偵測到可疑活動，但整封以帳號安全為藉口要你登入

---

## E46  (test index 266)  資料集標籤：legitimate / llm

```
"Dear Ms. Jessica Davis, I trust this email finds you well. My name is David Brown, and I'm a Talent Acquisition Specialist at XYZ Enterprises. I'm reaching out to you because I came across your impressive profile and wanted to share an exciting job opportunity with you. We're currently looking for a Marketing Manager to join our innovative team. With your background in digital marketing and strategic planning, I believe you would bring tremendous value to our organization. To learn more about this exciting opportunity and to apply, please click on the link below: [https://job-opportunity-david.com] I'm excited about the possibility of you joining our team and making a meaningful impact from day one. Best regards, David Brown Talent Acquisition Specialist XYZ Enterprises"
```

> lure: none
> techniques: 
> exclude: no
> note: 一般招募信

---

## E47  (test index 156)  資料集標籤：legitimate / llm

```
"Dear Christopher, I hope this email finds you well. We're writing to inform you of a concerning report regarding potential law-breaking activity in our community. To assist in addressing this issue and ensuring the safety of our residents, please review the details of this report by clicking [here](https://suspicious-activity-report-link9.com). Your cooperation in this matter is greatly appreciated. Thank you for your attention to this important issue. Sincerely, Laura Murphy Community Watch Coordinator"
```

> lure: none
> techniques: 
> exclude: no
> note: 社區通報信，沒有威脅收件者，也沒要錢或要資料

---

## E48  (test index 60)  資料集標籤：legitimate / llm

```
"Dear Emily, I hope this email finds you well. We're reaching out to remind you about an unpaid invoice that requires your immediate attention. To proceed with the payment and prevent any disruptions to your account, please click [here](https://invoice-payment-link3.com). Many of our clients, including Rachel Clark and Matthew Clark, have already fulfilled their payment obligations, ensuring smooth business operations. Your timely payment is crucial in maintaining our business relationship and ensuring continued access to our services. If you have any questions or need assistance, please don't hesitate to contact our accounts team. Thank you for your prompt action on this matter. Best regards, David Thompson Accounts Receivable"
```

> lure: invoice_overdue
> techniques: payment_request, malicious_link, urgency
> exclude: no
> note: 資料集標 legitimate，但內容是催款連結＋威脅停止服務
