# agent-mgc-novel-script

小说改编剧本智能体（ZeroClaw 运行时版本）。

该仓库只提供智能体描述与 skills，不再提供独立 Python 服务形态。

## 目录

- `zeroclaw-agent.manifest.json`
- `skills/novel-to-script-main.json`
- `skills/novel-intake-parse.json`
- `skills/novel-story-synopsis-generate.json`
- `skills/novel-character-profile-generate.json`
- `skills/novel-episode-outline-generate.json`
- `skills/novel-full-script-generate.json`

## ZeroClaw 挂载与配置

将本项目挂载到 ZeroClaw 容器，例如：

- 主机目录：`/opt/agents/agent-mgc-novel-script`
- 容器目录：`/workspace/agent-mgc-novel-script`

在 ZeroClaw `config.toml` 中启用 open skills：

```toml
[skills]
open_skills_enabled = true
open_skills_dir = "/workspace/agent-mgc-novel-script/skills"
prompt_injection_mode = "full"
```

## 入口技能

- `novel-to-script-main`

该主技能会按固定顺序串联 5 个子技能：输入解析 -> 故事梗概 -> 角色小传 -> 分集大纲 -> 完整剧本草案。

## 输入字段

必填：

- `novel_content`
- `novel_type`
- `target_audience`

选填：

- `expected_episode_count`

## 提示词维护（推荐）

建议使用 `md` 维护长提示词，再同步回 `json`：

1. 首次导出当前 JSON 提示词到 `prompts/`：

```powershell
powershell -ExecutionPolicy Bypass -File .\sync-skill-prompts.ps1 -Mode export
```

2. 编辑 `prompts/*.md`。

3. 回写到 `skills/*.json` 的 `prompt_template`：

```powershell
powershell -ExecutionPolicy Bypass -File .\sync-skill-prompts.ps1 -Mode build
```

说明：如果某个 skill JSON 非法，脚本会跳过并提示 `skip invalid json`，避免整批中断。
