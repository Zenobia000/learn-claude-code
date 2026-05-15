# s08: Background Tasks (背景任務)

`s01 > s02 > s03 > s04 > s05 > s06 | s07 > [ s08 ] s09 > s10 > s11 > s12`

> *"慢操作丟背景, agent 繼續想下一步"* -- 背景執行緒跑命令, 完成後注入通知。
>
> **Harness 層**: 背景執行 -- 模型繼續思考, harness 負責等待。

## 問題

有些命令要跑好幾分鐘: `npm install`、`pytest`、`docker build`。阻塞式迴圈下模型只能乾等。使用者說 "裝依賴, 順便建個設定檔", Agent 卻只能一個一個來。

## 解決方案

```
Main thread                Background thread
+-----------------+        +-----------------+
| agent loop      |        | subprocess runs |
| ...             |        | ...             |
| [LLM call] <---+------- | enqueue(result) |
|  ^drain queue   |        +-----------------+
+-----------------+

Timeline:
Agent --[spawn A]--[spawn B]--[other work]----
             |          |
             v          v
          [A runs]   [B runs]      (parallel)
             |          |
             +-- results injected before next LLM call --+
```

## 工作原理

1. BackgroundManager 用執行緒安全的通知佇列追蹤任務。

```python
class BackgroundManager:
    def __init__(self):
        self.tasks = {}
        self._notification_queue = []
        self._lock = threading.Lock()
```

2. `run()` 啟動守護執行緒, 立即回傳。

```python
def run(self, command: str) -> str:
    task_id = str(uuid.uuid4())[:8]
    self.tasks[task_id] = {"status": "running", "command": command}
    thread = threading.Thread(
        target=self._execute, args=(task_id, command), daemon=True)
    thread.start()
    return f"Background task {task_id} started"
```

3. 子程序完成後, 結果進入通知佇列。

```python
def _execute(self, task_id, command):
    try:
        r = subprocess.run(command, shell=True, cwd=WORKDIR,
            capture_output=True, text=True, timeout=300)
        output = (r.stdout + r.stderr).strip()[:50000]
    except subprocess.TimeoutExpired:
        output = "Error: Timeout (300s)"
    with self._lock:
        self._notification_queue.append({
            "task_id": task_id, "result": output[:500]})
```

4. 每次 LLM 呼叫前排空通知佇列。

```python
def agent_loop(messages: list):
    while True:
        notifs = BG.drain_notifications()
        if notifs:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['result']}" for n in notifs)
            messages.append({"role": "user",
                "content": f"<background-results>\n{notif_text}\n"
                           f"</background-results>"})
        response = client.messages.create(...)
```

迴圈保持單執行緒。只有子程序 I/O 被並行化。

## 相對 s07 的變更

| 組件           | 之前 (s07)       | 之後 (s08)                         |
|----------------|------------------|------------------------------------|
| Tools          | 8                | 6 (基礎 + background_run + check)  |
| 執行方式       | 僅阻塞           | 阻塞 + 背景執行緒                  |
| 通知機制       | 無               | 每輪排空的佇列                     |
| 並行           | 無               | 守護執行緒                         |

## 試一試

```sh
cd learn-claude-code
python agents/s08_background_tasks.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Run "sleep 5 && echo done" in the background, then create a file while it runs`
2. `Start 3 background tasks: "sleep 2", "sleep 4", "sleep 6". Check their status.`
3. `Run pytest in the background and keep working on other things`
