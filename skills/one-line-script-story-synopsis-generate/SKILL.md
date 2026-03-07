# one-line-script-story-synopsis-generate

## Description
一句话剧本：第2步故事梗概生成（可确认）。

## Version
3.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第2步，不得生成第3~5步正文。

## 输入契约
必需：
- `script_type`（必须为 `一句话剧本`）
- `script_content`
- `target_audience`
- `expected_episode_count`

可选：
- `step_feedback`（重生成意见）

## 输入解析
支持 `key=value` 与 `key: value`；支持键名同义归一化（`scriptType` 等）。

## 输出格式（固定）
[STEP_ID]: step2_story_synopsis
[STEP_STATUS]: draft
[SCRIPT_TYPE]: 一句话剧本
[EXPECTED_EPISODE_COUNT]: <数字>
[NEXT_STEP]: step3_character_profile
[USER_CONFIRM_REQUIRED]: true

## 第2步 故事梗概
- 200-350字，聚焦主冲突、主目标、核心反转。

## 主线大纲
### 第一幕：开端
### 第二幕：发展
### 第三幕：高潮与结局

## 开篇钩子
- 60-120字。

## 交互协议（固定）
正文末尾必须紧跟以下协议块，不得再额外输出“确认第X步”或“第X步重生成”之类的自然语言指令：

<fun_claw_interaction>
{
  "version": "1.0",
  "type": "approval_request",
  "stateId": "step2_story_synopsis",
  "title": "请确认当前故事梗概",
  "actions": [
    {
      "id": "approve",
      "label": "确认并继续",
      "kind": "send",
      "payload": "workflow_action=approve\nstateId=step2_story_synopsis"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "workflow_action=revise\nstateId=step2_story_synopsis\nstep_feedback="
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
