# novel-to-script-character-profile-generate

## Description
小说转剧本：第3步角色设定生成（可确认）。

## Version
3.0.0

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
[STEP_ID]: step3_character_profile
[STEP_STATUS]: draft
[SCRIPT_TYPE]: 小说转剧本
[EXPECTED_EPISODE_COUNT]: <数字>
[NEXT_STEP]: step4_episode_outline
[USER_CONFIRM_REQUIRED]: true

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

## 用户确认
- 确认通过：`确认第3步`
- 需要重生成：`第3步重生成：<修改意见>`

## 错误输出格式（固定）
```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
