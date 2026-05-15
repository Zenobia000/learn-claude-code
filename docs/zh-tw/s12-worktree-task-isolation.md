# s12: Worktree + Task Isolation (Worktree 任務隔離)

`s01 > s02 > s03 > s04 > s05 > s06 | s07 > s08 > s09 > s10 > s11 > [ s12 ]`

> *"各幹各的目錄, 互不干擾"* -- 任務管目標, worktree 管目錄, 按 ID 繫結。
>
> **Harness 層**: 目錄隔離 -- 永不碰撞的並行執行通道。

## 問題

到 s11, Agent 已經能自主認領和完成任務。但所有任務共享一個目錄。兩個 Agent 同時重構不同模組 -- A 改 `config.py`, B 也改 `config.py`, 未提交的改動互相污染, 誰也沒法乾淨回滾。

任務板管 "做什麼" 但不管 "在哪做"。解法: 給每個任務一個獨立的 git worktree 目錄, 用任務 ID 把兩邊關聯起來。

## 解決方案

```
Control plane (.tasks/)             Execution plane (.worktrees/)
+------------------+                +------------------------+
| task_1.json      |                | auth-refactor/         |
|   status: in_progress  <------>   branch: wt/auth-refactor
|   worktree: "auth-refactor"   |   task_id: 1             |
+------------------+                +------------------------+
| task_2.json      |                | ui-login/              |
|   status: pending    <------>     branch: wt/ui-login
|   worktree: "ui-login"       |   task_id: 2             |
+------------------+                +------------------------+
                                    |
                          index.json (worktree registry)
                          events.jsonl (lifecycle log)

State machines:
  Task:     pending -> in_progress -> completed
  Worktree: absent  -> active      -> removed | kept
```

## 工作原理

1. **建立任務。** 先把目標持久化。

```python
TASKS.create("Implement auth refactor")
# -> .tasks/task_1.json  status=pending  worktree=""
```

2. **建立 worktree 並繫結任務。** 傳入 `task_id` 自動將任務推進到 `in_progress`。

```python
WORKTREES.create("auth-refactor", task_id=1)
# -> git worktree add -b wt/auth-refactor .worktrees/auth-refactor HEAD
# -> index.json gets new entry, task_1.json gets worktree="auth-refactor"
```

繫結同時寫入兩側狀態:

```python
def bind_worktree(self, task_id, worktree):
    task = self._load(task_id)
    task["worktree"] = worktree
    if task["status"] == "pending":
        task["status"] = "in_progress"
    self._save(task)
```

3. **在 worktree 中執行命令。** `cwd` 指向隔離目錄。

```python
subprocess.run(command, shell=True, cwd=worktree_path,
               capture_output=True, text=True, timeout=300)
```

4. **收尾。** 兩種選擇:
   - `worktree_keep(name)` -- 保留目錄供後續使用。
   - `worktree_remove(name, complete_task=True)` -- 刪除目錄, 完成繫結任務, 發出事件。一個呼叫搞定拆除 + 完成。

```python
def remove(self, name, force=False, complete_task=False):
    self._run_git(["worktree", "remove", wt["path"]])
    if complete_task and wt.get("task_id") is not None:
        self.tasks.update(wt["task_id"], status="completed")
        self.tasks.unbind_worktree(wt["task_id"])
        self.events.emit("task.completed", ...)
```

5. **事件流。** 每個生命週期步驟寫入 `.worktrees/events.jsonl`:

```json
{
  "event": "worktree.remove.after",
  "task": {"id": 1, "status": "completed"},
  "worktree": {"name": "auth-refactor", "status": "removed"},
  "ts": 1730000000
}
```

事件類型: `worktree.create.before/after/failed`, `worktree.remove.before/after/failed`, `worktree.keep`, `task.completed`。

當機後從 `.tasks/` + `.worktrees/index.json` 重建現場。會話記憶是易失的; 磁碟狀態是持久的。

## 相對 s11 的變更

| 組件               | 之前 (s11)                 | 之後 (s12)                                   |
|--------------------|----------------------------|----------------------------------------------|
| 協調               | 任務板 (owner/status)      | 任務板 + worktree 顯式繫結                   |
| 執行範圍           | 共享目錄                   | 每個任務獨立目錄                             |
| 可恢復性           | 僅任務狀態                 | 任務狀態 + worktree 索引                     |
| 收尾               | 任務完成                   | 任務完成 + 顯式 keep/remove                  |
| 生命週期可見性     | 隱式日誌                   | `.worktrees/events.jsonl` 顯式事件流         |

## 試一試

```sh
cd learn-claude-code
python agents/s12_worktree_task_isolation.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Create tasks for backend auth and frontend login page, then list tasks.`
2. `Create worktree "auth-refactor" for task 1, then bind task 2 to a new worktree "ui-login".`
3. `Run "git status --short" in worktree "auth-refactor".`
4. `Keep worktree "ui-login", then list worktrees and inspect events.`
5. `Remove worktree "auth-refactor" with complete_task=true, then list tasks/worktrees/events.`
