# 詐騙警示 RAG 驗證集：標準答案

規則見 [../rules.md](../rules.md) 第 7 節。設定已凍結，**標完才跑，只跑一次，結果不好也不調整。**

來源：data/val（這些實驗都沒用過的切分）。V＝隨機、W＝針對。

- `lure:` 正確誘餌 id
- `specific:` 專屬警示編號，逗號分隔，沒有就留空
- `general:` 通用警示，只能是 A03、A11，沒有就留空

誘餌 id：none, account_expiry, security_alert, billing_problem, parcel_fee, file_share, mailbox_error, invoice_overdue, reward_curiosity, charity, legal_threat

| 編號 | 日期 | 標題 |
|---|---|---|
| A01 | 2026-05-26 | Asked to enter your email address and password to open a party invite? That’s a scam |
| A02 | 2023-05-09 | Those urgent emails from MetaMask and PayPal are phishing scams |
| A03（通用） | 2024-12-11 | Phishing scams can be hard to spot |
| A04 | 2025-07-02 | Are you really out of Cloud storage or is that message a scam? |
| A05 | 2018-12-26 | Netflix phishing scam: Don’t take the bait |
| A06 | 2023-12-14 | Fake shipping notification emails and text messages: What you need to know this holiday season |
| A07 | 2025-04-16 | Is that unexpected text a scam? |
| A08 | 2014-12-22 | Package delivery scam — delivered to your inbox |
| A09 | 2018-02-23 | Phishers send fake invoices |
| A10 | 2026-05-14 | Run a small business? Pay your bills, not scammers |
| A11（通用） | 2024-09-04 | Don’t take the bait on phishing scams |
| A12 | 2025-06-26 | Don’t pay for a prize (scam) |
| A13 | 2023-04-10 | Are you really the lucky winner? Spot the prize scams |
| A14 | 2026-01-22 | That text or email about your “tax refund” is a scam |
| A15 | 2024-01-23 | The IRS doesn't send tax refunds by email or text |
| A16 | 2023-12-11 | How to spot the latest job scams |
| A17 | 2022-05-11 | Want to work from home? Spot the scams first |
| A18 | 2023-04-17 | Make big money — now |
| A19 | 2026-08-27 | When donating, support those in need, not a scammer |
| A20 | 2023-10-19 | Safely donating in response to the Israel-Gaza crisis |
| A21 | 2024-09-13 | Did you get a call or email saying you missed jury duty and need to pay? It’s a scam |
| A22 | 2026-06-11 | Ignore calls, texts, and emails threatening to arrest you for missing jury duty |
| A23 | 2022-07-06 | COVID-19 contact tracing text message scams |

---

## V01  (val index 281)  資料集標籤：phishing / llm

```
Hi William, I hope you're having a great day. I stumbled upon an incredible social media contest that I believe you'll find enticing. It's your chance to win exclusive prizes and elevate your social media game. Click here to participate: [https://social-media-contest-link.com] Wishing you the best of luck! Ashley Turner
```

> lure: reward_curiosity
> specific: 
> general: A03
> labeled_by: claude+author
> note: 作者判斷：不算中獎（是「參加比賽有機會得獎」，不是「你已經中獎」），所以沒有專屬警示

---

## V02  (val index 85)  資料集標籤：legitimate / human

```
Re: [SM-USERS] SM 1.4.13 Configuration Question: Mail Domain	Parameter

On 2/7/08, Nancy Graziano  wrote:
> Good Evening,
>
> I have tried setting the Mail Domain parameter

Please be more specific.

> to our family's domain name
> (my husband and I are the only ones accessing mail through our own SM 1.4.13
> installation),
> and when I try to login without using our Domain extension, I get an
> "Unknown User or Password Incorrect" error. However, if I include our Domain
> extension, I can login
> without a problem.

See the Login Manager plugin.

> Here are the specifics of my ISP/installation:
>
>
> SM 1.4.13, manual installation
> Installed Plugins: address_add-2.1-1.4.0, calendar_file_backend-1.0-2.0,
> shared_calendars-2.0.1-1.4.0, twc_weather-1.3p3b-RC2
> PHP v4.4.4
> Web Server: Apache 1.3.37 (Unix)
> IMAP Server: IMAP c-Client Version 2004 [not sure if this is what you need,
> but it is all I could find...]
> SMTP Server: Cannot locate
> OS: Linux 2.6.9-55.0.2.ELsmp
> Browsers tried: Firefox (v2.0.0.12),  IE7 (v7.0.5730.11), IE6
> (v6.0.2900.2180.xpsp2_gdr.070227-2254) I tried a search
> online at SourceForge going back a couple months (before the announcement of
> SM1.4.13) but didn't find anything. Any suggestions?
>
> Thanks in advance.
> Nancy
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(未逐封)

---

## V03  (val index 319)  資料集標籤：phishing / llm

```
Dear Sarah, I hope this email finds you well and filled with the same passion for education that has brought us together today. My name is Michael Davis, and I represent the Enlightened Minds Scholarship Foundation. We are dedicated to providing educational opportunities to bright and deserving students who lack the necessary resources to pursue their dreams. Sarah, we have identified you as someone who values the power of education and understands its potential to change lives. Your support can offer disadvantaged students a pathway to success, unlocking their true potential and enabling them to overcome socioeconomic barriers. By making a contribution to our scholarship fund, you are investing in the future of these young minds. Your generosity will enable them to access quality education, empowering them to become leaders, innovators, and contributors to society. Together, we can create a ripple effect that will shape the trajectory of these students' lives and positively impact generations to come. I invite you, Sarah, to join us in this noble mission and make a difference that will be felt for years to come. To make a secure donation and become a beacon of inspiration for these aspiring scholars, please click on the following link: https://enlightenedmindsscholarship-donate.com Thank you for your consideration, Sarah. Together, let's illuminate the path to a brighter future through education. Warm regards, Michael Davis Enlightened Minds Scholarship Foundation
```

> lure: charity
> specific: A19, A20
> general: A03
> labeled_by: claude+author(未逐封)
> note: 獎學金捐款，屬於假慈善

---

## V04  (val index 226)  資料集標籤：phishing / human

```
Blockchain Failure Notice

Reconfirm account for unrestricted access Someone attempted unsuccessfully to sign into your account using a new device (TECNO-KG7h ) on Fri, 05 May 2022 22:06:34 PM, from CN. Your account has been restricted for your protection.  Restore activityYou can also see security activity at https://login.blockchain.com Blockchain.com, Inc. NMLS ID# 2024031 |NMLS Consumer Access                 Reconfirm account for unrestricted              access Someone              attempted unsuccessfully to sign into your account using a new              device (TECNO-KG7h ) on Fri, 05 May 2022 22:06:34 PM, from              CN.Your account has been restricted for your protection.              Restore              activity You              can also see security activity athttps://login.blockchain.com Blockchain.com, Inc. NMLS ID# 2024031 |NMLS Consumer              Access
```

> lure: security_alert
> specific: A02
> general: A03, A11
> labeled_by: claude+author
> note: 冒充 Blockchain.com 說帳號被限制；與練習集 R02 一樣把 A02（加密貨幣錢包冒充）算專屬

---

## V05  (val index 84)  資料集標籤：legitimate / human

```
[clamav-virusdb] Update (daily: 5760)

ClamAV database updated (09 Feb 2008 16-38 +0000): daily.cvd
Version: 5760

Submission-ID: 2257892
Sender: Virus Total
Submission notes: Same as in Submission-ID 2186561
Added: No

Submission-ID: 2257916
Sender: Virus Total
Submission notes: Same as in Submission-ID 2471810
Added: No

Submission-ID: 2257923
Sender: Virus Total
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2257929
Sender: Upload Malware
Submission notes: Already detected as Trojan.Downloader-23037
Added: No

Submission-ID: 2257975
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2257994
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258003
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258011
Sender: Jotti
Submission notes: Same as in Submission-ID 2364572
Added: No

Submission-ID: 2258049
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258064
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258067
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258085
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258087
Sender: Virus Total
Submission notes: Same as in Submission-ID 2309144
Added: No

Submission-ID: 2258093
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258129
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258147
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258151
Sender: Virus Total
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258158
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258177
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258199
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258202
Sender: Virus Total
Submission notes: Same as in Submission-ID 2304556
Added: No

Submission-ID: 2258255
Sender: Virus Total
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258262
Sender: Virus Total
Submission notes: Same as in Submission-ID 2246213
Added: No

Submission-ID: 2258276
Sender: Virus Total
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258300
Sender: VirScan.org
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID: 2258455
Sender: Virus Total
Submission notes: Same as in Submission-ID 2520262
Added: No

Submission-ID:
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(未逐封)

---

## V06  (val index 266)  資料集標籤：legitimate / llm

```
"Dear Emily, We hope you're doing well. We wanted to emphasize the importance of strengthening your account security. Your account contains sensitive information, and taking proactive steps to enhance security is crucial. To review and update your security settings, please click [here](https://account-security-link4.com). Your commitment to account security is greatly appreciated. Thank you for your cooperation. Best regards, Matthew Garcia Security Manager"
```

> lure: security_alert
> specific: 
> general: A03, A11
> labeled_by: claude+author
> note: 資料集標 legitimate，但內容是要你點連結更新帳號安全設定

---

## V07  (val index 246)  資料集標籤：phishing / llm

```
Dear Sarah, I hope this email finds you well. We wanted to send you a gentle reminder that time is running out to support our crucial efforts in providing aid to war-affected regions. Your past involvement has shown your unwavering commitment to making a difference, and we don't want you to miss this opportunity. To contribute and continue changing lives, please visit the following link: https://waraid-lastchance-donate.com. Your contribution, no matter the size, will help us provide essential resources, rebuild communities, and offer a glimmer of hope to those in need. We appreciate your consistent support and dedication to this cause. Together, we can be the catalyst for positive change and create a better future for all. Warm regards, Andrew Roberts
```

> lure: charity
> specific: A19, A20
> general: A03
> labeled_by: claude+author(未逐封)

---

## V08  (val index 273)  資料集標籤：phishing / human

```
=?UTF-8?B?QWxlcnQ6IOKakSBNYWlsYm94IHBhc3N3b3JkIHJlc2V0IGluIHByb2dyZXNzIGZvciA=?=jose@monkey.org

Your Password Reset in Progress                                                              monkey.org Dear jose   Your password reset is in process and your current password will be disabled shortly.   The password reset link will be forwarded to the new optional email submitted.Don't ignore this email notification your request will take effect shortly If you did not request this password resetUse the Cancel Request button to cancel the password reset and keep your account secure.   Cancel Request Thank you Service Administration Team Microsoft inc © 2020: We are here to serve you better.
```

> lure: account_expiry
> specific: 
> general: A03, A11
> labeled_by: claude+author(未逐封)
> note: 冒充 Microsoft 的密碼重設通知；與練習集 R18 同樣歸 account_expiry

---

## V09  (val index 235)  資料集標籤：phishing / human

```
=?UTF-8?B?4pqg77iPIEFDVElPTiBSRVFVSVJFRCBbIA==?=jose@monkey.org ] 

Webmail* ROUNDCUBE Dear jose, jose@monkey.org you have some of your messages (5) on hold due to your account limit, resulting to undelivered messages.Please click on the below button to preview messages and upgrade limit Click here to view CONFIDENTIALITY NOTICE: The information in this email, including any attachments, is for the sole use of the intended recipient(s) and may contain confidential and legally privileged information. If you are not the intended recipient, any disclosure, copying, distribution or use of the contents of this information in any manner is strictly prohibited and may be unlawful.
```

> lure: mailbox_error
> specific: 
> general: A03, A11
> labeled_by: claude+author(未逐封)

---

## V10  (val index 233)  資料集標籤：legitimate / llm

```
"Dear Amanda, I hope this email finds you in high spirits. I'm thrilled to share some exciting news with you - you've won a prize in our latest giveaway! You have been chosen to receive a fabulous prize valued at $1000! To claim your prize and begin the necessary procedures, please click [here](https://prize-claim-link10.com) to verify your identity and provide us with your mailing address. Your security and privacy are paramount to us. We have implemented stringent measures to ensure the confidentiality and integrity of your personal information. Congratulations once again on your win, Amanda! We can't wait to deliver your prize and share in your joy. Best regards, Kyle Thompson Prize Coordinator"
```

> lure: reward_curiosity
> specific: A12, A13
> general: A03, A11
> labeled_by: claude+author
> note: 資料集標 legitimate，但內容是中獎詐騙

---

## W01  (val index 223)  資料集標籤：phishing / human  挑選類別：包裹運費

```
Your Parcel Number RL001097064 is on the way

Your Parcel Number RL001097064 is on the way Your package is stopped at our post A R99.13 shipping cost have not been paid. if shipping cost is not paid, the package will be returned. Pay fees R99.13  


 Your Parcel Number RL001097064 is on the way Your package is stopped at our post A R99.13 shipping cost have not been paid. if shipping cost is not paid, the package will be returned.  

	Pay fees R99.13   



	            Your Parcel Number RL001097064 is on the way Your package is stopped at our post A R99.13 shipping cost have not been paid. if shipping cost is not paid, the package will be returned. Pay fees R99.13
```

> lure: parcel_fee
> specific: A06, A07, A08
> general: A03
> labeled_by: claude+author(未逐封)

---

## W02  (val index 138)  資料集標籤：phishing / llm  挑選類別：包裹運費

```
Dear Jasmine, Your Shipment is Lost. Take Immediate Action to Locate it! To locate your lost package, simply click the link below and provide us with your tracking number. Locate Your Lost Shipment: https://flickr.com We understand the importance of your order and are committed to helping you find a resolution. Warm regards, Technologent
```

> lure: parcel_fee
> specific: A06, A07, A08
> general: A03
> labeled_by: claude+author(未逐封)
> note: 包裹遺失、要你提供追蹤號碼，沒有要運費

---

## W03  (val index 98)  資料集標籤：phishing / llm  挑選類別：發票催款

```
Dear Christopher, We hope this email finds you well. We are writing to inform you that there is an overdue payment for invoice #24680. To prevent any further complications, please settle the payment by clicking on the following link: https://payment-confirmation-link.com If you have any questions or need assistance, please don't hesitate to contact us. Best regards, Samantha Roberts
```

> lure: invoice_overdue
> specific: A09, A10
> general: A03
> labeled_by: claude+author(未逐封)

---

## W04  (val index 58)  資料集標籤：phishing / llm  挑選類別：中獎

```
Dear Emily, Congratulations! You are the lucky winner of our grand cash prize of $10,000. Your perseverance and luck have paid off, and we are excited to reward you with this substantial sum of money. However, time is of the essence. This is a limited-time offer, and you must claim your cash prize within the next 72 hours. Failure to do so will result in the forfeiture of your winnings. Don't let this opportunity slip away. To claim your $10,000 cash prize, click the link below and follow the instructions on the secure claim page: https://cash-prize-claim-link.com Remember, the principle of Scarcity is at play here. Act now, and you will be one of the fortunate few who can enjoy a life-changing cash prize. Best regards, Thomas Mitchell
```

> lure: reward_curiosity
> specific: A12, A13
> general: A03
> labeled_by: claude+author(未逐封)

---

## W05  (val index 155)  資料集標籤：phishing / llm  挑選類別：退稅

```
Dear Jennifer, I hope this email finds you well. As an authorized IRS agent, I am reaching out to inform you about an unclaimed tax refund that you are eligible for. Our records indicate that you have not yet claimed the full amount you are owed. To claim your refund now, please click on the following link: [https://refund-claim-link4.com] Please be assured that this link will direct you to a secure portal where you can provide the necessary information to process your refund. As an IRS agent, I want to emphasize that your personal and financial details will be handled with the utmost care and security. Should you have any questions or concerns, please feel free to reach out to me directly at christopher.davis@irs.gov or call our dedicated helpline at 1-800-XXX-XXXX. Thank you for your prompt attention to this matter. Sincerely, Christopher Davis IRS Agent
```

> lure: reward_curiosity
> specific: A14, A15
> general: A03, A11
> labeled_by: claude+author(未逐封)

---

## W06  (val index 74)  資料集標籤：phishing / llm  挑選類別：求職

```
Hey Sophia, I hope this email finds you well. I wanted to personally reach out to you regarding an amazing work-from-home opportunity. Our company, Virtual Assistant Solutions, is currently seeking highly organized individuals like yourself to join our team. If you're interested in exploring this opportunity, click on the link below to learn more and apply: https://virtualassistant-job.com Take control of your career and enjoy the freedom of working from anywhere in the world! Best regards, James Harris
```

> lure: reward_curiosity
> specific: A16, A17
> general: A03
> labeled_by: claude+author(未逐封)

---

## W07  (val index 390)  資料集標籤：phishing / llm  挑選類別：投資

```
Hi Samuel, It's been a while since we last caught up, and I have some exciting news to share with you. I recently came across a fantastic investment opportunity that has the potential to generate substantial returns. I wanted to let you in on this exclusive opportunity before it becomes widely known. Click on the link below to learn more about this investment and secure your spot. linkedin-profile-confirmation.com I thought of you because I value our friendship and want us to benefit from this together. Let's explore this opportunity and make some great memories along the way. Best regards, Fred
```

> lure: reward_curiosity
> specific: A18
> general: A03
> labeled_by: claude+author(未逐封)

---

## W08  (val index 18)  資料集標籤：phishing / llm  挑選類別：慈善捐款

```
Dear John, I hope this email finds you well. As a compassionate individual who cares deeply about helping those affected by war, I wanted to reach out to you personally with an exclusive opportunity. For a limited time only, our organization is offering a chance to double your impact on war refugees around the world. I understand that you have a heart for those in need, and this is the perfect opportunity to make a significant difference. By clicking the link below, you will be directed to our secure donation page where you can contribute to our cause. Click here to make a difference: [https://support-war-refugees.com] What makes this offer truly special is that your generous contribution will be matched by a prominent philanthropist who shares our passion for helping war refugees. This means that every dollar you donate will be doubled, effectively doubling the impact of your donation. Can you imagine the positive change we can create together? But, here's the catch: this incredible opportunity won't last long. The matching program is only available for the next 48 hours. After that, the chance to double your impact will be gone forever. Don't miss out on this exclusive offer to provide life-saving aid to those in desperate need. Your contribution will provide shelter, food, medical assistance, and hope to countless individuals and families affected by war. Join us in making a difference today. Click the link below to donate and double your impact: [https://support-war-refugees.com] Thank you for your kind consideration and for being a beacon of hope in the lives of war refugees. Warm regards, Sarah Johnson
```

> lure: charity
> specific: A19, A20
> general: A03
> labeled_by: claude+author(未逐封)

---

## W09  (val index 32)  資料集標籤：phishing / llm  挑選類別：法律恐嚇

```
Dear Olivia, you are being investigated for your involvement in illegal activities. To provide your statement and prevent further legal action, click on the link below: [https://provide-statement-now.com]
```

> lure: legal_threat
> specific: A21, A22
> general: A03
> labeled_by: claude+author
> note: 與練習集 R10 一樣，把陪審團逮捕令警示算專屬

---

## W10  (val index 49)  資料集標籤：phishing / human  挑選類別：帳單付款

```
We're having some trouble with your current billing information 

Your suspension notification Hi jose@monkey.org, We could not authorize your payment for the next billing cycle of your subscription therefore we've suspended your membership. But your current subscription is active until it expires. Obviously we'd love to have you back, simply click restart your membership to update your details and continue to enjoy all the best TV shows & movies without interruption. RESTART MEMBERSHIP We're here to help if you need it. Visit the Help Center for more info or contact us. ?The Netflix Team    Questions? Visit the Help Center This account email has been sent to you as part of your Netflix membership. To change your email preferences at any time, please visit the Communication Settings page for your account. Please do not reply to this email, as we are unable to respond from this email address. If you need help or would like to contact us, please visit our Help Center at help.netflix.com. This message was mailed to [#email#] by Netflix. SRC: 12384_en_US Use of the Netflix service and website is subject to our Terms of Use and Privacy Statement. ?Netflix International B.V.?
```

> lure: billing_problem
> specific: A05
> general: A03, A11
> labeled_by: claude+author(未逐封)
