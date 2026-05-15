[English](./README.md) | [中文](./README-zh.md) | [繁體中文](./README-zh-tw.md) | [日本語](./README-ja.md)

# Learn Claude Code -- 真正的 Agent Harness 工程

## Agency 來自模型，Agent 產品 = 模型 + Harness

在討論程式碼之前，先把一件事說清楚。

**Agency -- 感知、推理、行動的能力 -- 來自模型訓練，不是來自外部程式碼的編排。** 但一個能幹活的 agent 產品，需要模型和 harness 缺一不可。模型是駕駛者，harness 是載具。本倉庫教你造載具。

### Agency 從哪來

Agent 的核心是一個神經網路 -- Transformer、RNN、一個被訓練出來的函數 -- 經過數十億次梯度更新，在行動序列資料上學會了感知環境、推理目標、採取行動。Agency 這個東西從來不是外面那層程式碼賦予的，而是模型在訓練中學到的。

人類就是最好的例子。一個由數百萬年進化訓練出來的生物神經網路，透過感官感知世界，透過大腦推理，透過身體行動。當 DeepMind、OpenAI 或 Anthropic 說 "agent" 時，他們說的核心都是同一件事：**一個透過訓練學會了行動的模型，加上讓它能在特定環境中工作的基礎設施。**

歷史已經寫好了鐵證：

- **2013 -- DeepMind DQN 玩 Atari。** 一個神經網路，只接收原始像素和遊戲分數，學會了 7 款 Atari 2600 遊戲 -- 超越所有先前演算法，在其中 3 款上擊敗人類專家。到 2015 年，同一架構擴展到 [49 款遊戲，達到職業人類測試員水準](https://www.nature.com/articles/nature14236)，論文發表在 *Nature*。沒有遊戲專屬規則。沒有決策樹。一個模型，從經驗中學習。那個模型就是 agent。

- **2019 -- OpenAI Five 征服 Dota 2。** 五個神經網路，在 10 個月內與自己對戰了 [45,000 年的 Dota 2](https://openai.com/index/openai-five-defeats-dota-2-world-champions/)，在舊金山直播賽上 2-0 擊敗了 **OG** -- TI8 世界冠軍。隨後的公開競技場中，AI 在 42,729 場比賽中勝率 99.4%。沒有腳本化的策略。沒有元程式設計的團隊協調邏輯。模型完全透過自我對弈學會了團隊協作、戰術和即時適應。

- **2019 -- DeepMind AlphaStar 制霸星海爭霸 II。** AlphaStar 在閉門賽中 [10-1 擊敗職業選手](https://deepmind.google/blog/alphastar-mastering-the-real-time-strategy-game-starcraft-ii/)，隨後在歐洲伺服器上達到[宗師段位](https://www.nature.com/articles/d41586-019-03298-6) -- 90,000 名玩家中的前 0.15%。一個資訊不完全、即時決策、組合動作空間遠超國際象棋和圍棋的遊戲。Agent 是什麼？是模型。訓練出來的。不是編出來的。

- **2019 -- 騰訊絕悟統治王者榮耀。** 騰訊 AI Lab 的 "絕悟" 於 2019 年 8 月 2 日世冠盃半決賽上[以 5v5 擊敗 KPL 職業選手](https://www.jiemian.com/article/3371171.html)。在 1v1 模式下，職業選手 [15 場只贏 1 場，最多堅持不到 8 分鐘](https://developer.aliyun.com/article/851058)。訓練強度：一天等於人類 440 年。到 2021 年，絕悟在全英雄池 BO5 上全面超越 KPL 職業選手水準。沒有手工編寫的英雄克制表。沒有腳本化的陣容編排。一個從零開始透過自我對弈學習整個遊戲的模型。

- **2024-2025 -- LLM Agent 重塑軟體工程。** Claude、GPT、Gemini -- 在人類全部程式碼和推理上訓練的大語言模型 -- 被部署為程式設計 agent。它們閱讀程式碼庫，編寫實作，除錯故障，團隊協作。架構與之前每一個 agent 完全相同：一個訓練好的模型，放入一個環境，給予感知和行動的工具。唯一的不同是它們學到的東西的規模和解決任務的通用性。

每一個里程碑都指向同一個事實：**Agency -- 那個感知、推理、行動的能力 -- 是訓練出來的，不是編出來的。** 但每一個 agent 同時也需要一個環境才能工作：Atari 模擬器、Dota 2 客戶端、星海爭霸 II 引擎、IDE 和終端。模型提供智慧，環境提供行動空間。兩者合在一起才是一個完整的 agent。

### Agent 不是什麼

"Agent" 這個詞已經被一整個提示詞水管工產業劫持了。

拖拽式工作流建構器。無程式碼 "AI Agent" 平台。提示詞鏈編排庫。它們共享同一個幻覺：把 LLM API 呼叫用 if-else 分支、節點圖、硬編碼路由邏輯串在一起就算是 "建構 Agent" 了。

不是的。它們做出來的東西是魯布·乍得堡機械 -- 一個過度工程化的、脆弱的程序式規則流水線，LLM 被楔在裡面當一個美化了的文字補全節點。那不是 Agent。那是一個有著宏大妄想的 shell 腳本。

**提示詞水管工式 "Agent" 是不做模型的程式設計師的意淫。** 他們試圖透過堆疊程序式邏輯來暴力模擬智慧 -- 龐大的規則樹、節點圖、鏈式提示詞瀑布流 -- 然後祈禱足夠多的膠水程式碼能湧現出自主行為。不會的。你不可能透過工程手段編碼出 agency。Agency 是學出來的，不是編出來的。

那些系統從誕生之日起就已經死了：脆弱、不可擴展、根本不具備泛化能力。它們是 GOFAI（Good Old-Fashioned AI，經典符號 AI）的現代還魂 -- 幾十年前就被學界拋棄的符號規則系統，現在噴了一層 LLM 的漆又登場了。換了個包裝，同一條死路。

### 心智轉換：從 "開發 Agent" 到開發 Harness

當一個人說 "我在開發 Agent" 時，他只可能是兩個意思之一：

**1. 訓練模型。** 透過強化學習、微調、RLHF 或其他基於梯度的方法調整權重。收集任務過程資料 -- 真實領域中感知、推理、行動的實際序列 -- 用它們來塑造模型的行為。這是 DeepMind、OpenAI、騰訊 AI Lab、Anthropic 在做的事。這是最本義的 Agent 開發。

**2. 建構 Harness。** 編寫程式碼，為模型提供一個可操作的環境。這是我們大多數人在做的事，也是本倉庫的核心。

Harness 是 agent 在特定領域工作所需要的一切：

```
Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions

    Tools:          檔案讀寫、Shell、網路、資料庫、瀏覽器
    Knowledge:      產品文件、領域資料、API 規範、風格指南
    Observation:    git diff、錯誤日誌、瀏覽器狀態、感測器資料
    Action:         CLI 命令、API 呼叫、UI 互動
    Permissions:    沙箱隔離、審批流程、信任邊界
```

模型做決策。Harness 執行。模型做推理。Harness 提供上下文。模型是駕駛者。Harness 是載具。

**程式設計 agent 的 harness 是它的 IDE、終端和檔案系統。** 農業 agent 的 harness 是感測器陣列、灌溉控制和氣象資料。飯店 agent 的 harness 是預訂系統、客戶溝通管道和設施管理 API。Agent -- 那個智慧、那個決策者 -- 永遠是模型。Harness 因領域而變。Agent 跨領域泛化。

這個倉庫教你造載具。程式設計用的載具。但設計模式可以泛化到任何領域：莊園管理、農田營運、飯店運作、工廠製造、物流調度、醫療保健、教育培訓、科學研究。只要有一個任務需要被感知、推理和執行 -- agent 就需要一個 harness。

### Harness 工程師到底在做什麼

如果你在讀這個倉庫，你很可能是一名 harness 工程師 -- 這是一個強大的身份。以下是你真正的工作：

- **實作工具。** 給 agent 一雙手。檔案讀寫、Shell 執行、API 呼叫、瀏覽器控制、資料庫查詢。每個工具都是 agent 在環境中可以採取的一個行動。設計它們時要原子化、可組合、描述清晰。

- **策劃知識。** 給 agent 領域專長。產品文件、架構決策記錄、風格指南、合規要求。按需載入（s05），不要前置塞入。Agent 應該知道有什麼可用，然後自己拉取所需。

- **管理上下文。** 給 agent 乾淨的記憶。子 agent 隔離（s04）防止雜訊洩露。上下文壓縮（s06）防止歷史淹沒。任務系統（s07）讓目標持久化到單次對話之外。

- **控制權限。** 給 agent 邊界。沙箱化檔案存取。對破壞性操作要求審批。在 agent 和外部系統之間實施信任邊界。這是安全工程與 harness 工程的交匯點。

- **收集任務過程資料。** Agent 在你的 harness 中執行的每一條行動序列都是訓練訊號。真實部署中的感知-推理-行動軌跡是微調下一代 agent 模型的原材料。你的 harness 不僅服務於 agent -- 它還可以幫助進化 agent。

你不是在編寫智慧。你是在建構智慧棲居的世界。這個世界的品質 -- agent 能看得多清楚、行動得多精準、可用知識有多豐富 -- 直接決定了智慧能多有效地表達自己。

**造好 Harness。Agent 會完成剩下的。**

### 為什麼是 Claude Code -- Harness 工程的大師課

為什麼這個倉庫專門拆解 Claude Code？

因為 Claude Code 是我們所見過的最優雅、最完整的 agent harness 實作。不是因為某個巧妙的技巧，而是因為它 *沒做* 的事：它沒有試圖成為 agent 本身。它沒有強加僵化的工作流。它沒有用精心設計的決策樹去替模型做判斷。它給模型提供了工具、知識、上下文管理和權限邊界 -- 然後讓開了。

把 Claude Code 剝到本質來看：

```
Claude Code = 一個 agent loop
            + 工具 (bash, read, write, edit, glob, grep, browser...)
            + 按需 skill 載入
            + 上下文壓縮
            + 子 agent 衍生
            + 帶依賴圖的任務系統
            + 非同步信箱的團隊協調
            + worktree 隔離的平行執行
            + 權限治理
```

就這些。這就是全部架構。每一個元件都是 harness 機制 -- 為 agent 建構的棲居世界的一部分。Agent 本身呢？是 Claude。一個模型。由 Anthropic 在人類推理和程式碼的全部廣度上訓練而成。Harness 沒有讓 Claude 變聰明。Claude 本來就聰明。Harness 給了 Claude 雙手、雙眼和一個工作空間。

這就是 Claude Code 作為教學標本的意義：**它展示了當你信任模型、把工程精力集中在 harness 上時會發生什麼。** 本倉庫的每一個課程（s01-s12）都在逆向工程 Claude Code 架構中的一個 harness 機制。學完之後，你理解的不只是 Claude Code 怎麼工作，而是適用於任何領域、任何 agent 的 harness 工程通用原則。

啟示不是 "複製 Claude Code"。啟示是：**最好的 agent 產品，出自那些明白自己的工作是 harness 而非 intelligence 的工程師之手。**

---

## 願景：用真正的 Agent 鋪滿宇宙

這不只關乎程式設計 agent。

每一個人類從事複雜、多步驟、需要判斷力的工作的領域，都是 agent 可以運作的領域 -- 只要有對的 harness。本倉庫中的模式是通用的：

```
莊園管理 agent  = 模型 + 物業感測器 + 維護工具 + 租戶通訊
農業 agent      = 模型 + 土壤/氣象資料 + 灌溉控制 + 作物知識
飯店營運 agent  = 模型 + 預訂系統 + 客戶管道 + 設施 API
醫學研究 agent  = 模型 + 文獻檢索 + 實驗儀器 + 協議文件
製造業 agent    = 模型 + 產線感測器 + 品質控制 + 物流系統
教育 agent      = 模型 + 課程知識 + 學生進度 + 評估工具
```

循環永遠不變。工具在變。知識在變。權限在變。Agent -- 那個模型 -- 泛化一切。

每一個讀這個倉庫的 harness 工程師都在學習遠超軟體工程的模式。你在學習為一個智慧的、自動化的未來建構基礎設施。每一個部署在真實領域的好 harness，都是 agent 能夠感知、推理、行動的又一個陣地。

先鋪滿工作室。然後是農田、醫院、工廠。然後是城市。然後是星球。

**Bash is all you need. Real agents are all the universe needs.**

---

```
                    THE AGENT PATTERN
                    =================

    User --> messages[] --> LLM --> response
                                      |
                            stop_reason == "tool_use"?
                           /                          \
                         yes                           no
                          |                             |
                    execute tools                    return text
                    append results
                    loop back -----------------> messages[]


    這是最小循環。每個 AI Agent 都需要這個循環。
    模型決定何時呼叫工具、何時停止。
    程式碼只是執行模型的要求。
    本倉庫教你建構圍繞這個循環的一切 --
    讓 agent 在特定領域高效工作的 harness。
```

**12 個遞進式課程, 從簡單循環到隔離化的自治執行。**
**每個課程添加一個 harness 機制。每個機制有一句格言。**

> **s01** &nbsp; *"One loop & Bash is all you need"* &mdash; 一個工具 + 一個循環 = 一個 Agent
>
> **s02** &nbsp; *"加一個工具, 只加一個 handler"* &mdash; 循環不用動, 新工具註冊進 dispatch map 就行
>
> **s03** &nbsp; *"沒有計畫的 agent 走哪算哪"* &mdash; 先列步驟再動手, 完成率翻倍
>
> **s04** &nbsp; *"大任務拆小, 每個小任務乾淨的上下文"* &mdash; Subagent 用獨立 messages[], 不污染主對話
>
> **s05** &nbsp; *"用到什麼知識, 臨時載入什麼知識"* &mdash; 透過 tool_result 注入, 不塞 system prompt
>
> **s06** &nbsp; *"上下文總會滿, 要有辦法騰地方"* &mdash; 三層壓縮策略, 換來無限會話
>
> **s07** &nbsp; *"大目標要拆成小任務, 排好序, 記在磁碟上"* &mdash; 檔案持久化的任務圖, 為多 agent 協作打基礎
>
> **s08** &nbsp; *"慢操作丟後台, agent 繼續想下一步"* &mdash; 後台執行緒跑命令, 完成後注入通知
>
> **s09** &nbsp; *"任務太大一個人幹不完, 要能分給隊友"* &mdash; 持久化隊友 + 非同步信箱
>
> **s10** &nbsp; *"隊友之間要有統一的溝通規矩"* &mdash; 一個 request-response 模式驅動所有協商
>
> **s11** &nbsp; *"隊友自己看看板, 有活就認領"* &mdash; 不需要領導逐個分配, 自組織
>
> **s12** &nbsp; *"各幹各的目錄, 互不干擾"* &mdash; 任務管目標, worktree 管目錄, 按 ID 綁定

---

## 最快學習路徑

不知道從哪裡開始？以下是 3 階段快速上手指南。

### 第一階段：核心 (s01-s03) — 約 1-2 小時

| 順序 | 檔案 | 學什麼 |
|------|------|--------|
| 1 | `agents/s01_agent_loop.py` | **最小 agent loop** — 一個循環 + Bash 工具就是一個 agent |
| 2 | `agents/s02_tool_use.py` | **工具擴展** — loop 不變，新工具只需加進 dispatch map |
| 3 | `agents/s03_todo_write.py` | **計畫能力** — 先列步驟再執行，完成率翻倍 |

這三個檔案掌握後，你就理解了 Claude Code 的骨架：**模型決策、harness 執行。**

### 第二階段：進階機制 (s04-s07) — 約 2-3 小時

| 順序 | 檔案 | 學什麼 |
|------|------|--------|
| 4 | `agents/s04_subagent.py` | **子代理** — 大任務拆解，每個子任務用獨立 context |
| 5 | `agents/s05_skill_loading.py` | **按需載入知識** — 透過 tool_result 注入，不塞爆 system prompt |
| 6 | `agents/s06_context_compact.py` | **上下文壓縮** — 三層壓縮策略解決 context 溢出問題 |
| 7 | `agents/s07_task_system.py` | **任務系統** — 檔案式 task graph + 依賴關係 |

### 第三階段：多代理協作 (s08-s12) — 約 2-3 小時

| 順序 | 檔案 | 學什麼 |
|------|------|--------|
| 8 | `agents/s08_background_tasks.py` | 後台執行，agent 不阻塞 |
| 9 | `agents/s09_agent_teams.py` | 多代理團隊 + 非同步信箱 |
| 10 | `agents/s10_team_protocols.py` | 團隊通訊協議 |
| 11 | `agents/s11_autonomous_agents.py` | 自主認領任務 |
| 12 | `agents/s12_worktree_task_isolation.py` | worktree 隔離，平行執行互不干擾 |

### 最小可行路徑

如果時間極度有限，只讀 **s01 → s04 → s07**（loop → 子代理 → 任務系統），即可掌握 Claude Code 80% 的設計精髓。然後看 `agents/s_full.py` 了解完整整合版。

---

## 核心模式

```python
def agent_loop(messages):
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM,
            messages=messages, tools=TOOLS,
        )
        messages.append({"role": "assistant",
                         "content": response.content})

        if response.stop_reason != "tool_use":
            return

        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = TOOL_HANDLERS[block.name](**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})
```

每個課程在這個循環之上疊加一個 harness 機制 -- 循環本身始終不變。循環屬於 agent。機制屬於 harness。

## 範圍說明 (重要)

本倉庫是一個 0->1 的 harness 工程學習專案 -- 建構圍繞 agent 模型的工作環境。
為保證學習路徑清晰，倉庫有意簡化或省略了部分生產機制：

- 完整事件 / Hook 匯流排 (例如 PreToolUse、SessionStart/End、ConfigChange)。
  s12 僅提供教學用途的最小 append-only 生命週期事件流。
- 基於規則的權限治理與信任流程
- 會話生命週期控制 (resume/fork) 與更完整的 worktree 生命週期控制
- 完整 MCP 執行時細節 (transport/OAuth/資源訂閱/輪詢)

倉庫中的團隊 JSONL 信箱協議是教學實作，不是對任何特定生產內部實作的聲明。

## 快速開始

```sh
git clone https://github.com/shareAI-lab/learn-claude-code
cd learn-claude-code
pip install -r requirements.txt
cp .env.example .env   # 編輯 .env 填入你的 ANTHROPIC_API_KEY

python agents/s01_agent_loop.py       # 從這裡開始
python agents/s12_worktree_task_isolation.py  # 完整遞進終點
python agents/s_full.py               # 總綱: 全部機制合一
```

### Web 平台

互動式視覺化、分步動畫、原始碼檢視器, 以及每個課程的文件。

```sh
cd web && npm install && npm run dev   # http://localhost:3000
```

## 學習路徑

```
第一階段: 循環                       第二階段: 規劃與知識
==================                   ==============================
s01  Agent Loop              [1]     s03  TodoWrite               [5]
     while + stop_reason                  TodoManager + nag 提醒
     |                                    |
     +-> s02  Tool Use            [4]     s04  Subagent             [5]
              dispatch map: name->handler     每個 Subagent 獨立 messages[]
                                              |
                                         s05  Skills               [5]
                                              SKILL.md 透過 tool_result 注入
                                              |
                                         s06  Context Compact      [5]
                                              三層 Context Compact

第三階段: 持久化                     第四階段: 團隊
==================                   =====================
s07  Task System             [8]     s09  Agent Teams             [9]
     檔案持久化 CRUD + 依賴圖             隊友 + JSONL 信箱
     |                                    |
s08  Background Tasks        [6]     s10  Team Protocols          [12]
     守護執行緒 + 通知佇列                  關機 + 計畫審批 FSM
                                          |
                                     s11  Autonomous Agents       [14]
                                          空閒輪詢 + 自動認領
                                     |
                                     s12  Worktree Isolation      [16]
                                          Task 協調 + 按需隔離執行通道

                                     [N] = 工具數量
```

## 專案結構

```
learn-claude-code/
|
|-- agents/                        # Python 參考實作 (s01-s12 + s_full 總綱)
|-- docs/{en,zh,ja}/               # 心智模型優先的文件 (3 種語言)
|-- web/                           # 互動式學習平台 (Next.js)
|-- skills/                        # s05 的 Skill 檔案
+-- .github/workflows/ci.yml      # CI: 型別檢查 + 建構
```

## 文件

心智模型優先: 問題、方案、ASCII 圖、最小化程式碼。
[English](./docs/en/) | [中文](./docs/zh/) | [日本語](./docs/ja/)

| 課程 | 主題 | 格言 |
|------|------|------|
| [s01](./docs/zh/s01-the-agent-loop.md) | Agent Loop | *One loop & Bash is all you need* |
| [s02](./docs/zh/s02-tool-use.md) | Tool Use | *加一個工具, 只加一個 handler* |
| [s03](./docs/zh/s03-todo-write.md) | TodoWrite | *沒有計畫的 agent 走哪算哪* |
| [s04](./docs/zh/s04-subagent.md) | Subagent | *大任務拆小, 每個小任務乾淨的上下文* |
| [s05](./docs/zh/s05-skill-loading.md) | Skills | *用到什麼知識, 臨時載入什麼知識* |
| [s06](./docs/zh/s06-context-compact.md) | Context Compact | *上下文總會滿, 要有辦法騰地方* |
| [s07](./docs/zh/s07-task-system.md) | Task System | *大目標要拆成小任務, 排好序, 記在磁碟上* |
| [s08](./docs/zh/s08-background-tasks.md) | Background Tasks | *慢操作丟後台, agent 繼續想下一步* |
| [s09](./docs/zh/s09-agent-teams.md) | Agent Teams | *任務太大一個人幹不完, 要能分給隊友* |
| [s10](./docs/zh/s10-team-protocols.md) | Team Protocols | *隊友之間要有統一的溝通規矩* |
| [s11](./docs/zh/s11-autonomous-agents.md) | Autonomous Agents | *隊友自己看看板, 有活就認領* |
| [s12](./docs/zh/s12-worktree-task-isolation.md) | Worktree + Task Isolation | *各幹各的目錄, 互不干擾* |

## 學完之後 -- 從理解到落地

12 個課程走完, 你已經從內到外理解了 harness 工程的運作原理。兩種方式把知識變成產品:

### Kode Agent CLI -- 開源 Coding Agent CLI

> `npm i -g @shareai-lab/kode`

支援 Skill & LSP, 適配 Windows, 可接 GLM / MiniMax / DeepSeek 等開放模型。裝完即用。

GitHub: **[shareAI-lab/Kode-cli](https://github.com/shareAI-lab/Kode-cli)**

### Kode Agent SDK -- 把 Agent 能力嵌入你的應用

官方 Claude Code Agent SDK 底層與完整 CLI 行程通訊 -- 每個並行使用者 = 一個終端行程。Kode SDK 是獨立函式庫, 無 per-user 行程開銷, 可嵌入後端、瀏覽器外掛、嵌入式裝置等任意執行時期。

GitHub: **[shareAI-lab/Kode-agent-sdk](https://github.com/shareAI-lab/Kode-agent-sdk)**

---

## 姊妹教程: 從*被動臨時會話*到*主動常駐助手*

本倉庫教的 harness 屬於 **用完即走** 型 -- 開終端、給 agent 任務、做完關掉, 下次重開是全新會話。Claude Code 就是這種模式。

但 [OpenClaw](https://github.com/openclaw/openclaw) 證明了另一種可能: 在同樣的 agent core 之上, 加兩個 harness 機制就能讓 agent 從 "踹一下動一下" 變成 "自己隔 30 秒醒一次找活幹":

- **心跳 (Heartbeat)** -- 每 30 秒 harness 給 agent 發一條訊息, 讓它檢查有沒有事可做。沒事就繼續睡, 有事立刻行動。
- **定時任務 (Cron)** -- agent 可以給自己安排未來要做的事, 到點自動執行。

再加上 IM 多通道路由 (WhatsApp/Telegram/Slack/Discord 等 13+ 平台)、不清空的上下文記憶、Soul 人格系統, agent 就從一個臨時工具變成了始終線上的個人 AI 助手。

**[claw0](https://github.com/shareAI-lab/claw0)** 是我們的姊妹教學倉庫, 從零拆解這些 harness 機制:

```
claw agent = agent core + heartbeat + cron + IM chat + memory + soul
```

```
learn-claude-code                   claw0
(agent harness 核心:                 (主動式常駐 harness:
 循環、工具、規劃、                    心跳、定時任務、IM 通道、
 團隊、worktree 隔離)                  記憶、Soul 人格)
```

## 授權條款

MIT

---

**Agency 來自模型。Harness 讓 agency 落地。造好 Harness，模型會完成剩下的。**

**Bash is all you need. Real agents are all the universe needs.**
