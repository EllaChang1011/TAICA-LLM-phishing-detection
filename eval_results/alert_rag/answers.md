# 詐騙警示 RAG 評測題：標準答案

規則見 [rules.md](rules.md)。**在看到任何檢索結果之前標完。**

- 全部 30 封都由 Claude 預標（作者決定交給 Claude）。請逐封複核：同意就把 labeled_by 改成 claude+author，不同意就改答案並在 note 記下原因
- 有 note 的是比較難判斷的，請優先看

每封填：
- `lure:` 這封信的正確誘餌 id（查詢 D 會用到）
- `specific:` 專屬警示編號，逗號分隔，沒有就留空
- `general:` 通用警示，只能是 A03、A11，沒有就留空

誘餌 id：none, account_expiry, security_alert, billing_problem, parcel_fee, file_share, mailbox_error, invoice_overdue, reward_curiosity, charity, legal_threat

## 警示清單

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

## R01  (test index 314)  資料集標籤：phishing / human

```
monkey.org Password update

Dear jose, The password for your email account (jose@monkey.org) expires today 10/11/2022 3:37:27 a.m.. Keep and continue with the same password using the below portal.     Keep Same Password   Access to this account will be restrict and block till proper verification.   You can also see security activity at: https://myaccount.monkey.org/notifications
```

> lure: account_expiry
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)

---

## R02  (test index 47)  資料集標籤：phishing / human

```
UNCONFIRMED CRYPTO TRANSACTION

- This mail is in HTML. Some elements may be ommited in plain text. - Blckchain ? ..com Bitcoin Wallet Payment Not Rectified Hi there, You have a Pending Transaction of $7,000,000.00BTC that was directed to your wallet email address ( jose@monkey.org ) We need your confirmation with your Wallet Address before it can be redirected to your provided Wallet address. Reply with Your ticket number (#2660112) and your Wallet address for reconfirmation before crediting you. Best, The Blockchain.com Team  Blockchain.com Blockchain Access UK Ltd 2 Tallis Street London EC4Y 0AB This is an agreement between Blockchain Luxembourg S.A. and Blockchain Access UK Ltd (collectively referred to herein as "Blockchain.com", "we", "us", or "our") and you (together with Blockchain.com, the "Parties" and each a "Party"). By using any Blockchain.com service, whether through blockchain.com , any associated website, API, or mobile application, you agree that you have read, understood, and accept all of the terms and conditions contained herein (the "User Agreement"), as well as our Privacy Policy available at blockchain.com/legal , Cookie Policy, available at blockchain.com/cookies , API Agreement, available at blockchain.com/legal/api- terms and Trading Principles, located at exchange.blockchain.com/ legal Important Note Digital asset markets are unregulated and not currently governed by any specific European or US regulatory framework. Digital currencies are not bank deposits, are not legal tender, are not backed by the government, and accounts and value balances. Blockchain Access UK Ltd's products and services are not within the jurisdiction of the UK Financial Ombudsman Scheme, nor are they subject to the UK Financial Services Compensation Scheme, the US Federal Deposit Insurance Corporation or Securities Investor Protection Corporation, or any other non-UK or non-US governmental or government-backed protections. Legislative and regulatory changes or actions in any jurisdiction in which Blockchain.com's customers are located may adversely affect the use, transfer, exchange, and value of digital currencies.                      Blckchain?.com Bitcoin Wallet Payment Not Rectified  Hi there, You have a Pending Transaction of $7,000,000.00BTC that was directed to your wallet email address ( jose@monkey.org ) We need your confirmation with your Wallet Address before it can be redirected to your provided Wallet address. Reply with Your ticket number (#2660112) and your Wallet address for reconfirmation before crediting you. Best,The Blockchain.com Team                Blockchain.com Blockchain Access UK Ltd2 Tallis StreetLondon EC4Y 0AB This is an agreement between Blockchain Luxembourg S.A. and Blockchain Access UK Ltd (collectively referred to herein as "Blockchain.com", "we", "us", or "our") and you (together with Blockchain.com, the "Parties" and each a "Party"). By using any Blockchain.com service, whether through blockchain.com, any asso
```

> lure: reward_curiosity
> specific: A02
> general: A11
> labeled_by: claude+author(整批同意)
> note: 邊界：冒充 Blockchain.com，要你回信提供錢包地址。A02 講的是加密貨幣錢包的冒充釣魚，手法相近但情境不同（A02 是錢包被凍結）

---

## R03  (test index 28)  資料集標籤：phishing / llm

```
Dear Amanda, I hope this email finds you well. My name is Matthew Turner, and I'm offering you an exclusive opportunity to become a master identity thief. We have a proven system that guarantees success and financial freedom. To learn more about this opportunity and take the first step towards a life of luxury, visit: https://identity-theft-opportunity-link.com Remember, this opportunity is only available to a select few. Don't let it slip away! Best regards, Matthew Turner
```

> lure: reward_curiosity
> specific: A18
> general: A03
> labeled_by: claude+author(整批同意)
> note: 邊界：「保證成功、財務自由、只限少數人」符合 A18 描述的高壓賺錢機會，但信件內容本身很怪（教人當身分竊賊）

---

## R04  (test index 343)  資料集標籤：legitimate / llm

```
"Dear Matthew, Congratulations once again on accepting the job offer for the position of [Job Title] with [Company Name]! We are delighted to have you join our team. As you begin your journey with us, we want to ensure a smooth transition into your new role. Attached to this email, you will find detailed information regarding the onboarding process, including important documents to review and complete, as well as upcoming orientation sessions and training schedules. Please review the attached onboarding package at your earliest convenience and reach out if you have any questions or require assistance. We look forward to working with you and wish you all the best in your new position. Best regards, Olivia Smith HR Coordinator [Company Name]"
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)
> note: 正常的到職通知，附件是到職資料

---

## R05  (test index 286)  資料集標籤：legitimate / human

```
Re: clarification of our inclusion policy (fwd) 


Daryl C. W. O'Shea writes:
> Justin Mason wrote:
> > Daryl C. W. O'Shea writes:
> >> Graham Murray wrote:
> >>> Michael Peddemors  writes:
> >>>
> >>>> And with the current SA, this is more difficult to turn off via a config 
> >>>> option for example.. 
> >>> I do not think it is difficult. Does setting the scores of the following
> >>> rules to zero in local.cf not turn off spamhaus RBL checking?
> >>> __RCVD_IN_ZEN RCVD_IN_SBL RCVD_IN_XBL RCVD_IN_PBL
> >> URIBL_SBL queries sbl.spamhaus.org, FWIW.
> > 
> > yep, this kind of proves Michael's point I think ;)
> 
> Well, no harder to turn off than any other DNS based rule.  grep'ing for 
> the zone you want to disable isn't exactly an obscure method or much work.
> 
> In any case, it reminds me of a feature I had in mind... rule groups.
> 
> header  RCVD_IN_XBL     whatever
> group   RCVD_IN_XBL     spamhaus
> header  __RCVD_IN_ZEN   whatever
> group   __RCVD_IN_ZEN   spamhaus
> 
> then to disable them all...
> 
> disable_group    spamhaus
> 
> ...disable_group lines could be included by default, commented out, in 
> local.cf.

yeah, exactly, that would be a good way to solve the problem.
Or maybe an

  if group_active(spamhaus)
  header  RCVD_IN_XBL     whatever
  header  __RCVD_IN_ZEN   whatever
  ...
  endif



--j.
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)

---

## R06  (test index 278)  資料集標籤：phishing / llm

```
Hello William, we have noticed some unusual activity on your account. To secure your account, please verify your information by clicking on the following link: https://account-security-check.com. Your prompt action is highly appreciated. Thank you.
```

> lure: security_alert
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)

---

## R07  (test index 30)  資料集標籤：legitimate / human

```
[Bug 5667] add new URIBL lookup on rhsbl.ahbl.org

http://issues.apache.org/SpamAssassin/show_bug.cgi?id=5667





------- Additional Comments From user7@gvc.ceas-challenge.cc  2007-10-03 05:53 -------
(In reply to comment #0)>
> For providers who use our DNSbl service, you must make sure to alert your
> customers to the fact that you are using our service on the support pages or
> signup pages with a link to our website. Your customers have a right to know
> what methods you are using to filter their e-mail.'
> 
> this would be tricky for us... :(

duh.  we're talking about the RHSbl service, not the DNSbl one.



------- You are receiving this mail because: -------
You are the assignee for the bug, or are watching the assignee.
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)

---

## R08  (test index 242)  資料集標籤：phishing / human

```
=?UTF-8?B?4pqg77iPIFJlY292ZXJ5IE5vdGlmaWNhdGlvbiAgKE1vbmRh?=
 =?UTF-8?B?eSwgRmVicnVhcnkgMjgsIDIwMjIp?=

Recovery Notification Hello jose@monkey.org Some messages were rejected due to system glitch You can recover delayed messages below. Restore Messages https://c0bf9de4-33bb-4cb0-8670-50c516bd-mw6d3.ondigitalocean.app/e659d4a6-3a42-4191-9d70-769a75/?email=jose@monkey.org Thank You. monkey.org support © 2022 Inc. All Rights Reserved.     ⚠️ Recovery Notification  (Monday, February 28, 2022)         Recovery Notification Hello jose@monkey.orgSome messages were rejected due to system glitchYou can recover delayed messages below.Restore Messages Thank You.     monkey.org support © 2022  Inc. All Rights Reserved.
```

> lure: mailbox_error
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)

---

## R09  (test index 363)  資料集標籤：phishing / llm

```
Dear Jessica Davis, I hope this email finds you in good health and high spirits. My name is David Roberts, and I am the Recruitment Manager at Elite Solutions. I came across your impressive resume and wanted to offer you an exciting work-from-home opportunity. At Elite Solutions, we believe in empowering individuals to achieve financial independence and success. We have a unique program designed for motivated individuals like yourself who are seeking the flexibility and freedom of working from home while earning a substantial income. To learn more about this exciting work-from-home opportunity and to take the first step towards financial freedom, please click on the following link: https://elitesolutions-workfromhome.com We provide comprehensive training and ongoing support to ensure your success in this venture. If you have any questions or need further information, please don't hesitate to contact me directly at workfromhome@elitesolutions.com. Don't miss out on this opportunity to create the life you've always dreamed of with Elite Solutions! Best regards, David Roberts Recruitment Manager Elite Solutions
```

> lure: reward_curiosity
> specific: A16, A17
> general: A03
> labeled_by: claude+author(整批同意)
> note: 招募信＋在家工作

---

## R10  (test index 120)  資料集標籤：phishing / llm

```
Hello Benjamin, our records indicate a violation of legal compliance on your part. To avoid further consequences, please click on the link below to resolve this matter: [https://resolve-compliance-issue.com]
```

> lure: legal_threat
> specific: A21, A22
> general: A03
> labeled_by: claude+author(整批同意)
> note: 邊界：A21、A22 講的是陪審團逮捕令，這封只說「違反法規」，但核心手法相同（以法律後果威脅、要你點連結處理）

---

## R11  (test index 142)  資料集標籤：legitimate / llm

```
"Dear Sarah, I trust you're having a great day. We're thrilled to introduce you to our podcast series where we delve into random topics and unravel intriguing mysteries. To listen to our latest episodes and embark on a journey of discovery, please click [here](https://random-topic-podcast-link4.com). Your consistent listenership fuels our passion for storytelling and exploration. Thank you for tuning in. Best regards, Matthew Clark Podcast Host"
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)

---

## R12  (test index 198)  資料集標籤：phishing / human

```
You Have a New USAA Document

To ensure delivery to your inbox, please add USAA.Customer.Service@mailcenter.usaa.com to your address book.      USAA SECURITY ZONE USAA # ending in:7829   New Document for You   Dear Member,   Please take a few minutes to review the following new document that we've posted for you:   Change in Terms Credit Card     View Documents     Thank you, USAA   USAA means United Services Automobile Association and its insurance, banking, investment and other companies. Banks Member FDIC. Investments provided by USAA Investment Management Company and USAA Financial Advisors Inc., both registered broker dealers. a   Go PaperlessReview and edit your online document preferences at usaa.com.                    Please do not reply to this e-mail.   To contact USAA, visit our secure contact page.   Privacy Promise   USAA, 9800 Fredericksburg Road, San Antonio, Texas 78288                129481-1217
```

> lure: file_share
> specific: 
> general: A03
> labeled_by: claude+author(整批同意)
> note: USAA 文件通知，沒有講檔案分享的專屬警示

---

## R13  (test index 51)  資料集標籤：phishing / human

```
Notification - MailBox has (3) Pending emails

Notification   Hi jose@monkey.org You have 9 unreceived emails on 2/13/2021 4:05:14 a.m., this was caused due to a system delay, Rectify Below:  View Pending Messages In Mail Saver.Source: monkey.org Support
```

> lure: mailbox_error
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)

---

## R14  (test index 298)  資料集標籤：legitimate / human

```
Re: Forwarding all localmail

* Randy Ramsdell :

> I would like to know what would be better that using aliases or .forward  
> to forward all local mail. I want to simply forward all mail without  
> having to intervene for new users or new services.
> Any suggestion?

aliases or virtual_alias_maps

-- 
Ralf Hildebrandt (ecfa.ocnmogiylyn@charite.de)             ulivs@charite.de
Postfix - Einrichtung, Betrieb und Wartung       Tel. +49 (0)30-450 570-155
http://www.arschkrebs.de
Lesbian Nazi Hookers Abducted by UFOs and Forced Into Weight Loss
Programs - -all next week on Town Talk.
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)

---

## R15  (test index 33)  資料集標籤：phishing / llm

```
Hello, esteemed user! Our system has detected a potential security breach in your account. We kindly request you to verify your account details by clicking the link below. As a gesture of goodwill, we will grant you a one-month premium subscription for free once the verification is complete. Act now to protect your account!
```

> lure: security_alert
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)
> note: A02 只講加密貨幣錢包和 PayPal，不算專屬

---

## R16  (test index 79)  資料集標籤：legitimate / llm

```
"Dear Ms. Samantha Harris, I hope this email finds you safe and well. In today's digital landscape, the threat of online fraud and cybercrime is ever-present, making it essential to stay informed and vigilant. As a fraud awareness advocate, I'm committed to providing you with the information and resources you need to protect yourself from online fraud and scams. Here are some proactive steps you can take to safeguard your financial and personal information: 1. Regularly review your bank and credit card statements for any unauthorized transactions. 2. Be cautious when sharing personal information online, especially on social media platforms. 3. Enable account alerts and notifications for unusual activity. 4. Educate yourself about common online scams and phishing tactics. 5. Report any suspicious activity to the appropriate authorities. For additional tips and resources on fraud prevention, please visit our fraud awareness website: [https://prevent-online-fraud-christopher.com] Thank you for your attention to this important matter, and please don't hesitate to reach out if you have any questions or concerns. Best regards, Christopher Taylor Fraud Awareness Advocate"
```

> lure: none
> specific: 
> general: 
> labeled_by: claude+author(整批同意)
> note: 防詐宣導信，本身沒有招數

---

## R17  (test index 197)  資料集標籤：phishing / llm

```
Dear Mary, We have detected some suspicious activity on your account and are reaching out to ensure the security of your valuable information. As part of our commitment to account security, we kindly request you to verify your account details by clicking on the following link: https://account-security-verification.com. Your prompt action is highly appreciated, as it will help us resolve any potential security concerns and prevent unauthorized access to your account. Thank you for your cooperation. Sincerely, John Anderson
```

> lure: security_alert
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)

---

## R18  (test index 42)  資料集標籤：phishing / human

```
LinkedIn Important Notification

Dear jose, We notice that you requested to cancel your LinkedIn account. Click below to continue with your account  for free. Continue Using Your LinkedIn Account Source: LinkedIn.com  ©2022
```

> lure: account_expiry
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)
> note: 冒充 LinkedIn，說你申請刪除帳號

---

## R19  (test index 106)  資料集標籤：phishing / human

```
jose@monkey.org =?UTF-8?B?7ZWg64u565+JIOyXheuNsOydtO2KuCDtlYTsmpQg?=

안녕    사용자, 귀하의  jose 계정 2 개월 전부터 업그레이드되지 않은.   지금 업그레이드하거나 계정이 차단됩니다.   지금 업그레이드   다음 24 시간 이내에 계정을 업그레이드하지 않으면 영구 종료됩니다.   monkey.org. 2020
```

> lure: account_expiry
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)
> note: 韓文信；bge 是英文模型，查詢 A 預期會很差

---

## R20  (test index 67)  資料集標籤：phishing / llm

```
Dear User, We have recently upgraded our platform to provide you with enhanced features and improved user experience. To access these new features, we kindly request you to update your account settings. Click on the link below to proceed with the update. Failure to do so may result in limited functionality and restricted access to our services. amazon-prime-account-recovery.com Thank you for your cooperation. Regards, The Account Management Team
```

> lure: account_expiry
> specific: 
> general: A03, A11
> labeled_by: claude+author(整批同意)
> note: 理由是平台升級

---

# 針對組：專屬命中@3 用

依 rules.md 第 5 節的規則挑選。逮捕令／法律恐嚇類在測試集中找不到符合的信，從缺。

---

## T01  (test index 144)  資料集標籤：phishing / human  挑選類別：包裹運費

```
Your Parcel Number RL001097064 is on the way

Your shipment is on the way Dear ClientYour Parcel Number RL001097064 is on the wayYour package is stopped at our post A R 16.13 shipping cost have not been paid.if shipping cost is not paid, the package will be returned. Payment details Economy Service delivery of 1 parcel with a charge weight of 0.856 kg Base Charge R 3.00 Waybill Surcharge R 5.50 Fuel Surcharge 34.82 % R 6.30 Sub Total R 1.80 VAT 15 % R 1.62 Grand Total R 16.13 Pay fees R16.13   With the RAM App, you can see the current status of your package and the next step..  RAM Transport (South Africa) (Proprietary) Limited t/a RAM Hand-to-Hand Couriers Regards,Terri-Leigh Fisher  Online Customer Service Representative  Online Customer Service Tel: 0861 726 726  Fax: 0861 726 726 Mobile: 0861 726 726 Email: Terri-Leigh.Fisher@ram.co.za  Branch:  Isando      

Your shipment is on the way

Dear ClientYour Parcel Number RL001097064 is on the way
Your package is stopped at our post A R 16.13 shipping cost have not been paid.
if shipping cost is not paid, the package will be returned.

 Payment details 

Economy Servicedelivery of1parcel with a charge weight of 0.856kg   

 Base Charge 	R 	3.00 

 Waybill Surcharge 	R 	5.50 

 Fuel Surcharge34.82 % 	R 	6.30 

 Sub Total 	R 	1.80 

 VAT15 % 	R 	1.62 

 Grand Total 	R 	16.13


	Pay fees R16.13  
With the RAM App, you can see the current status of your package and the next step.. 



RAM Transport (South Africa) (Proprietary) Limited t/a RAM Hand-to-Hand Couriers 


Regards,Terri-Leigh Fisher 

Online Customer Service Representative 

Online Customer Service 


Tel: 0861 726 726 Fax:0861 726 726 Mobile: 0861 726 726 Email: Terri-Leigh.Fisher@ram.co.za 

Branch:Isando



   Your shipment is on the way Dear ClientYour Parcel Number RL001097064 is on the wayYour package is stopped at our post A R 16.13 shipping cost have not been paid.if shipping cost is not paid, the package will be returned. Payment details Economy Service delivery of 1 parcel with a charge weight of 0.856 kg Base Charge R 3.00 Waybill Surcharge R 5.50 Fuel Surcharge 34.82 % R 6.30 Sub Total R 1.80 VAT 15 % R 1.62 Grand Total R 16.13 Pay fees R16.13   With the RAM App, you can see the current status of your package and the next step..  RAM Transport (South Africa) (Proprietary) Limited t/a RAM Hand-to-Hand Couriers Regards,Terri-Leigh Fisher  Online Customer Service Representative  Online Customer Service Tel: 0861 726 726  Fax: 0861 726 726 Mobile: 0861 726 726 Email: Terri-Leigh.Fisher@ram.co.za  Branch:  Isando
```

> lure: parcel_fee
> specific: A06, A07, A08
> general: A03
> labeled_by: claude+author(整批同意)

---

## T02  (test index 177)  資料集標籤：phishing / human  挑選類別：包裹運費

```
=?UTF-8?B?4pyIIEZlZEV4IMKpIFNoaXBtZW50IE5vdGlmaWNhdGlvbiAzODQ3ODkyOTk=?=

1/8/2021 6:32:41 a.m. Dear Customer, Your package has been returned to the FedEx Office.The reason for the return is - payment of shipping costs. the cost of your shipment is not paid . so you will be charged to pay handling cost 6,53 $ (USD)You have a period of 48 hours to recover your package, otherwise it will be returned to the sender.Click here to view the status of your shipment : https:/fedex.com/en-fr/tracking/domestic/cost-shipping/384789299FedEx Support Team
```

> lure: parcel_fee
> specific: A06, A07, A08
> general: A03
> labeled_by: claude+author(整批同意)
> note: 冒充 FedEx

---

## T03  (test index 62)  資料集標籤：phishing / llm  挑選類別：發票催款

```
Dear David, We hope this email finds you in good health. We are writing to inform you that there is an outstanding payment for invoice #54321. To avoid any disruptions, please make the payment by clicking on the following link: https://invoice-payment-link.com If you have any questions or concerns, please do not hesitate to contact us. Best regards, Jessica Collins
```

> lure: invoice_overdue
> specific: A09, A10
> general: A03
> labeled_by: claude+author(整批同意)

---

## T04  (test index 167)  資料集標籤：phishing / llm  挑選類別：中獎

```
Dear John, Congratulations! You have been selected as the lucky winner of our Ultimate Vacation Getaway! Your jaw-dropping prize includes an all-expenses-paid trip to a luxurious resort in the Caribbean. To claim your prize, simply click on the following link and provide us with your contact details: Claim Your Prize Now: https://ultimate-vacation-claim.com Act quickly, as this exclusive offer expires in 48 hours. Don't miss out on this once-in-a-lifetime opportunity! Best regards, Emily Johnson
```

> lure: reward_curiosity
> specific: A12, A13
> general: A03
> labeled_by: claude+author(整批同意)

---

## T05  (test index 15)  資料集標籤：phishing / llm  挑選類別：退稅

```
Dear Mr. Simmons, We have received your tax refund request, and we are pleased to inform you that it has been approved. To proceed with the confirmation process and receive your refund of $2,200, please click on the following link: https://refund-confirmation-portal.com. This link will direct you to our secure portal, where you will be required to provide your personal and banking details. We appreciate your prompt response. Best regards, Matthew Thompson
```

> lure: reward_curiosity
> specific: A14, A15
> general: A03, A11
> labeled_by: claude+author(整批同意)
> note: 要求提供個人與銀行資料，符合 A11「要你確認個人或財務資料」

---

## T06  (test index 1)  資料集標籤：phishing / llm  挑選類別：求職

```
Dear Job Seeker, We have come across your impressive resume and are pleased to inform you of a potential job opportunity. Our company is currently seeking qualified candidates for a high-paying position that matches your skill set. To apply for this position, please reply to this email with your updated resume and a brief cover letter highlighting your relevant experience. Our hiring team will review your application and contact you for further steps if you meet our criteria. We look forward to hearing from you soon. Best regards, Recruitment Team
```

> lure: reward_curiosity
> specific: A16, A17
> general: 
> labeled_by: claude+author(整批同意)
> note: 要你回信附履歷，沒有連結，也沒要個人或財務資料，所以沒有通用警示

---

## T07  (test index 185)  資料集標籤：phishing / llm  挑選類別：求職

```
Hi Olivia, Are you tired of the corporate grind? Our company, Freedom Lifestyle Enterprises, is offering an incredible work-from-home opportunity that allows you to achieve financial freedom while maintaining a flexible schedule. If you're ready to break free from the traditional 9-5 routine, click on the link below to learn more about this life-changing opportunity: https://freedomlifestyle-opportunity.com Don't miss out on the chance to live life on your own terms! Best regards, Matthew Lewis
```

> lure: reward_curiosity
> specific: A16, A17
> general: A03
> labeled_by: claude+author(整批同意)
> note: 在家工作機會

---

## T08  (test index 70)  資料集標籤：phishing / llm  挑選類別：投資

```
Dear Samantha, I hope this email finds you well. I am writing to you today with an extraordinary investment opportunity that has been exclusively curated for individuals like yourself who are part of the elite few. Our team of financial experts has uncovered a hidden gem in the market – an investment opportunity with immense potential for exponential growth. However, due to its exclusivity, we can only offer this opportunity to a limited number of individuals. To gain access to detailed information about this exclusive investment opportunity, including a comprehensive prospectus and expert analysis, please click on the following link: https://exclusive-investment-link.com Please note that this opportunity is time-sensitive, and spots are filling up quickly. Don't miss out on the chance to secure your financial future. Best regards, Richard Thompson
```

> lure: reward_curiosity
> specific: A18
> general: A03
> labeled_by: claude+author(整批同意)

---

## T09  (test index 148)  資料集標籤：phishing / llm  挑選類別：慈善捐款

```
Dear Michael, I hope this email finds you in good health and high spirits. My name is Jennifer Thompson, and I am reaching out to you on behalf of the War Victims Relief Fund. We are dedicated to providing immediate aid and support to those affected by the devastating consequences of war. In light of recent events, we have identified a critical need for emergency assistance in war-torn regions. We have been impressed with your commitment to humanitarian causes in the past, and we believe that together, we can make a significant impact on the lives of countless individuals and families. Our organization is currently working tirelessly to provide essential resources such as food, clean water, medical supplies, and shelter to those who have been displaced or injured due to the ongoing conflicts. However, the scale of the crisis far exceeds our available resources, and we are in desperate need of additional funding to continue our vital work. We understand that generosity comes in many forms, and we are humbly requesting your support during this critical time. Your contribution, no matter the size, will enable us to provide immediate assistance to those who need it most and help rebuild shattered lives. To make a secure donation and offer a lifeline of hope to war victims, we kindly ask you to click on the following link: [https://warvictimsrelief.org/donate] We assure you that every penny donated will be used judiciously and in accordance with our organization's strict financial guidelines. Additionally, we would be honored to recognize your generosity by including your name in our list of esteemed donors, showcasing the impact that compassionate individuals like yourself can have on the lives of those in need. Thank you for taking the time to consider our urgent appeal. Together, we can bring light to the darkest corners of our world and make a tangible difference in the lives of war victims. If you have any questions or would like to learn more about our organization's work, please do not hesitate to reach out. With sincere gratitude, Jennifer Thompson War Victims Relief Fund
```

> lure: charity
> specific: A19, A20
> general: A03
> labeled_by: claude+author(整批同意)
> note: 戰爭救援捐款

---

## T10  (test index 109)  資料集標籤：phishing / human  挑選類別：帳單付款

```
We're having some trouble with your current billing information 

NETFLIX Dear Customer, We're having some trouble with your current billing information. We'll try again, but in the meantime you may want to update your payment details.                                                  UPDATE YOUR DETAILS   


  NETFLIX 


Dear Customer, 

We're having some trouble with your current billing information. 

We'll try again, but in the meantime you may want to update your payment details. 

 UPDATE YOUR DETAILS                NETFLIX Dear Customer, We're having some trouble with your current billing information. We'll try again, but in the meantime you may want to update your payment details.                                                  UPDATE YOUR DETAILS
```

> lure: billing_problem
> specific: A05
> general: A03, A11
> labeled_by: claude+author(整批同意)
