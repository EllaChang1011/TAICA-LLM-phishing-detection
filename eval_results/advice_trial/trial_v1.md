# 生成步驟試用：兩個模型並排

不是正式評測，只用來決定用哪個模型。每句都經過出處檢查；被丟掉的列在最後。

---

## T01 包裹運費（test 144）

顯示的警示：A08 0.616

### phishing-detector-14b（5.7 秒）

- **相同手法**：（沒有通過檢查）
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A08]", "email_quote": "Your shipment is on the way", "alert_quote": "Did you get a text message with a shipment tracking code and a link to update your delivery preferences? It's a scam. L`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A08]", "quote": "Con artists often use the names and logos of familiar organizations to get under your guard. So how do you tell what’s legit and what’s a scam? Here are some ways to spot `
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A08]", "quote": "Another sure sign an email is a scam? If you hover over the link in the email, it won’t show the official website of the supposed sender — in this case, the U.S. Postal Se`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A08]", "quote": "For more tips, check out our articles on phishing and malware. And if you have questions about a delivery by the U.S. Postal Service, visit usps.com or call 1-800-ASK-USPS`

### qwen3:14b（13.2 秒）

- **相同手法**：此郵件使用與[A08]相同的詐騙手法，偽裝成物流通知要求付款，實際為虛假資訊。（A08）
  - 信中原句：「Your package is stopped at our post A R 16.13 shipping cost have not been paid.」
  - 警示原句：「the email says you missed a delivery. But, it says, if you print the attached form and take it to your local post office, you can pick up your package and avoid penalties.」
- **建議**：此郵件包含「With the RAM App」的連結，應避免點擊或下載附件。（A08）
  - 警示原句：「It tells you to click on a link or download an attachment」
- **建議**：應檢查郵件中的連結是否指向RAM Transport官方網站（如ram.co.za），非官方網址即為詐騙。（A08）
  - 警示原句：「Another sure sign an email is a scam? If you hover over the link in the email, it won’t show the official website of the supposed sender」
- **建議**：如需確認物流資訊，應直接聯繫RAM Transport官方客服（如0861 726 726），勿依郵件指示操作。（A08）
  - 警示原句：「if you have questions about a delivery by the U.S. Postal Service, visit usps.com or call 1-800-ASK-USPS」

---

## T05 退稅（test 15）

顯示的警示：A14 0.675, A15 0.673

### phishing-detector-14b（7.7 秒）

- **相同手法**：（沒有通過檢查）
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "email_quote": "We have received your tax refund request, and we are pleased to inform you that it has been approved.", "alert_quote": "These scams often start with a text or email `
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "Know that the real IRS and state tax offices won’t reach out by text, email, or on social media to get your information. Only scammers will.", "text": "請注意，真正的國稅局和州稅務機構不會通`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "Don’t respond or click any links. To check the status of a pending tax refund, never use the link from the message.", "text": "請勿回應或點擊任何鏈接。要檢查待處理的稅款退還狀態，請勿使用消息中的鏈接。"}`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "If you clicked on a link in one of these messages, or you shared personal or financial information, report it at IdentityTheft.gov to get a free, customized recovery plan.`

### qwen3:14b（15.6 秒）

- **相同手法**：此電子郵件使用與A14相同的詐騙手法，偽裝成稅務機構通知用戶稅退款已獲批准，並誘導點擊連結。（A14）
  - 信中原句：「We have received your tax refund request, and we are pleased to inform you that it has been approved.」
  - 警示原句：「These scams often start with a text or email that looks like it’s from the IRS or a state tax office saying they’ve ‘processed’ or ‘approved’ your tax refund claim.」
- **建議**：不要回應或點擊連結，並透過USA.gov查詢稅退款狀態，而非使用訊息中的連結。（A14）
  - 警示原句：「Don’t respond or click any links. To check the status of a pending tax refund, never use the link from the message. Instead, visit USA.gov to learn how to find out if you’re really getting a federal or state tax refund.」
- **建議**：透過IRS官方網站（Where’s My Refund）查詢稅退款狀態，確認是否真的有退款。（A15）
  - 警示原句：「Check the status of any pending refund on the IRS official website. Visit Where’s My Refund to see if you’re really getting a refund.」
- **建議**：即使未受損，也應向FTC報告此詐騙行為，郵件地址為ReportFraud@ftc.gov。（A15）
  - 警示原句：「If you see this or any other a scam, even if you didn’t lose money, report it to the FTC at ReportFraud@ftc.gov.」

---

## T09 慈善捐款（test 148）

顯示的警示：A19 0.671, A20 0.656

### phishing-detector-14b（9.3 秒）

- **相同手法**：此郵件使用與[A19]相同的詐騙手法，透過提供一個假的捐款連結來誘導讀者進行捐款。（A19）
  - 信中原句：「To make a secure donation and offer a lifeline of hope to war victims, we kindly ask you to click on the following link: [https://warvictimsrelief.org/donate]」
  - 警示原句：「Before you donate: - Do some research. Search online for the cause you care about using terms like "hurricane relief" or "wildfire recovery." If you get a request to donate to a cause on social media, research that, too. Don't assume it's legitimate because a friend posted it.」
- ❌ 丟掉（quote_not_in_alert，score 0.422）：`{"alert": "A19", "quote": "Donate to charities you know and trust with a proven track record with responding to a humanitarian crisis.", "text": "捐款前請選擇您信任且有良好聲譽的慈善機構。"}`
- ❌ 丟掉（quote_not_in_alert，score 0.102）：`{"alert": "A19", "quote": "Research the organization — especially if the donation request comes on social media. Search the name plus \"complaint,\" \"review,\" \"rating,\" or \"scam.\" And check out `
- ❌ 丟掉（quote_not_in_alert，score 0.767）：`{"alert": "A19", "quote": "Don't donate to anyone who insists you pay by cash, gift card, wiring money, or cryptocurrency. That's how scammers tell you to pay.", "text": "請勿向堅持要求您以現金、禮品卡、電匯或加密貨幣付款的人捐款`

### qwen3:14b（13.3 秒）

- **相同手法**：此電子郵件使用與A19相同的詐騙手法，聲稱捐款將被嚴格用於援助，但未明確說明資金流向，與A19中提醒的‘確認捐款比例’相呼應。（A19）
  - 信中原句：「We assure you that every penny donated will be used judiciously and in accordance with our organization's strict financial guidelines.」
  - 警示原句：「Find out exactly how much of your donation goes directly to the people the charity says it helps.」
- **建議**：應先進行研究，透過網際網路搜尋相關慈善機構的資訊，例如使用‘戰爭援助’等關鍵字查詢。（A19）
  - 警示原句：「Do some research. Search online for the cause you care about using terms like “hurricane relief” or “wildfire recovery.”」
- **建議**：應透過Charity Watch或Give.org等平台查閱慈善機構的資訊，確認其是否為合法且長期存在的組織。（A19）
  - 警示原句：「Look charities up on Charity Watch or Give.org.」
- **建議**：若對方要求僅能以現金、禮券、匯款或加密貨幣捐款，應拒絕並懷疑其為詐騙。（A19）
  - 警示原句：「Don’t donate to anyone who says you can only pay by cash, gift card, wiring money, or cryptocurrency.」

---

## T10 Netflix 帳單（test 109）

顯示的警示：A05 0.668, A11 0.622

### phishing-detector-14b（8.9 秒）

- **相同手法**：（沒有通過檢查）
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A05]", "email_quote": "We're having some trouble with your current billing information.", "alert_quote": "Scammers often use familiar company names or pretend to be someone you know.", "te`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A05]", "quote": "Check it out. If you have concerns about the email, contact the company directly. But look up their phone number or website yourself. That way, you’ll know you’re getting `
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A05]", "quote": "Take a closer look. While some phishing emails look completely legit, bad grammar and spelling can tip you off to phishing. Other clues: Your name is missing, or you don’t`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A11]", "quote": "Don’t click on any links in unexpected emails or texts. If you’re concerned, contact the company directly using a link you already use or a phone number you know is correc`

### qwen3:14b（11.1 秒）

- **相同手法**：此郵件使用與[A05]相同的詐騙手法，聲稱帳戶因付款資訊問題被暫停，並誘導點擊連結。（A05）
  - 信中原句：「We're having some trouble with your current billing information」
  - 警示原句：「The email claims the user’s account is on hold because Netflix is “having some trouble with your current billing information” and invites the user to click on a link to update their payment method.」
- **建議**：應直接聯繫公司並自行查找官方聯絡方式，而非使用郵件中的連結。（A05）
  - 警示原句：「Check it out. If you have concerns about the email, contact the company directly. But look up their phone number or website yourself.」
- **建議**：不應點擊來歷不明郵件或簡訊中的連結。（A11）
  - 警示原句：「Don’t click on any links in unexpected emails or texts.」
- ❌ 丟掉（quote_not_in_alert，score 0.766）：`{"alert": "A05", "quote": "Report phishing emails. Forward them to spam@uce.gov ... and to reportphishing@apwg.org.", "text": "應將詐騙郵件轉寄至spam@uce.gov和reportphishing@apwg.org。"}`

---

## E07 標成正常的退稅詐騙（test 344）

顯示的警示：A14 0.723, A15 0.694

### phishing-detector-14b（8.2 秒）

- **相同手法**：（沒有通過檢查）
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "email_quote": "This is your last chance to claim your refund before the deadline passes.", "alert_quote": "To \"verify your identity\" and \"send you money,\" they ask you to click`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "To \"verify your identity\" and \"send you money,\" they ask you to click a link to enter details like your Social Security and bank account numbers — but it’s a phishing `
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "If you get a message like this: - Know that the real IRS and state tax offices won’t reach out by text, email, or on social media to get your information. Only scammers wi`
- ❌ 丟掉（alert_not_shown，score -）：`{"alert": "[A14]", "quote": "If you clicked on a link in one of these messages, or you shared personal or financial information, report it at IdentityTheft.gov to get a free, customized recovery plan.`

### qwen3:14b（13.0 秒）

- **相同手法**：此郵件使用與A14相同的詐騙手法，偽裝成稅務機構要求點擊連結以竊取個人資料。（A14）
  - 信中原句：「Click here to claim your tax refund before it's too late: [https://lastchanceclaimyourrefund.com/sarahjohnson]」
  - 警示原句：「These scams often start with a text or email that looks like it’s from the IRS or a state tax office saying they’ve ‘processed’ or ‘approved’ your tax refund claim.」
- **建議**：不要回應或點擊連結，應透過USA.gov查詢稅款退還狀態，而非使用郵件中的連結。（A14）
  - 警示原句：「Don’t respond or click any links. To check the status of a pending tax refund, never use the link from the message. Instead, visit USA.gov to learn how to find out if you’re really getting a federal or state tax refund.」
- **建議**：切勿點擊任何連結，以免惡意軟體竊取您的資訊。（A15）
  - 警示原句：「Never click on any links, which can put malware on your computer or phone, letting scammers steal from you.」
- **建議**：應透過IRS官方網站「Where’s My Refund」查詢退稅狀態，而非依賴來信內容。（A15）
  - 警示原句：「Check the status of any pending refund on the IRS official website. Visit Where’s My Refund to see if you’re really getting a refund.」

