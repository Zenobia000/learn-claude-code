# s02: Tool Use (工具使用)

`s01 > [ s02 ] s03 > s04 > s05 > s06 | s07 > s08 > s09 > s10 > s11 > s12`

> *"加一個工具, 只加一個 handler"* -- 迴圈不用動, 新工具註冊進 dispatch map 就行。
>
> **Harness 層**: 工具分發 -- 擴展模型能觸達的邊界。

## 問題

只有 `bash` 時, 所有操作都走 shell。`cat` 截斷不可預測, `sed` 遇到特殊字元就崩, 每次 bash 呼叫都是不受約束的安全面。專用工具 (`read_file`, `write_file`) 可以在工具層面做路徑沙箱。

關鍵洞察: 加工具不需要改迴圈。

## 解決方案

```
+--------+      +-------+      +------------------+
|  User  | ---> |  LLM  | ---> | Tool Dispatch    |
| prompt |      |       |      | {                |
+--------+      +---+---+      |   bash: run_bash |
                    ^           |   read: run_read |
                    |           |   write: run_wr  |
                    +-----------+   edit: run_edit |
                    tool_result | }                |
                                +------------------+

The dispatch map is a dict: {tool_name: handler_function}.
One lookup replaces any if/elif chain.
```

## 工作原理

1. 每個工具有一個處理函式。路徑沙箱防止逃逸工作區。

```python
def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path

def run_read(path: str, limit: int = None) -> str:
    text = safe_path(path).read_text()
    lines = text.splitlines()
    if limit and limit < len(lines):
        lines = lines[:limit]
    return "\n".join(lines)[:50000]
```

2. dispatch map 將工具名稱對應到處理函式。

```python
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"],
                                        kw["new_text"]),
}
```

3. 迴圈中按名稱查找處理函式。迴圈體本身與 s01 完全一致。

```python
for block in response.content:
    if block.type == "tool_use":
        handler = TOOL_HANDLERS.get(block.name)
        output = handler(**block.input) if handler \
            else f"Unknown tool: {block.name}"
        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": output,
        })
```

加工具 = 加 handler + 加 schema。迴圈永遠不變。

## 相對 s01 的變更

| 元件           | 之前 (s01)         | 之後 (s02)                     |
|----------------|--------------------|--------------------------------|
| Tools          | 1 (僅 bash)        | 4 (bash, read, write, edit)    |
| Dispatch       | 寫死 bash 呼叫     | `TOOL_HANDLERS` 字典           |
| 路徑安全       | 無                 | `safe_path()` 沙箱             |
| Agent loop     | 不變               | 不變                           |

## 試一試

```sh
cd learn-claude-code
python agents/s02_tool_use.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `Read the file requirements.txt`
2. `Create a file called greet.py with a greet(name) function`
3. `Edit greet.py to add a docstring to the function`
4. `Read greet.py to verify the edit worked`
