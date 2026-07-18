# Coding Agent 與 Harness 工程 -- 教學計畫書

**版本**: v0.3（2026-07-18）
**教材基礎**: 本 repo（learn-claude-code）12 個 session + `docs/zh-tw/` 文件，投影片內容完全基於此 repo
**授課形式**: 實體 1 小時講授（素材通用於直播 / 錄播）
**投影片產出**: PowerPoint 組版 + gpt-image-2 生圖（`~/.claude/skills/draw/draw.py`，API key 讀 `~/.openai.env`）
**版權**: © 2026 桑尼資料科學 Sunny Data Science，版權所有（見第 6.4 節聲明全文）

---

## 1. 課程定位

### 1.1 學員輪廓

| 已具備 | 尚未接觸 |
|--------|----------|
| Python 基礎 | Agent loop 的實作原理 |
| 深度學習概念（非底層理論） | Tool use / stop_reason 驅動的控制流 |
| 雲端 LLM API 應用經驗（打 API、下 prompt） | Context 工程（子代理、按需載入、壓縮） |
| 做過 fine-tuning 專案 | Multi-agent 協作原理（委派、協議、隔離） |

### 1.2 核心認知缺口（課程切入點）

學員的使用模式停在**單輪 API 應用**：組 prompt、打 API、拿回應。
但業界主流已經不是「套 API 打 prompt」-- 是 **coding agent**：模型在迴圈裡
自己讀檔、跑指令、看結果、修正，直到任務完成。

課程主軸一句話：**「從打 API 的人，變成設計 agent loop 的人。」**

重心配置（依此輪廓調整）：
- **模型底層原理點到為止** -- 只需一個結論：agency 來自模型訓練，不用進理論
- **火力集中在 harness 設計** -- agent loop 怎麼寫、12 個機制怎麼疊
- **Multi-agent 原理完整講** -- 委派、通訊協議、自主認領、隔離，這是與單 API 應用差距最大的部分

### 1.3 課程目標（結業時學員能做到）

1. 徒手寫出最小 agent loop（30 行內），解釋 `stop_reason` 驅動的控制流
2. 說出 Claude Code 每個功能（TodoWrite、Subagent、Skill、Compact、Task…）對應的 harness 機制與其解決的問題
3. 講出 multi-agent 系統的四個核心問題與解法：怎麼委派（teams）、怎麼溝通（protocols）、怎麼分工（autonomous）、怎麼不打架（worktree isolation）
4. 課後用整合版 `agents/s_full.py` 對真實 repo 完成一個開發任務

---

## 2. 教學設計原理

### 2.1 單一遞增原則（教材已內建）

每個 session 只加**一個**機制，agent loop 從 s01 到 s12 始終不變。
學員永遠只需理解一個新概念，舊知識是穩定地基。

```
s01 loop → +工具 → +計劃 → +子代理 → +知識 → +壓縮 → +任務
         → +背景 → +團隊 → +協議 → +自主 → +隔離 → s_full.py
```

### 2.2 學術教學式敘事：觀念 → 作法 → 目的

不走顧問簡報的 one-page summary 路線。三幕式：

1. **觀念**：Agent 是什麼、harness 是什麼（建立心智模型）
2. **作法**：迴圈怎麼寫、機制怎麼疊（把心智模型落到程式碼）
3. **目的**：為什麼要會造 harness（收斂到工程價值）

### 2.3 提問停頓與節奏

三幕之間與轉折點用「提問停頓頁」銜接 -- 頁面只有一個問題，留 30–60 秒
讓學員先想，下一頁揭曉。每頁只推進一個念頭，但頁面不空：
每頁必有一個圖解或一段 ≤ 15 行的程式碼作為錨點。

---

## 3. 授課形式與載體分工

**單場 1 小時講授**，投影片 **28 頁**（上限 30）。深度不塞進投影片：

| 載體 | 角色 | 分量 |
|------|------|------|
| 投影片（1 小時講授） | 觀念骨架 + 現場 demo + 節奏控制 | 28 頁 |
| 影片（課後自學） | 每個 session 的深度 walkthrough | 14 支 × 8–15 分鐘 |
| repo 本身 | 動手實作、diff 對照、練習 | 12 支程式 + 文件 |

配速：60 分鐘 / 28 頁 ≈ 每頁 2 分鐘；其中 4 頁是提問停頓頁（各 30–60 秒），
2 頁是現場 demo（各約 4 分鐘）。

---

## 4. 投影片規劃（28 頁，三幕式）

### 4.1 頁面清單

**第一幕：觀念 -- Agent 是什麼（頁 1–7，約 12 分鐘）**

| 頁 | 內容 | 型態 |
|----|------|------|
| 1 | 封面：Coding Agent 與 Harness 工程 | 標題 |
| 2 | 你們熟悉的世界：組 prompt → 打 API → 拿回應（單輪呼叫） | 圖解 |
| 3 | **提問停頓**：「你呼叫過的 LLM API，為什麼不會自己改你的程式碼？」 | 停頓 |
| 4 | Agent 產品 = 模型（駕駛者）+ Harness（載具）；agency 來自訓練，一句帶過 | 圖解 |
| 5 | Harness 五要素：Tools / Knowledge / Observation / Action / Permissions | 圖解 |
| 6 | 反例：prompt chain / node graph 為什麼不是 agent | 對比圖 |
| 7 | **提問停頓**：「那最小可行的 agent，程式碼長什麼樣？」 | 停頓 |

**第二幕：作法 -- 一個迴圈疊 12 個機制（頁 8–23，約 38 分鐘）**

| 頁 | 內容 | 型態 |
|----|------|------|
| 8 | 答案：一個迴圈。30 行。（轉場） | 轉場 |
| 9 | Agent loop 全圖：messages → LLM → stop_reason → tools → 回圈 | 圖解 |
| 10 | s01 的 30 行逐段解讀（while True / stop_reason / tool_result） | 程式碼 |
| 11 | **現場 demo**：`python agents/s01_agent_loop.py` 跑通一個任務 | demo |
| 12 | 機制地圖：12 sessions 三階段，迴圈始終不變 | 地圖 |
| 13 | 骨架層（s02–s03）：加工具 = 加 handler；沒有計劃的 agent 會漂移 → TodoWrite | 圖+碼 |
| 14 | **提問停頓**：「任務越做越長，context 會發生什麼事？」 | 停頓 |
| 15 | Context 工程（s04–s06）：subagent 乾淨 context、skill 按需載入、compact 騰空間 | 圖解 |
| 16 | 對應真實功能：這三招就是 Claude Code 的 Task / Skills / /compact | 對照表 |
| 17 | 任務系統（s07–s08）：檔案式任務圖 + 依賴；慢操作丟背景不阻塞 | 圖解 |
| 18 | **提問停頓**：「一個 agent 不夠用的時候呢？」 | 停頓 |
| 19 | Multi-agent 原理 I（s09）：委派給隊友 -- 每個隊友獨立 context + 非同步信箱 | 圖解 |
| 20 | Multi-agent 原理 II（s10–s11）：通訊協議（共同規則）與自主認領（掃看板上工） | 圖解 |
| 21 | Multi-agent 原理 III（s12）：平行改檔會打架 → worktree 隔離，各做各的目錄 | 圖解 |
| 22 | `s_full.py`：12 個機制全部疊起來，740 行 = 一個 Claude Code 雛形 | 結構圖 |
| 23 | **現場 demo**：s_full.py 執行一個含委派的任務 | demo |

**第三幕：目的 -- 為什麼要會造載具（頁 24–28，約 10 分鐘）**

| 頁 | 內容 | 型態 |
|----|------|------|
| 24 | 關鍵洞察：12 個機制疊完，agent loop 一行都沒改 | 收束 |
| 25 | 換模型不換 harness：改 `.env` 一行即換 MiniMax / GLM / Kimi / DeepSeek | 證明 |
| 26 | 課後實作（三梯度作業）+ 自學地圖（影片 × 文件 × 最小路徑 s01→s04→s07） | 作業 |
| 27 | 總結：Agency 是學出來的，Harness 是工程出來的 | 收束 |
| 28 | Q&A + 版權聲明頁 | 結尾 |

### 4.2 機制束的錨點口號（頁 12–21 使用，亦為影片各集標題）

| Session | 錨點口號 | 對應 Claude Code 功能 |
|---------|----------|----------------------|
| s01 | 一個迴圈 + Bash 就是一切 | Agent 本體 |
| s02 | 加工具 = 加一個 handler | Read / Write / Edit 工具 |
| s03 | 沒有計劃的 agent 會漂移 | TodoWrite |
| s04 | 大任務拆小，各用乾淨 context | Task / Subagent |
| s05 | 需要時載入，不是一開始就塞 | Skills / CLAUDE.md |
| s06 | Context 會滿，你需要騰空間 | /compact |
| s07 | 大目標拆小任務、排序、持久化 | Task system |
| s08 | 慢操作丟背景，agent 繼續思考 | Background tasks |
| s09 | 任務太大就委派給隊友 | Agent teams |
| s10 | 隊友需要共同的通訊規則 | Team protocols |
| s11 | 隊友自己掃看板、認領任務 | Autonomous agents |
| s12 | 各做各的目錄，互不干擾 | Git worktree isolation |

---

## 5. 影片規劃與提示詞

### 5.1 影片結構

每個 session 一支影片，**8–15 分鐘**，共 14 支（總覽 1 + sessions 12 + 實戰 1）。
投影片負責 1 小時的地圖，影片承載每個機制的完整深度。

每支影片固定五段式：

1. **Hook（30–60 秒）**：痛點場景，「上一集的 agent 在這種情況會壞掉」
2. **概念（2–3 分鐘）**：機制圖解 + 錨點口號
3. **Code walkthrough（3–5 分鐘）**：螢幕錄影，重點走與前一集的 diff
4. **Live run（2–3 分鐘）**：實際跑 `python agents/sNN_xxx.py`，展示行為差異
5. **Recap + 預告（1 分鐘）**：一句話總結 + 下一集的痛點預告

### 5.2 影片腳本產生用 Meta-Prompt（範本）

```
你是一位資深的 AI 工程講師，正在為「Coding Agent 與 Harness 工程」課程錄製第 {N} 集影片腳本。

## 觀眾
會 Python、用過雲端 LLM API（打 API、下 prompt），
但從未看過 agent 產品的內部實作，對模型底層理論不熟 -- 不要進訓練原理。

## 本集主題
{session_id}: {title} -- 口號：「{slogan}」

## 素材（必讀）
- 概念文件：docs/zh-tw/{doc_file}
- 程式碼：agents/{code_file}
- 前一集程式碼（用於 diff）：agents/{prev_code_file}

## 腳本結構（總長 {duration} 分鐘）
1. Hook：描述「沒有{mechanism}時 agent 會怎麼壞」的具體場景
2. 概念：用「{analogy}」比喻解釋機制，畫面配合文件中的架構圖
3. Code walkthrough：只講與前一集的 diff，逐段解釋，每段 ≤ 20 行
4. Live run：執行 {demo_command}，旁白解說輸出中的關鍵行為
5. Recap：重複口號一次，預告下一集痛點：「{next_hook}」

## 風格要求
- 繁體中文口語，直接、零廢話
- 每個概念必須先給痛點再給機制，禁止先講抽象定義
- 對應到 Claude Code 真實功能時明確點名（例如「這就是你用的 TodoWrite」）
- 逐字稿含畫面指示（[畫面：...]）與停頓標記
```

### 5.3 每集變數表（節錄，完整表格隨提示詞檔產出）

| 集數 | session | 比喻（analogy） | demo 重點 |
|------|---------|------------------|-----------|
| EP01 | 總覽 | 駕駛者 vs 載具 | 成品展示 |
| EP02 | s01 | 你自己就是那個迴圈（手動貼結果） | 30 行 loop 跑通 |
| EP03 | s02 | 瑞士刀 vs 單一 Bash | 同任務工具選擇差異 |
| EP04 | s03 | 沒有待辦清單的裝修工人 | 長任務漂移對比 |
| EP05 | s04 | 主廚與備料廚師（各自的工作台） | context 汙染對比 |
| EP06 | s05 | 隨身手冊 vs 背整座圖書館 | token 用量對比 |
| EP07 | s06 | 筆記本寫滿了要謄重點 | 壓縮前後對話 |
| EP08 | s07 | 看板牆上的便利貼 | 任務依賴圖 |
| EP09 | s08 | 洗衣機轉的時候你去做別的事 | 阻塞 vs 非阻塞 |
| EP10 | s09 | 一個人蓋不完的房子 | 委派全流程 |
| EP11 | s10 | 工地無線電的通話規範 | 訊息協議 |
| EP12 | s11 | 自己看班表上工的員工 | 認領機制 |
| EP13 | s12 | 每人一間工作室 | 平行改檔不衝突 |
| EP14 | 實戰 | 從零件到整車 | s_full.py 對真實 repo 跑任務 |

---

## 6. 投影片視覺設計規範與產出流程

### 6.1 視覺設計系統（全 28 頁統一）

**設計哲學：每頁一個視覺焦點（自注意力式引導）** --
一頁只有一個高對比焦點元素（關鍵圖解、關鍵程式碼、關鍵一句話），
其餘元素降飽和、退到背景層，觀眾的視線自動被引到重點。

| 項目 | 規範 |
|------|------|
| 色彩 | 深色底（深藍黑 `#171C28`），主文字近白（`#E6E9F0`）；強調色**琥珀 `#FFB454`**（每頁唯一焦點色）；輔助色青 `#5CCFE6`（次要標記用，不與琥珀同時搶焦點） |
| 標題字 | Noto Sans TC Black / 微軟正黑 Bold，44–54 pt |
| 內文字 | Noto Sans TC Regular，20–28 pt，每頁 ≤ 6 行 |
| 程式碼 | JetBrains Mono（或 Cascadia Code），深色 code block，關鍵行以琥珀高亮 |
| Icon | 單色線性（outline、等粗線條），統一一套；焦點 icon 用琥珀，其餘用灰 |
| 視覺動線 | 由左上敘事區 → 中央焦點區 → 右下行動區；停頓頁例外：問題置中、四周留白 |
| 頁碼 | **不做**（講師於 PowerPoint 內自行嵌入） |
| 左下角 | 每頁固定放置**桑尼資料科學橫幅**（Sunny Data Science banner） |
| 右下角 | 版權角標：`© 2026 桑尼資料科學` 小字（12 pt，低對比灰） |

### 6.2 生圖與組版分工（重要）

gpt-image-2 在 low quality 下**中文文字容易變形**，因此嚴格分工：

- **生圖（draw.py）負責**：背景版式、圖解插畫、icon、示意圖 -- 畫面中不含中文字，
  或僅含大型英文標語（如 "ONE LOOP IS ALL YOU NEED"）
- **PowerPoint 負責**：所有中文文字（可編輯、可改版、零亂碼）、程式碼區塊、頁面組合

產出流程：

```
每頁生圖提示詞（course/slides/prompts/）
  → python ~/.claude/skills/draw/draw.py "<prompt>" --size 1536x1024 --name pXX
  → 輸出 PNG 至 slides/generated/
  → PowerPoint 匯入為底圖，疊中文文字與程式碼
```

參數基準：`--size 1536x1024`（16:9 投影）、`--quality low`（NT$0.3/張；
封面與關鍵圖解頁若需精緻可個別升 medium）。28 頁全 low 約 NT$9。

### 6.3 生圖提示詞的統一風格前綴（每頁提示詞共用）

```
Dark navy (#171C28) presentation slide background, flat vector illustration style,
thin-line monochrome icons, single amber (#FFB454) focal element with all other
elements desaturated gray-blue, generous negative space, clean grid layout,
16:9, no Chinese text, minimal English labels only
```

### 6.4 智慧財產權聲明

**投影片每頁**：右下角 `© 2026 桑尼資料科學` 角標。

**封面（頁 1）小字 + 版權聲明頁（頁 28）全文**：

> 本教材（含投影片、影片、講義、範例程式與其編排設計）由桑尼資料科學
> （Sunny Data Science）研發，受著作權法及相關智慧財產權法律保護。
> © 2026 桑尼資料科學，版權所有。
>
> 未經著作權人事前書面同意，不得以任何形式重製、改作、散布、公開傳輸、
> 公開播送或作商業使用。本教材僅授權課程學員為個人學習目的使用。
> 教材中引用之開源專案（learn-claude-code）依其原授權條款（見該 repo LICENSE）使用，
> 其著作權歸原作者所有。

---

## 7. 產出物與資料夾結構

所有課程產出集中在 repo 的 `course/` 目錄：

```
course/
├── 00-course-plan.md          # 本計畫書
├── 01-syllabus.md             # 課綱（學習目標、對應教材、作業）
├── slides/
│   ├── design-spec.md         # 視覺設計規範（6.1–6.3 的執行版）
│   ├── prompts/               # 每頁生圖提示詞 p01.md ... p28.md
│   ├── generated/             # draw.py 輸出的 PNG（PPT 底圖）
│   └── speaker-notes.md       # 每頁講稿要點（含停頓頁引導語）
├── video-prompts/
│   └── ep01.md ... ep14.md    # 每集影片腳本產生提示詞（meta-prompt 已填變數）
└── homework/
    ├── tasks.md               # 三梯度課後作業（用 s_full.py 對真實 repo）
    └── rubric.md              # 評分標準
```

---

## 8. 執行步驟（建議順序）

| 步驟 | 產出 | 說明 |
|------|------|------|
| 1. 計畫書定稿 | 本檔 | 待你審閱 |
| 2. 課綱 | `01-syllabus.md` | 依第 3–4 節展開 |
| 3. 設計規範 + 28 頁生圖提示詞 | `slides/design-spec.md`、`slides/prompts/` | 依第 6 節 |
| 4. 批次生圖 | `slides/generated/*.png` | draw.py，全 low 約 NT$9 |
| 5. 講稿要點 | `slides/speaker-notes.md` | 含停頓頁引導語與 demo 指令 |
| 6. 影片提示詞 | `video-prompts/ep01–14.md` | 依 5.2 範本填變數 |
| 7. 作業教材 | `homework/` | 三梯度任務 + 評分標準 |

---

## 附錄：已確認事項

1. ~~image2API 位置~~ → 即 `~/.claude/skills/draw/`（draw.py + `~/.openai.env`），為投影片生圖工具
2. 授課形式：實體，素材通用於直播 / 錄播
3. 學員皆有 API key，對 AI 工具不陌生
4. 投影片工具：PowerPoint 組版，頁面視覺由 gpt-image-2 產出
5. 頁碼不做（講師自行於 PPT 嵌入）；左下角桑尼資料科學橫幅；含智財聲明
