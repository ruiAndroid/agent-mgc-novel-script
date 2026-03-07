# novel-to-script-character-profile-generate

## Description
小说转剧本：第3步角色设定生成（可确认）。

## Version
3.2.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第3步，不得生成第4~5步正文。

## 输入契约
必需：
- `script_type`（必须为 `小说转剧本`）
- `script_content`
- `target_audience`
- `expected_episode_count`

可选：
- `story_output`
- `step_feedback`

## 依赖策略
1. 优先使用 `story_output`。
2. 若缺少 `story_output`，允许回退基于 `script_content` 生成（不得报硬错误）。

## 输出格式（固定）
正文必须按以下结构输出，且不得再输出 [STEP_ID] / [STEP_STATUS] / [USER_CONFIRM_REQUIRED] / [NEXT_STEP] 等旧格式字段：

# 当前状态
- stateId: step3_character_profile
- stateLabel: 角色设定
- script_type: 小说转剧本
- expected_episode_count: <数字>

## 第3步 角色设定


## 角色基础信息
### 主要角色
### 次要角色

## 人物关系
### 核心关系
### 对立关系
### 隐藏关系
### 情感纠葛

## 角色成长弧光
### 主要角色
### 次要角色

## 交互协议（固定）
正文末尾必须紧跟以下协议块，不得再额外输出“确认第X步”或“第X步重生成”之类的自然语言指令：

<fun_claw_interaction>
{
  "version": "1.0",
  "type": "approval_request",
  "stateId": "step3_character_profile",
  "title": "请确认当前角色设定",
  "actions": [
    {
      "id": "confirm",
      "label": "确认并继续",
      "kind": "send",
      "payload": "interaction_action=confirm\nstateId=step3_character_profile"
    },
    {
      "id": "revise",
      "label": "提出修改",
      "kind": "prefill",
      "payload": "interaction_action=revise\nstateId=step3_character_profile\nstep_feedback="
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
