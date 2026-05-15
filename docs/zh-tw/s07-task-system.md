# s07: Task System (任務系統)

`s01 > s02 > s03 > s04 > s05 > s06 | [ s07 ] s08 > s09 > s10 > s11 > s12`

> *"大目標要拆成小任務, 排好序, 記在磁碟上"* -- 檔案持久化的任務圖, 為多 agent 協作打基礎。
>
> **Harness 層**: 持久化任務 -- 比任何一次對話都長命的目標。

## 問題

s03 的 TodoManager 只是記憶體中的扁平清單: 沒有順序、沒有依賴、狀態只有做完沒做完。真實目標是有結構的 -- 任務 B 依賴任務 A, 任務 C 和 D 可以並行, 任務 E 要等 C 和 D 都完成。

沒有顯式的關係, Agent 分不清什麼能做、什麼被卡住、什麼能同時跑。而且清單只活在記憶體裡, 上下文壓縮 (s06) 一跑就沒了。

## 解決方案

把扁平清單升級為持久化到磁碟的**任務圖**。每個任務是一個 JSON 檔案, 有狀態、前置依賴 (`blockedBy`)。任務圖隨時回答三個問題:

- **什麼可以做?** -- 狀態為 `pending` 且 `blockedBy` 為空的任務。
- **什麼被卡住?** -- 等待前置任務完成的任務。
- **什麼做完了?** -- 狀態為 `completed` 的任務, 完成時自動解鎖後續任務。

```
.tasks/
  task_1.json  {"id":1, "status":"completed"}
  task_2.json  {"id":2, "blockedBy":[1], "status":"pending"}
  task_3.json  {"id":3, "blockedBy":[1], "status":"pending"}
  task_4.json  {"id":4, "blockedBy":[2,3], "status":"pending"}

任務圖 (DAG):
                 +----------+
            +--> | task 2   | --+
            |    | pending  |   |
+----------+     +----------+    +--> +----------+
| task 1   |                          | task 4   |
| completed| --> +----------+    +--> | blocked  |
+----------+     | task 3   | --+     +----------+
                 | pending  |
                 +----------+

順序:   task 1 必須先完成, 才能開始 2 和 3
並行:   task 2 和 3 可以同時執行
依賴:   task 4 要等 2 和 3 都完成
狀態:   pending -> in_progress -> completed
```

這個任務圖是 s07 之後所有機制的協調骨架: 背景執行 (s08)、多 agent 團隊 (s09+)、worktree 隔離 (s12) 都讀寫這同一個結構。

## 工作原理

1. **TaskManager**: 每個任務一個 JSON 檔案, CRUD + 依賴圖。

```python
class TaskManager:
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1

    def create(self, subject, description=""):
        task = {"id": self._next_id, "subject": subject,
                "status": "pending", "blockedBy": [],
                "owner": ""}
        self._save(task)
        self._next_id += 1
        return json.dumps(task, indent=2)
```

2. **依賴解除**: 完成任務時, 自動將其 ID 從其他任務的 `blockedBy` 中移除, 解鎖後續任務。

```python
def _clear_dependency(self, completed_id):
    for f in self.dir.glob("task_*.json"):
        task = json.loads(f.read_text())
        if completed_id in task.get("blockedBy", []):
            task["blockedBy"].remove(completed_id)
            self._save(task)
```

3. **狀態變更 + 依賴關聯**: `update` 處理狀態轉換和依賴邊。

```python
def update(self, task_id, status=None,
           add_blocked_by=None, remove_blocked_by=None):
    task = self._load(task_id)
    if status:
        task["status"] = status
        if status == "completed":
            self._clear_dependency(task_id)
    if add_blocked_by:
        task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))
    if remove_blocked_by:
        task["blockedBy"] = [x for x in task["blockedBy"] if x not in remove_blocked_by]
    self._save(task)
```

4. 四個任務工具加入 dispatch map。

```python
TOOL_HANDLERS = {
    # ...base tools...
    "task_create": lambda **kw: TASKS.create(kw["subject"]),
    "task_update": lambda **kw: TASKS.update(kw["task_id"], kw.get("status")),
    "task_list":   lambda **kw: TASKS.list_all(),
    "task_get":    lambda **kw: TASKS.get(kw["task_id"]),
}
```

從 s07 起, 任務圖是多步工作的預設選擇。s03 的 Todo 仍可用於單次會話內的快速清單。

## 相對 s06 的變更

| 組件 | 之前 (s06) | 之後 (s07) |
|---|---|---|
| Tools | 5 | 8 (`task_create/update/list/get`) |
| 規劃模型 | 扁平清單 (僅記憶體) | 帶依賴關係的任務圖 (磁碟) |
| 關係 | 無 | `blockedBy` 邊 |
| 狀態追蹤 | 做完沒做完 | `pending` -> `in_progress` -> `completed` |
| 持久化 | 壓縮後丟失 | 壓縮和重啟後存活 |

## 試一試

```sh
cd learn-claude-code
python agents/s07_task_system.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Create 3 tasks: "Setup project", "Write code", "Write tests". Make them depend on each other in order.`
2. `List all tasks and show the dependency graph`
3. `Complete task 1 and then list tasks to see task 2 unblocked`
4. `Create a task board for refactoring: parse -> transform -> emit -> test, where transform and emit can run in parallel after parse`
