# s04: Subagents (Subagent)

`s01 > s02 > s03 > [ s04 ] s05 > s06 | s07 > s08 > s09 > s10 > s11 > s12`

> *"大任務拆小, 每個小任務乾淨的上下文"* -- Subagent 用獨立 messages[], 不汙染主對話。
>
> **Harness 層**: 上下文隔離 -- 守護模型的思維清晰度。

## 問題

Agent 工作越久, messages 陣列越臃腫。每次讀檔案、跑命令的輸出都永久留在上下文裡。「這個專案用什麼測試框架?」可能要讀 5 個檔案, 但父 Agent 只需要一個詞: "pytest。"

## 解決方案

```
Parent agent                     Subagent
+------------------+             +------------------+
| messages=[...]   |             | messages=[]      | <-- fresh
|                  |  dispatch   |                  |
| tool: task       | ----------> | while tool_use:  |
|   prompt="..."   |             |   call tools     |
|                  |  summary    |   append results |
|   result = "..." | <---------- | return last text |
+------------------+             +------------------+

Parent context stays clean. Subagent context is discarded.
```

## 工作原理

1. 父 Agent 有一個 `task` 工具。Subagent 擁有除 `task` 外的所有基礎工具 (禁止遞迴生成)。

```python
PARENT_TOOLS = CHILD_TOOLS + [
    {"name": "task",
     "description": "Spawn a subagent with fresh context.",
     "input_schema": {
         "type": "object",
         "properties": {"prompt": {"type": "string"}},
         "required": ["prompt"],
     }},
]
```

2. Subagent 以 `messages=[]` 啟動, 執行自己的迴圈。只有最終文字返回給父 Agent。

```python
def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,
            tools=CHILD_TOOLS, max_tokens=8000,
        )
        sub_messages.append({"role": "assistant",
                             "content": response.content})
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input)
                results.append({"type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output)[:50000]})
        sub_messages.append({"role": "user", "content": results})
    return "".join(
        b.text for b in response.content if hasattr(b, "text")
    ) or "(no summary)"
```

Subagent 可能跑了 30+ 次工具呼叫, 但整個訊息歷史直接丟棄。父 Agent 收到的只是一段摘要文字, 作為普通 `tool_result` 返回。

## 相對 s03 的變更

| 元件           | 之前 (s03)       | 之後 (s04)                    |
|----------------|------------------|-------------------------------|
| Tools          | 5                | 5 (基礎) + task (僅父端)      |
| 上下文         | 單一共享         | 父 + 子隔離                   |
| Subagent       | 無               | `run_subagent()` 函式         |
| 返回值         | 不適用           | 僅摘要文字                    |

## 試一試

```sh
cd learn-claude-code
python agents/s04_subagent.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Use a subtask to find what testing framework this project uses`
2. `Delegate: read all .py files and summarize what each one does`
3. `Use a task to create a new module, then verify it from here`
