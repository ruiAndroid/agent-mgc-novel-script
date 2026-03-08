# novel-to-script-story-synopsis-generate

## Description
小说转剧本：第2步故事梗概生成（可确认）。

## Version
3.2.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第2步，不得生成第3~5步正文。

## 输入契约
必需：
- `script_type`（必须为 `小说转剧本`）
- `script_content`
- `target_audience`
- `expected_episode_count`

可选：
- `step_feedback`

## 输入解析
支持 `key=value` 与 `key: value`；支持键名同义归一化（`scriptType` 等）。

## 输出格式（固定）
正文必须按以下结构输出，且不得再输出 [STEP_ID] / [STEP_STATUS] / [USER_CONFIRM_REQUIRED] / [NEXT_STEP] 等旧格式字段：

# 当前状态
- stateId: step2_story_synopsis
- stateLabel: 故事梗概
- script_type: 小说转剧本
- expected_episode_count: <数字>

## 第2步 故事梗概


- 250-450字，保持原小说主冲突与人物动机。

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
      "id": "confirm",
      "label": "确认并继续",
      "kind": "send",
      "payload": "interaction_action=confirm\nstateId=step2_story_synopsis\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "interaction_action=revise\nstateId=step2_story_synopsis\nscript_type=<当前script_type>\nscript_content=<当前script_content>\ntarget_audience=<当前target_audience>\nexpected_episode_count=<当前expected_episode_count>\nstep_feedback="
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
