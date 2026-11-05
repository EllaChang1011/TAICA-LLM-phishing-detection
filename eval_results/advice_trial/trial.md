# 生成步驟試用：兩個模型並排

不是正式評測，只用來決定用哪個模型。每句都經過出處檢查；被丟掉的列在最後。

## 試用結論（5 封，不是正式評測）

| | phishing-detector-14b | qwen3:14b |
|---|---|---|
| 「相同手法」通過檢查 | 5/5 | 5/5 |
| 建議通過 / 被丟掉 | 10 / 5 | 14 / 1 |
| 被丟掉的原因 | 主要是把 A20 的原句標成 A19、A15 的標成 A14（出處標錯，檢查有抓到） | 1 次原句裡用了「...」省略 |
| 用語 | 有大陸用語（鏈接、信息、短信、社交媒體） | 繁體用語 |
| 每封時間 | 約 8.5 秒 | 約 13 秒（含切換模型） |

第一版（trial_v1.md）phishing-detector-14b 幾乎全被丟掉，原因是它把編號寫成「[A14]」。檢查程式改成容忍中括號後重跑，才是上表的結果。

檢查抓不到的問題，人工閱讀時發現：E07 的 qwen3:14b 說這封信「偽裝成稅務機構」，但信裡寄件人自稱 Jonathan Lee，沒有冒充國稅局。引用的兩句原句都是真的，但連結它們的中文說法誇大了。這就是「出處屬實，但改寫不忠實」的例子。

---

## T01 包裹運費（test 144）

顯示的警示：A08 0.616

### phishing-detector-14b（8.8 秒）

- **相同手法**：此郵件聲稱您的包裹正在運輸途中，與[A08]中描述的假郵件一樣，聲稱您的包裹被扣留並要求支付費用。（A08）
  - 信中原句：「Your shipment is on the way」
  - 警示原句：「Did you get a text message with a shipment tracking code and a link to update your delivery preferences? It's a scam. Learn more.」
- **建議**：詐騙者經常使用知名組織的名稱和標誌來降低您的警惕。要識別合法郵件和詐騙郵件，可以參考[A08]中提到的識別方法。（A08）
  - 警示原句：「Con artists often use the names and logos of familiar organizations to get under your guard. So how do you tell what’s legit and what’s a scam? Here are some ways to spot a bogus email:」
- **建議**：如果郵件中的連結指向的不是聲稱發件人的官方網站，這是一個詐騙郵件的確鑿證據，如[A08]中所述。（A08）
  - 警示原句：「Another sure sign an email is a scam? If you hover over the link in the email, it won’t show the official website of the supposed sender — in this case, the U.S. Postal Service website.」
- **建議**：如需更多資訊，請閱讀[A08]中提到的有關釣魚郵件和惡意軟體的文章。如果您對美國郵政服務的投遞有任何疑問，請訪問usps.com或撥打1-800-ASK-USPS。（A08）
  - 警示原句：「For more tips, check out our articles on phishing and malware. And if you have questions about a delivery by the U.S. Postal Service, visit usps.com or call 1-800-ASK-USPS.」

### qwen3:14b（11.8 秒）

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

### phishing-detector-14b（8.3 秒）

- **相同手法**：這封電子郵件使用與[A14]相同的詐騙手法，聲稱稅款退還請求已被批准。（A14）
  - 信中原句：「We have received your tax refund request, and we are pleased to inform you that it has been approved.」
  - 警示原句：「These scams often start with a text or email that looks like it’s from the IRS or a state tax office saying they’ve “processed” or “approved” your tax refund claim.」
- **建議**：請注意，真正的國稅局和州稅務機構不會通過短信、電子郵件或社交媒體聯繫您以獲取您的個人信息，只有詐騙者才會這樣做。（A14）
  - 警示原句：「Know that the real IRS and state tax offices won’t reach out by text, email, or on social media to get your information. Only scammers will.」
- **建議**：請勿回應或點擊任何鏈接。要檢查待處理的稅款退還狀態，請勿使用消息中的鏈接。（A14）
  - 警示原句：「Don’t respond or click any links. To check the status of a pending tax refund, never use the link from the message.」
- ❌ 丟掉（quote_not_in_alert，score 0.432）：`{"alert": "[A14]", "quote": "If you clicked on a link in one of these messages, or you shared personal or financial information, report it at IdentityTheft.gov to get a free, customized recovery plan.`

### qwen3:14b（15.8 秒）

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

### phishing-detector-14b（9.6 秒）

- **相同手法**：此郵件使用與[A19]相同的詐騙手法，透過提供一個假的捐款連結來誘導讀者進行捐款。（A19）
  - 信中原句：「To make a secure donation and offer a lifeline of hope to war victims, we kindly ask you to click on the following link: [https://warvictimsrelief.org/donate]」
  - 警示原句：「Before you donate: - Do some research. Search online for the cause you care about using terms like "hurricane relief" or "wildfire recovery." If you get a request to donate to a cause on social media, research that, too. Don't assume it's legitimate because a friend posted it.」
- ❌ 丟掉（quote_not_in_alert，score 0.422）：`{"alert": "A19", "quote": "Donate to charities you know and trust with a proven track record with responding to a humanitarian crisis.", "text": "捐款前請選擇您信任且有良好聲譽的慈善機構。"}`
- ❌ 丟掉（quote_not_in_alert，score 0.102）：`{"alert": "A19", "quote": "Research the organization — especially if the donation request comes on social media. Search the name plus \"complaint,\" \"review,\" \"rating,\" or \"scam.\" And check out `
- ❌ 丟掉（quote_not_in_alert，score 0.767）：`{"alert": "A19", "quote": "Don't donate to anyone who insists you pay by cash, gift card, wiring money, or cryptocurrency. That's how scammers tell you to pay.", "text": "請勿向堅持要求您以現金、禮品卡、電匯或加密貨幣付款的人捐款`

### qwen3:14b（13.1 秒）

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

### phishing-detector-14b（8.7 秒）

- **相同手法**：這封郵件使用與[A05]相同的詐騙手法，利用用戶對帳戶問題的擔憂來誘導點擊。（A05）
  - 信中原句：「We're having some trouble with your current billing information.」
  - 警示原句：「Scammers often use familiar company names or pretend to be someone you know.」
- **建議**：如果對郵件內容有疑問，應直接聯繫公司，但要自行查找正確的電話號碼或網站，以避免聯繫詐騙者或點擊下載惡意軟體的連結。（A05）
  - 警示原句：「Check it out. If you have concerns about the email, contact the company directly. But look up their phone number or website yourself. That way, you’ll know you’re getting the real company and not about to call a scammer or follow a link that will download malware.」
- **建議**：檢查郵件的語法和拼寫，這些可能是詐騙郵件的跡象。例如，郵件中可能缺少您的姓名，或您根本沒有該公司的帳戶。（A05）
  - 警示原句：「Take a closer look. While some phishing emails look completely legit, bad grammar and spelling can tip you off to phishing. Other clues: Your name is missing, or you don’t even have an account with the company. In the Netflix example, the scammer used the British spelling of "Center" (Centre) and used the greeting, "Hi Dear." Listing only an international phone number for a U.S.-based company is also suspicious.」
- **建議**：不要點擊來自可疑郵件或簡訊的連結。如有疑慮，請使用您已知正確的連結或電話號碼直接聯繫公司。（A11）
  - 警示原句：「Don’t click on any links in unexpected emails or texts. If you’re concerned, contact the company directly using a link you already use or a phone number you know is correct.」

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

### phishing-detector-14b（8.6 秒）

- **相同手法**：這封電子郵件使用與[A14]相同的詐騙手法，利用最後機會聲稱可以領取稅款退款，誘導用戶點擊連結。（A14）
  - 信中原句：「This is your last chance to claim your refund before the deadline passes.」
  - 警示原句：「To "verify your identity" and "send you money," they ask you to click a link to enter details like your Social Security and bank account numbers — but it’s a phishing scam.」
- **建議**：不要點擊任何連結，因為這可能是 phishing 養魚網站，會讓詐騙者竊取您的個人資料。（A14）
  - 警示原句：「To "verify your identity" and "send you money," they ask you to click a link to enter details like your Social Security and bank account numbers — but it’s a phishing scam.」
- **建議**：請知道真正的 IRS 和州稅務機構不會透過簡訊、電子郵件或社交媒體聯繫您以取得您的個人資料，只有詐騙者才會這樣做。（A14）
  - 警示原句：「If you get a message like this: - Know that the real IRS and state tax offices won’t reach out by text, email, or on social media to get your information. Only scammers will.」
- ❌ 丟掉（quote_not_in_alert，score 0.432）：`{"alert": "[A14]", "quote": "If you clicked on a link in one of these messages, or you shared personal or financial information, report it at IdentityTheft.gov to get a free, customized recovery plan.`

### qwen3:14b（13.2 秒）

- **相同手法**：此郵件使用與A14相同的詐騙手法，偽裝成稅務機構要求點擊連結以竊取個人資料。（A14）
  - 信中原句：「Click here to claim your tax refund before it's too late: [https://lastchanceclaimyourrefund.com/sarahjohnson]」
  - 警示原句：「These scams often start with a text or email that looks like it’s from the IRS or a state tax office saying they’ve ‘processed’ or ‘approved’ your tax refund claim.」
- **建議**：不要回應或點擊連結，應透過USA.gov查詢稅款退還狀態，而非使用郵件中的連結。（A14）
  - 警示原句：「Don’t respond or click any links. To check the status of a pending tax refund, never use the link from the message. Instead, visit USA.gov to learn how to find out if you’re really getting a federal or state tax refund.」
- **建議**：切勿點擊任何連結，以免惡意軟體竊取您的資訊。（A15）
  - 警示原句：「Never click on any links, which can put malware on your computer or phone, letting scammers steal from you.」
- **建議**：應透過IRS官方網站「Where’s My Refund」查詢退稅狀態，而非依賴來信內容。（A15）
  - 警示原句：「Check the status of any pending refund on the IRS official website. Visit Where’s My Refund to see if you’re really getting a refund.」

