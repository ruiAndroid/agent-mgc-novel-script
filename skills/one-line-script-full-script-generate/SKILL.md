# one-line-script-full-script-generate

## Description
一句话剧本：第5步全集剧本生成（可确认）。

## Version
3.3.0

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

## 终态规则（固定）
- `step5_full_script` 是最终创作状态。
- 当用户以 `interaction_action=confirm` 确认当前全集剧本时，只输出 1 到 2 句简短完成确认，不附带 `<fun_claw_interaction>...</fun_claw_interaction>`。
- 当当前全集剧本已确认完成后，若用户后续消息仅表达感谢、满意、夸赞、结束语或寒暄，只输出 1 到 2 句简短收尾，不附带 `<fun_claw_interaction>...</fun_claw_interaction>`。
- 当当前全集剧本已确认完成后，若用户提出对当前成品的明确修改意见，则按当前成品的修改请求处理，重新输出 `step5_full_script` 正文与交互协议块。
- 以上终态轻量回复禁止输出过程分析、规则解释、状态说明，禁止出现“我应该”“让我”“根据规则”之类的决策文本。

## 交互协议（固定）
正文末尾必须紧跟以下协议块，不得再额外输出“确认第X步”或“第X步重生成”之类的自然语言指令。
仅当当前全集剧本仍处于待确认 / 待修改状态时输出协议块；终态完成确认与轻量收尾不得输出协议块：

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
      "payload": "interaction_action=confirm\nstateId=step5_full_script\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "interaction_action=revise\nstateId=step5_full_script\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>\nstep_feedback="
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
