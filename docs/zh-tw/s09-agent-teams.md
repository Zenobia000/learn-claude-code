# s09: Agent Teams (Agent 團隊)

`s01 > s02 > s03 > s04 > s05 > s06 | s07 > s08 > [ s09 ] s10 > s11 > s12`

> *"任務太大一個人幹不完, 要能分給隊友"* -- 持久化隊友 + JSONL 信箱。
>
> **Harness 層**: 團隊信箱 -- 多個模型, 透過檔案協調。

## 問題

Subagent (s04) 是一次性的: 產生、幹活、回傳摘要、消亡。沒有身份, 沒有跨呼叫的記憶。Background Tasks (s08) 能跑 shell 命令, 但做不了 LLM 引導的決策。

真正的團隊協作需要三樣東西: (1) 能跨多輪對話存活的持久 Agent, (2) 身份和生命週期管理, (3) Agent 之間的通訊通道。

## 解決方案

```
Teammate lifecycle:
  spawn -> WORKING -> IDLE -> WORKING -> ... -> SHUTDOWN

Communication:
  .team/
    config.json           <- team roster + statuses
    inbox/
      alice.jsonl         <- append-only, drain-on-read
      bob.jsonl
      lead.jsonl

              +--------+    send("alice","bob","...")    +--------+
              | alice  | -----------------------------> |  bob   |
              | loop   |    bob.jsonl << {json_line}    |  loop  |
              +--------+                                +--------+
                   ^                                         |
                   |        BUS.read_inbox("alice")          |
                   +---- alice.jsonl -> read + drain ---------+
```

## 工作原理

1. TeammateManager 透過 config.json 維護團隊名冊。

```python
class TeammateManager:
    def __init__(self, team_dir: Path):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load_config()
        self.threads = {}
```

2. `spawn()` 建立隊友並在執行緒中啟動 agent loop。

```python
def spawn(self, name: str, role: str, prompt: str) -> str:
    member = {"name": name, "role": role, "status": "working"}
    self.config["members"].append(member)
    self._save_config()
    thread = threading.Thread(
        target=self._teammate_loop,
        args=(name, role, prompt), daemon=True)
    thread.start()
    return f"Spawned teammate '{name}' (role: {role})"
```

3. MessageBus: append-only 的 JSONL 收件匣。`send()` 追加一行; `read_inbox()` 讀取全部並清空。

```python
class MessageBus:
    def send(self, sender, to, content, msg_type="message", extra=None):
        msg = {"type": msg_type, "from": sender,
               "content": content, "timestamp": time.time()}
        if extra:
            msg.update(extra)
        with open(self.dir / f"{to}.jsonl", "a") as f:
            f.write(json.dumps(msg) + "\n")

    def read_inbox(self, name):
        path = self.dir / f"{name}.jsonl"
        if not path.exists(): return "[]"
        msgs = [json.loads(l) for l in path.read_text().strip().splitlines() if l]
        path.write_text("")  # drain
        return json.dumps(msgs, indent=2)
```

4. 每個隊友在每次 LLM 呼叫前檢查收件匣, 將訊息注入上下文。

```python
def _teammate_loop(self, name, role, prompt):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(50):
        inbox = BUS.read_inbox(name)
        if inbox != "[]":
            messages.append({"role": "user",
                "content": f"<inbox>{inbox}</inbox>"})
        response = client.messages.create(...)
        if response.stop_reason != "tool_use":
            break
        # execute tools, append results...
    self._find_member(name)["status"] = "idle"
```

## 相對 s08 的變更

| 組件           | 之前 (s08)       | 之後 (s09)                         |
|----------------|------------------|------------------------------------|
| Tools          | 6                | 9 (+spawn/send/read_inbox)         |
| Agent 數量     | 單一             | 領導 + N 個隊友                    |
| 持久化         | 無               | config.json + JSONL 收件匣         |
| 執行緒         | 背景命令         | 每執行緒完整 agent loop            |
| 生命週期       | 一次性           | idle -> working -> idle            |
| 通訊           | 無               | message + broadcast                |

## 試一試

```sh
cd learn-claude-code
python agents/s09_agent_teams.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Spawn alice (coder) and bob (tester). Have alice send bob a message.`
2. `Broadcast "status update: phase 1 complete" to all teammates`
3. `Check the lead inbox for any messages`
4. 輸入 `/team` 檢視團隊名冊和狀態
5. 輸入 `/inbox` 手動檢查領導的收件匣
