# 招數卡考試結果（正式數字）

執行時間：2026-11-05T01:28:17　計分 48 封（排除 0 封標籤錯誤）

| 指標 | 數值 |
|---|---|
| 誘餌正確率 | 0.708 |
| 手法 precision / recall / F1 | 0.615 / 0.533 / 0.571 |
| 帳號到期 / 安全警告 / 信箱錯誤 互相混淆 | 3 次 |
| 沒有招數的信被套上招數（新版） | 6 / 19 |
| 沒有招數的信被列出釣魚指標（舊版） | 5 / 19 |
| 引用的證據不在信裡 | 2 / 101 |
| JSON 解析失敗（新版） | 0 |

## 逐封結果

| # | 標準答案 | 模型 | 誘餌 |
|---|---|---|---|
| E01 | security_alert + credential_link, urgency | security_alert + credential_link, impersonation | ✅ |
| E02 | none | none | ✅ |
| E03 | mailbox_error + malicious_link, urgency | mailbox_error + credential_link | ✅ |
| E04 | charity + malicious_link, payment_request | reward_curiosity + credential_link | ❌ |
| E05 | none | none | ✅ |
| E06 | none | none | ✅ |
| E07 | reward_curiosity + malicious_link, urgency | reward_curiosity + malicious_link | ✅ |
| E08 | reward_curiosity + malicious_link, urgency | reward_curiosity + malicious_link, urgency | ✅ |
| E09 | none | none | ✅ |
| E10 | legal_threat + credential_link, urgency | security_alert + credential_link, urgency | ❌ |
| E11 | account_expiry + credential_link, urgency, impersonation | account_expiry + credential_link, impersonation | ✅ |
| E12 | none | reward_curiosity + malicious_link | ❌ |
| E13 | account_expiry + credential_link, urgency, impersonation | account_expiry + credential_link, urgency | ✅ |
| E14 | account_expiry + credential_link, urgency, impersonation | account_expiry + credential_link, urgency | ✅ |
| E15 | file_share + malicious_link, urgency, impersonation | file_share + credential_link, urgency | ✅ |
| E16 | account_expiry + credential_link, urgency, impersonation | （無效） + impersonation | ❌ |
| E17 | reward_curiosity + malicious_link, urgency | reward_curiosity + malicious_link, urgency | ✅ |
| E18 | reward_curiosity + malicious_link | reward_curiosity + malicious_link | ✅ |
| E19 | mailbox_error + malicious_link, impersonation | mailbox_error + credential_link, urgency | ✅ |
| E20 | none | none | ✅ |
| E21 | none | reward_curiosity + malicious_link | ❌ |
| E22 | billing_problem + credential_link | billing_problem + credential_link, impersonation | ✅ |
| E23 | invoice_overdue + payment_request, malicious_link | invoice_overdue + payment_request | ✅ |
| E24 | none | none | ✅ |
| E25 | account_expiry + reply_with_info | security_alert + reply_with_info, impersonation | ❌ |
| E26 | reward_curiosity + reply_with_info, urgency | reward_curiosity + reply_with_info | ✅ |
| E27 | none | charity + impersonation | ❌ |
| E28 | security_alert + credential_link, impersonation | security_alert + impersonation, credential_link | ✅ |
| E29 | reward_curiosity + malicious_link | reward_curiosity + malicious_link | ✅ |
| E30 | none | none | ✅ |
| E31 | reward_curiosity + malicious_link | reward_curiosity + malicious_link, impersonation | ✅ |
| E32 | none | none | ✅ |
| E33 | account_expiry + credential_link, urgency | security_alert + credential_link, impersonation | ❌ |
| E34 | security_alert + credential_link, urgency, impersonation | account_expiry + credential_link, impersonation | ❌ |
| E35 | none | none | ✅ |
| E36 | none | none | ✅ |
| E37 | none | none | ✅ |
| E38 | account_expiry + credential_link, urgency, impersonation | account_expiry + credential_link, impersonation | ✅ |
| E39 | none | none | ✅ |
| E40 | none | none | ✅ |
| E41 | reward_curiosity + malicious_link | reward_curiosity + credential_link | ✅ |
| E42 | none | reward_curiosity + reply_with_info | ❌ |
| E43 | account_expiry + malicious_link, urgency, impersonation | account_expiry + credential_link, impersonation | ✅ |
| E44 | security_alert + credential_link, urgency | security_alert + credential_link | ✅ |
| E45 | security_alert + credential_link | none | ❌ |
| E46 | none | reward_curiosity + malicious_link, impersonation | ❌ |
| E47 | none | security_alert + credential_link | ❌ |
| E48 | invoice_overdue + payment_request, malicious_link, urgency | （無效） + credential_link | ❌ |

## 分析

### 依來源拆開看

| | 人寫的信（24 封） | LLM 生成的信（24 封） |
|---|---|---|
| 誘餌正確率 | 22 / 24（92%） | 12 / 24（50%） |
| 沒有招數的信被套上招數（新版） | 0 / 12 | 6 / 7 |
| 沒有招數的信被列出釣魚指標（舊版） | 0 / 12 | 5 / 7 |

整體數字被 LLM 生成的信拉低。這批信的主題跟釣魚信重疊，例如研討會邀請、求職、合作洽談，而且大約一半的標籤疑似有誤。

### 正常信被亂套招數：新版沒有比舊版好

6 / 19 vs 5 / 19，差異在誤差範圍內。人寫的正常信新舊版都是 0，所以練習集上看到的改善（人寫正常信 1 → 0）在考試集沒有重現。

被套錯的 6 封全是 LLM 生成的信，證據也都很弱，例如用「I hope this email finds you in good spirits」當作利誘的證據。這印證了驗證機制的限制：句子真的在信裡，但不能支持這個招數。

### 引用證據不在信裡：2 / 101，兩次都發生在 E16，原因不同

E16 在字母之間塞了大量零寬字元，還用西里爾字母假冒英文字母（е、а、о、і、Р）。

- 「Keep My Password」（相似度 0.75）：信裡是西里爾字母拼成的 Kееp / Раssword。模型引用時寫成正常英文，但 _normalize() 當時只清掉零寬字元，沒有把西里爾字母轉回拉丁字母，所以比對失敗。這是**驗證程式的缺口**，不是模型編造。
- 「Your password has expired.」（相似度 0.897）：信件主旨是「Your email password has expired.」，模型漏掉了「email」，剛好低於 0.9 的門檻。這是**模型改寫原句**，跟西里爾字母無關，被丟掉是合理的。

所以完全憑空編造的證據是 0 次；不是一字不差引用的有 1 次。

**考試後修正（不影響上面的正式數字）**：_normalize() 加上外型相近字元的對照表（西里爾、希臘字母 → 拉丁字母），依外型而不是發音轉換。修正效果用單元測試展示（tests/test_cot_module.py：「Keep My Password」對 E16 原文的相似度 0.75 → 1.0），沒有重跑這 48 封。

另外加了 find_homoglyph_words()：一個單字裡同時混用拉丁字母和外型相近的西里爾/希臘字母時，就標記出來。在 train/val/test 共 4,000 封信上，正常信 0 / 2,000 封被標記，人寫的釣魚信 26 / 1,000 封被標記。這個訊號在這份資料上沒有誤判，但涵蓋率低，所以只能當作補充證據。

### 手法錯誤的主要來源

- 帶連結騙帳密 / 誘導點擊連結 互相混淆（多標 8 次、漏標 8 次）：預標規則是「信裡有寫登入、驗證才算騙帳密」，模型則把「取回郵件」、「看文件」的按鈕也當成騙帳密。這有一部分是規則定義的差異。
- 急迫漏標 12 次：模型標急迫比預標保守。
- 假冒身分多標 7 次：仍然會把沒有名字的「Security Team」、署名當成假冒。
- E48：模型把手法 id payment_request 填進誘餌欄位（id 混用，被程式擋下）。

### 已知限制

- 標準答案由 Claude 預標、作者複核，只有一位標註者，沒有計算標註者間一致性。
- 包裹運費、附件、慈善捐款在 48 封中出現 0～1 次，無法評估各類別的表現。
- E10（防疫接觸者追蹤）沒有適合的誘餌卡，標準答案勉強標成 legal_threat。
- 這份結果之後若修改 prompt、卡片或驗證程式，需要另抽新的考試集，不能重跑這一份當正式數字。
