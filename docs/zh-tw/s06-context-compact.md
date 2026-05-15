# s06: Context Compact (上下文壓縮)

`s01 > s02 > s03 > s04 > s05 > [ s06 ] | s07 > s08 > s09 > s10 > s11 > s12`

> *"上下文總會滿, 要有辦法騰地方"* -- 三層壓縮策略, 換來無限會話。
>
> **Harness 層**: 壓縮 -- 乾淨的記憶, 無限的會話。

## 問題

上下文視窗是有限的。讀一個 1000 行的檔案就吃掉 ~4000 token; 讀 30 個檔案、跑 20 條命令, 輕鬆突破 100k token。不壓縮, Agent 根本沒法在大專案裡幹活。

## 解決方案

三層壓縮, 激進程度遞增:

```
Every turn:
+------------------+
| Tool call result |
+------------------+
        |
        v
[Layer 1: micro_compact]        (silent, every turn)
  Replace tool_result > 3 turns old
  with "[Previous: used {tool_name}]"
        |
        v
[Check: tokens > 50000?]
   |               |
   no              yes
   |               |
   v               v
continue    [Layer 2: auto_compact]
              Save transcript to .transcripts/
              LLM summarizes conversation.
              Replace all messages with [summary].
                    |
                    v
            [Layer 3: compact tool]
              Model calls compact explicitly.
              Same summarization as auto_compact.
```

## 工作原理

1. **第一層 -- micro_compact**: 每次 LLM 呼叫前, 將舊的 tool result 替換為佔位符。

```python
def micro_compact(messages: list) -> list:
    tool_results = []
    for i, msg in enumerate(messages):
        if msg["role"] == "user" and isinstance(msg.get("content"), list):
            for j, part in enumerate(msg["content"]):
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    tool_results.append((i, j, part))
    if len(tool_results) <= KEEP_RECENT:
        return messages
    for _, _, part in tool_results[:-KEEP_RECENT]:
        if len(part.get("content", "")) > 100:
            part["content"] = f"[Previous: used {tool_name}]"
    return messages
```

2. **第二層 -- auto_compact**: token 超過閾值時, 儲存完整對話到磁碟, 讓 LLM 做摘要。

```python
def auto_compact(messages: list) -> list:
    # Save transcript for recovery
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    # LLM summarizes
    response = client.messages.create(
        model=MODEL,
        messages=[{"role": "user", "content":
            "Summarize this conversation for continuity..."
            + json.dumps(messages, default=str)[:80000]}],
        max_tokens=2000,
    )
    return [
        {"role": "user", "content": f"[Compressed]\n\n{response.content[0].text}"},
    ]
```

3. **第三層 -- manual compact**: `compact` 工具按需觸發同樣的摘要機制。

4. 迴圈整合三層:

```python
def agent_loop(messages: list):
    while True:
        micro_compact(messages)                        # Layer 1
        if estimate_tokens(messages) > THRESHOLD:
            messages[:] = auto_compact(messages)       # Layer 2
        response = client.messages.create(...)
        # ... tool execution ...
        if manual_compact:
            messages[:] = auto_compact(messages)       # Layer 3
```

完整歷史透過 transcript 儲存在磁碟上。資訊沒有真正丟失, 只是移出了活躍上下文。

## 相對 s05 的變更

| 元件           | 之前 (s05)       | 之後 (s06)                     |
|----------------|------------------|--------------------------------|
| Tools          | 5                | 5 (基礎 + compact)             |
| 上下文管理     | 無               | 三層壓縮                       |
| Micro-compact  | 無               | 舊結果 -> 佔位符               |
| Auto-compact   | 無               | token 閾值觸發                 |
| Transcripts    | 無               | 儲存到 .transcripts/           |

## 試一試

```sh
cd learn-claude-code
python agents/s06_context_compact.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Read every Python file in the agents/ directory one by one` (觀察 micro-compact 替換舊結果)
2. `Keep reading files until compression triggers automatically`
3. `Use the compact tool to manually compress the conversation`
