# Learn Claude Code — 最快學習路徑指南（繁體中文）

## 整體架構總覽

```mermaid
graph TB
    subgraph 核心概念
        A[Agency 來自模型訓練<br/>不是外部程式碼]
    end

    subgraph Agent產品
        B[Agent 產品 = 模型 + Harness]
        B1[模型 = 駕駛者<br/>決策、推理]
        B2[Harness = 載具<br/>工具、知識、權限]
    end

    A --> B
    B --> B1
    B --> B2

    subgraph Harness組成
        H1[Tools<br/>檔案讀寫 / Shell / 網路]
        H2[Knowledge<br/>產品文件 / API 規範]
        H3[Observation<br/>git diff / 錯誤日誌]
        H4[Action<br/>CLI 命令 / API 呼叫]
        H5[Permissions<br/>沙箱隔離 / 信任邊界]
    end

    B2 --> H1
    B2 --> H2
    B2 --> H3
    B2 --> H4
    B2 --> H5
```

---

## 學習路徑流程圖

```mermaid
flowchart TD
    Start([開始學習]) --> P1

    subgraph P1[第一階段：核心骨架 ~1-2 小時]
        S01[s01: Agent Loop<br/>一個迴圈 + Bash = Agent]
        S02[s02: Tool Use<br/>工具擴展，loop 不變]
        S03[s03: Todo Write<br/>先計劃再執行]
        S01 --> S02 --> S03
    end

    P1 -->|掌握骨架| Check1{時間有限？}
    Check1 -->|是| MVP[最小可行路徑<br/>s01 → s04 → s07]
    Check1 -->|否| P2

    subgraph P2[第二階段：進階機制 ~2-3 小時]
        S04[s04: Subagent<br/>子代理，獨立 context]
        S05[s05: Skill Loading<br/>按需載入知識]
        S06[s06: Context Compact<br/>三層壓縮策略]
        S07[s07: Task System<br/>檔案式任務圖 + 依賴]
        S04 --> S05 --> S06 --> S07
    end

    P2 --> P3

    subgraph P3[第三階段：多代理協作 ~2-3 小時]
        S08[s08: Background Tasks<br/>背景執行不阻塞]
        S09[s09: Agent Teams<br/>多代理 + 非同步信箱]
        S10[s10: Team Protocols<br/>團隊通訊協議]
        S11[s11: Autonomous Agents<br/>自主認領任務]
        S12[s12: Worktree Isolation<br/>平行執行互不干擾]
        S08 --> S09 --> S10 --> S11 --> S12
    end

    MVP --> Full
    P3 --> Full([完整版 agents/s_full.py])

    style P1 fill:#e8f5e9,stroke:#2e7d32
    style P2 fill:#e3f2fd,stroke:#1565c0
    style P3 fill:#fce4ec,stroke:#c62828
    style MVP fill:#fff3e0,stroke:#e65100
    style Full fill:#f3e5f5,stroke:#6a1b9a
```

---

## 核心 Agent Loop 運作流程

```mermaid
flowchart LR
    User([使用者]) -->|訊息| Messages[messages 陣列]
    Messages --> LLM[Claude 模型]
    LLM --> Response{stop_reason?}
    Response -->|tool_use| Execute[執行工具]
    Execute -->|結果加回 messages| Messages
    Response -->|end_turn| Return([回傳文字回應])
```

---

## 各 Session 對應的 Harness 機制

```mermaid
graph LR
    subgraph 第一階段
        s01[s01<br/>Agent Loop]
        s02[s02<br/>Tool Use]
        s03[s03<br/>Todo Write]
    end

    subgraph 第二階段
        s04[s04<br/>Subagent]
        s05[s05<br/>Skill Loading]
        s06[s06<br/>Context Compact]
        s07[s07<br/>Task System]
    end

    subgraph 第三階段
        s08[s08<br/>Background Tasks]
        s09[s09<br/>Agent Teams]
        s10[s10<br/>Team Protocols]
        s11[s11<br/>Autonomous Agents]
        s12[s12<br/>Worktree Isolation]
    end

    s01 -->|加工具| s02
    s02 -->|加計劃| s03
    s03 -->|加子代理| s04
    s04 -->|加知識| s05
    s05 -->|加壓縮| s06
    s06 -->|加任務| s07
    s07 -->|加背景| s08
    s08 -->|加團隊| s09
    s09 -->|加協議| s10
    s10 -->|加自主| s11
    s11 -->|加隔離| s12

    style s01 fill:#c8e6c9
    style s02 fill:#c8e6c9
    style s03 fill:#c8e6c9
    style s04 fill:#bbdefb
    style s05 fill:#bbdefb
    style s06 fill:#bbdefb
    style s07 fill:#bbdefb
    style s08 fill:#ffcdd2
    style s09 fill:#ffcdd2
    style s10 fill:#ffcdd2
    style s11 fill:#ffcdd2
    style s12 fill:#ffcdd2
```

---

## 最小可行路徑（時間極有限時）

```mermaid
flowchart LR
    S01[s01: Agent Loop<br/>理解核心迴圈] -->|跳到| S04[s04: Subagent<br/>理解任務拆解]
    S04 -->|跳到| S07[s07: Task System<br/>理解任務管理]
    S07 -->|對照| Full[s_full.py<br/>完整整合版]

    style S01 fill:#fff9c4,stroke:#f57f17
    style S04 fill:#fff9c4,stroke:#f57f17
    style S07 fill:#fff9c4,stroke:#f57f17
    style Full fill:#e1bee7,stroke:#6a1b9a
```

> **只讀 3 個檔案，即可掌握 Claude Code 80% 的設計精髓。**

---

## 每個 Session 的程式碼檔案對照

| 階段 | Session | 程式碼 | 核心概念 | 口號 |
|------|---------|--------|----------|------|
| 核心 | s01 | `agents/s01_agent_loop.py` | Agent Loop | 一個迴圈 + Bash 就是一切 |
| 核心 | s02 | `agents/s02_tool_use.py` | 工具擴展 | 加工具就是加一個 handler |
| 核心 | s03 | `agents/s03_todo_write.py` | 計劃能力 | 沒有計劃的 agent 會漂移 |
| 進階 | s04 | `agents/s04_subagent.py` | 子代理 | 大任務拆小，各用乾淨 context |
| 進階 | s05 | `agents/s05_skill_loading.py` | 知識載入 | 需要時載入，不是一開始就塞 |
| 進階 | s06 | `agents/s06_context_compact.py` | 上下文壓縮 | Context 會滿，你需要騰空間 |
| 進階 | s07 | `agents/s07_task_system.py` | 任務系統 | 大目標拆小任務，排序，持久化 |
| 協作 | s08 | `agents/s08_background_tasks.py` | 背景執行 | 慢操作丟背景，agent 繼續思考 |
| 協作 | s09 | `agents/s09_agent_teams.py` | 代理團隊 | 任務太大就委派給隊友 |
| 協作 | s10 | `agents/s10_team_protocols.py` | 團隊協議 | 隊友需要共同的通訊規則 |
| 協作 | s11 | `agents/s11_autonomous_agents.py` | 自主代理 | 隊友自己掃看板、認領任務 |
| 協作 | s12 | `agents/s12_worktree_task_isolation.py` | 工作樹隔離 | 各做各的目錄，互不干擾 |

---

## 建議的實際操作方式

1. **先跑 `s01`** — 確認你能用 Anthropic API 跑通最小 agent loop
2. **逐個 session 往上疊** — 每個 session 只加一個概念，diff 前後兩個檔案看差異最有效
3. **看完整版 `agents/s_full.py`** — 所有機制整合後的完整版，對照理解全貌
4. **閱讀對應文件** — 每個 session 在 `docs/` 目錄有詳細說明文件
