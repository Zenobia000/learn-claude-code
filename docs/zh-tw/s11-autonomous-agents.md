# s11: Autonomous Agents (Autonomous Agent)

`s01 > s02 > s03 > s04 > s05 > s06 | s07 > s08 > s09 > s10 > [ s11 ] s12`

> *"隊友自己看看板, 有活就認領"* -- 不需要領導逐個分配, 自組織。
>
> **Harness 層**: 自治 -- 模型自己找活幹, 無需指派。

## 問題

s09-s10 中, 隊友只在被明確指派時才動。領導得給每個隊友寫 prompt, 任務看板上 10 個未認領的任務得手動分配。這擴展不了。

真正的自治: 隊友自己掃描任務看板, 認領沒人做的任務, 做完再找下一個。

一個細節: Context Compact (s06) 後 Agent 可能忘了自己是誰。身份重注入解決這個問題。

## 解決方案

```
Teammate lifecycle with idle cycle:

+-------+
| spawn |
+---+---+
    |
    v
+-------+   tool_use     +-------+
| WORK  | <------------- |  LLM  |
+---+---+                +-------+
    |
    | stop_reason != tool_use (or idle tool called)
    v
+--------+
|  IDLE  |  poll every 5s for up to 60s
+---+----+
    |
    +---> check inbox --> message? ----------> WORK
    |
    +---> scan .tasks/ --> unclaimed? -------> claim -> WORK
    |
    +---> 60s timeout ----------------------> SHUTDOWN

Identity re-injection after compression:
  if len(messages) <= 3:
    messages.insert(0, identity_block)
```

## 工作原理

1. 隊友迴圈分兩個階段: WORK 和 IDLE。LLM 停止呼叫工具 (或呼叫了 `idle`) 時, 進入 IDLE。

```python
def _loop(self, name, role, prompt):
    while True:
        # -- WORK PHASE --
        messages = [{"role": "user", "content": prompt}]
        for _ in range(50):
            response = client.messages.create(...)
            if response.stop_reason != "tool_use":
                break
            # execute tools...
            if idle_requested:
                break

        # -- IDLE PHASE --
        self._set_status(name, "idle")
        resume = self._idle_poll(name, messages)
        if not resume:
            self._set_status(name, "shutdown")
            return
        self._set_status(name, "working")
```

2. 空閒階段迴圈輪詢收件匣和任務看板。

```python
def _idle_poll(self, name, messages):
    for _ in range(IDLE_TIMEOUT // POLL_INTERVAL):  # 60s / 5s = 12
        time.sleep(POLL_INTERVAL)
        inbox = BUS.read_inbox(name)
        if inbox:
            messages.append({"role": "user",
                "content": f"<inbox>{inbox}</inbox>"})
            return True
        unclaimed = scan_unclaimed_tasks()
        if unclaimed:
            claim_task(unclaimed[0]["id"], name)
            messages.append({"role": "user",
                "content": f"<auto-claimed>Task #{unclaimed[0]['id']}: "
                           f"{unclaimed[0]['subject']}</auto-claimed>"})
            return True
    return False  # timeout -> shutdown
```

3. 任務看板掃描: 找 pending 狀態、無 owner、未被阻塞的任務。

```python
def scan_unclaimed_tasks() -> list:
    unclaimed = []
    for f in sorted(TASKS_DIR.glob("task_*.json")):
        task = json.loads(f.read_text())
        if (task.get("status") == "pending"
                and not task.get("owner")
                and not task.get("blockedBy")):
            unclaimed.append(task)
    return unclaimed
```

4. 身份重注入: 上下文過短 (說明發生了壓縮) 時, 在開頭插入身份區塊。

```python
if len(messages) <= 3:
    messages.insert(0, {"role": "user",
        "content": f"<identity>You are '{name}', role: {role}, "
                   f"team: {team_name}. Continue your work.</identity>"})
    messages.insert(1, {"role": "assistant",
        "content": f"I am {name}. Continuing."})
```

## 相對 s10 的變更

| 組件           | 之前 (s10)       | 之後 (s11)                       |
|----------------|------------------|----------------------------------|
| Tools          | 12               | 14 (+idle, +claim_task)          |
| 自治性         | 領導指派         | 自組織                           |
| 空閒階段       | 無               | 輪詢收件匣 + 任務看板            |
| 任務認領       | 僅手動           | 自動認領未分配任務               |
| 身份           | 系統提示         | + 壓縮後重注入                   |
| 逾時           | 無               | 60 秒空閒 -> 自動關機            |

## 試一試

```sh
cd learn-claude-code
python agents/s11_autonomous_agents.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Create 3 tasks on the board, then spawn alice and bob. Watch them auto-claim.`
2. `Spawn a coder teammate and let it find work from the task board itself`
3. `Create tasks with dependencies. Watch teammates respect the blocked order.`
4. 輸入 `/tasks` 檢視帶 owner 的任務看板
5. 輸入 `/team` 監控誰在工作、誰在空閒
