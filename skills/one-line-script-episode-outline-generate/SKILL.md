# one-line-script-episode-outline-generate

## Description
一句话剧本：第4步分集大纲生成（可确认）。

## Version
3.2.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第4步，不得生成第5步正文。

## 输入契约
必需：
- `script_type`（必须为 `一句话剧本`）
- `script_content`
- `expected_episode_count`

可选：
- `story_output`
- `character_output`
- `step_feedback`

## 依赖策略
1. 优先使用 `story_output + character_output`。
2. 任一缺失时允许回退生成，不得因缺失直接失败。

## 输出格式（固定）
正文必须按以下结构输出，且不得再输出 [STEP_ID] / [STEP_STATUS] / [USER_CONFIRM_REQUIRED] / [NEXT_STEP] 等旧格式字段：

# 当前状态
- stateId: step4_episode_outline
- stateLabel: 分集大纲
- script_type: 一句话剧本
- expected_episode_count: <数字>

## 第4步 分集大纲


按 `expected_episode_count` 输出第1集到第N集，每集包含：
- 核心事件
- 卡点/反转
- 集末钩子

## 交互协议（固定）
正文末尾必须紧跟以下协议块，不得再额外输出“确认第X步”或“第X步重生成”之类的自然语言指令：

<fun_claw_interaction>
{
  "version": "1.0",
  "type": "approval_request",
  "stateId": "step4_episode_outline",
  "title": "请确认当前分集大纲",
  "actions": [
    {
      "id": "confirm",
      "label": "确认并继续",
      "kind": "send",
      "payload": "interaction_action=confirm\nstateId=step4_episode_outline\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "interaction_action=revise\nstateId=step4_episode_outline\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>\nstep_feedback="
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
