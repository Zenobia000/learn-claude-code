# s05: Skills (Skill 載入)

`s01 > s02 > s03 > s04 > [ s05 ] s06 | s07 > s08 > s09 > s10 > s11 > s12`

> *"用到什麼知識, 臨時載入什麼知識"* -- 透過 tool_result 注入, 不塞 system prompt。
>
> **Harness 層**: 按需知識 -- 模型開口要時才給的領域專長。

## 問題

你希望 Agent 遵循特定領域的工作流: git 約定、測試模式、程式碼審查清單。全塞進系統提示太浪費 -- 10 個 Skill, 每個 2000 token, 就是 20,000 token, 大部分跟當前任務毫無關係。

## 解決方案

```
System prompt (Layer 1 -- always present):
+--------------------------------------+
| You are a coding agent.              |
| Skills available:                    |
|   - git: Git workflow helpers        |  ~100 tokens/skill
|   - test: Testing best practices     |
+--------------------------------------+

When model calls load_skill("git"):
+--------------------------------------+
| tool_result (Layer 2 -- on demand):  |
| <skill name="git">                   |
|   Full git workflow instructions...  |  ~2000 tokens
|   Step 1: ...                        |
| </skill>                             |
+--------------------------------------+
```

第一層: 系統提示中放 Skill 名稱 (低成本)。第二層: tool_result 中按需放完整內容。

## 工作原理

1. 每個 Skill 是一個目錄, 包含 `SKILL.md` 檔案和 YAML frontmatter。

```
skills/
  pdf/
    SKILL.md       # ---\n name: pdf\n description: Process PDF files\n ---\n ...
  code-review/
    SKILL.md       # ---\n name: code-review\n description: Review code\n ---\n ...
```

2. SkillLoader 遞迴掃描 `SKILL.md` 檔案, 用目錄名稱作為 Skill 標識。

```python
class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills = {}
        for f in sorted(skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body}

    def get_descriptions(self) -> str:
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "")
            lines.append(f"  - {name}: {desc}")
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'."
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"
```

3. 第一層寫入系統提示。第二層不過是 dispatch map 中的又一個工具。

```python
SYSTEM = f"""You are a coding agent at {WORKDIR}.
Skills available:
{SKILL_LOADER.get_descriptions()}"""

TOOL_HANDLERS = {
    # ...base tools...
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw["name"]),
}
```

模型知道有哪些 Skill (便宜), 需要時再載入完整內容 (貴)。

## 相對 s04 的變更

| 元件           | 之前 (s04)       | 之後 (s05)                     |
|----------------|------------------|--------------------------------|
| Tools          | 5 (基礎 + task)  | 5 (基礎 + load_skill)          |
| 系統提示       | 靜態字串         | + Skill 描述列表               |
| 知識庫         | 無               | skills/\*/SKILL.md 檔案        |
| 注入方式       | 無               | 兩層 (系統提示 + result)       |

## 試一試

```sh
cd learn-claude-code
python agents/s05_skill_loading.py
```

試試這些 prompt (英文 prompt 對 LLM 效果更好, 也可以用中文):

1. `What skills are available?`
2. `Load the agent-builder skill and follow its instructions`
3. `I need to do a code review -- load the relevant skill first`
4. `Build an MCP server using the mcp-builder skill`
