# agent-mgc-novel-script

小说改编剧本智能体（ZeroClaw 运行时版本）。

该仓库只提供智能体描述与 skills，不再提供独立 Python 服务形态。

## 目录

- `agent.minifest.json`
- `skills/<skill_id>/SKILL.md`（每个技能一个目录）
- `scripts/json-skills-to-skill-md.ps1`（JSON 技能迁移脚本）

## ZeroClaw 挂载与配置

将本项目挂载到 ZeroClaw 容器，例如：

- 主机目录：`/opt/agents/agent-mgc-novel-script`
- 容器目录：`/workspace/agent-mgc-novel-script`

在 ZeroClaw `config.toml` 中启用 open skills：

```toml
[autonomy]
cli_excluded_tools = [
  "shell",
  "file_read",
  "file_write",
  "file_edit",
  "glob_search",
  "content_search",
  "cron_add",
  "cron_list",
  "cron_remove",
  "cron_update",
  "cron_run",
  "cron_runs",
  "memory_store",
  "memory_recall",
  "memory_forget",
  "schedule",
  "model_routing_config",
  "proxy_config",
  "git_operations",
  "pushover",
  "pdf_read",
  "screenshot",
  "image_info",
  "browser_open",
  "browser",
  "http_request",
  "web_fetch",
  "web_search_tool",
  "composio",
]

[skills]
open_skills_enabled = true
open_skills_dir = "/workspace/agent-mgc-novel-script/skills"
prompt_injection_mode = "compact"
```

## 入口技能

- `novel-to-script-main`

该主技能会按固定顺序串联 4 个子技能（故事梗概 -> 角色小传 -> 分集大纲 -> 完整剧本草案），输入解析在主技能内完成。

## 输入字段

必填：

- `script_content`
- `script_type`
- `target_audience`
- `expected_episode_count`

## 交互协议

当前仓库约定多轮确认类回复使用平台通用交互协议：

- `fun-claw-interaction/v1`

在 `interactive` 模式下，正文末尾追加：

```text
<fun_claw_interaction>
{ ...JSON... }
</fun_claw_interaction>
```

协议块用于声明：

- 当前状态 `state_id`
- 是否需要用户确认
- 可执行动作 `actions`
- 点击后回传的 `payload`

平台前端只解析该协议块，不应依赖具体业务文案。

## 技能格式

当前仓库使用 ZeroClaw 可识别的目录技能格式：

- `skills/novel-to-script-main/SKILL.md`
- `skills/novel-to-script-story-synopsis-generate/SKILL.md`
- `skills/novel-to-script-character-profile-generate/SKILL.md`
- `skills/novel-to-script-episode-outline-generate/SKILL.md`
- `skills/novel-to-script-full-script-generate/SKILL.md`
- `skills/one-line-script-story-synopsis-generate/SKILL.md`
- `skills/one-line-script-character-profile-generate/SKILL.md`
- `skills/one-line-script-episode-outline-generate/SKILL.md`
- `skills/one-line-script-full-script-generate/SKILL.md`

如需从历史 `skills/*.json` 迁移，可执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\json-skills-to-skill-md.ps1 -Overwrite -RemoveSource
```


