# one-line-script-full-script-generate

## Description
一句话剧本：第5步全集剧本生成（可确认）。

## Version
3.2.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第5步。

## 输入契约
必需：
- `script_type`（必须为 `一句话剧本`）
- `script_content`
- `expected_episode_count`

可选：
- `story_output`
- `character_output`
- `outline_output`
- `output_depth`：`lite` | `full`（默认 `lite`）
- `step_feedback`

## 依赖策略
1. 优先使用 `outline_output`。
2. 缺少上游输出时允许回退生成，不得直接失败。

## 输出强约束（性能优先）
1. 默认 `output_depth=lite`：
   - 每集 1-2 场景。
   - 每集总行数控制在 12-24 行。
2. 仅在用户明确要求“完整版”时使用 `output_depth=full`。

## 输出格式（固定）
正文必须按以下结构输出，且不得再输出 [STEP_ID] / [STEP_STATUS] / [USER_CONFIRM_REQUIRED] / [NEXT_STEP] 等旧格式字段：

# 当前状态
- stateId: step5_full_script
- stateLabel: 全集剧本
- script_type: 一句话剧本
- expected_episode_count: <数字>
- output_depth: lite|full

## 第5步 全集剧本


从 `# 第1集` 到 `# 第N集`。

## 交互协议（固定）
正文末尾必须紧跟以下协议块，不得再额外输出“确认第X步”或“第X步重生成”之类的自然语言指令：

<fun_claw_interaction>
{
  "version": "1.0",
  "type": "approval_request",
  "stateId": "step5_full_script",
  "title": "请确认当前全集剧本",
  "actions": [
    {
      "id": "confirm",
      "label": "确认并继续",
      "kind": "send",
      "payload": "interaction_action=confirm\nstateId=step5_full_script"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "interaction_action=revise\nstateId=step5_full_script\nstep_feedback="
    }
  ]
}
</fun_claw_interaction>

## 错误输出格式（固定）
```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
