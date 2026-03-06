# novel-to-script-story-synopsis-generate

## Description
小说转剧本：第2步故事梗概生成（可确认）。

## Version
3.0.0

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
[STEP_ID]: step2_story_synopsis
[STEP_STATUS]: draft
[SCRIPT_TYPE]: 小说转剧本
[EXPECTED_EPISODE_COUNT]: <数字>
[NEXT_STEP]: step3_character_profile
[USER_CONFIRM_REQUIRED]: true

## 第2步 故事梗概
- 250-450字，保持原小说主冲突与人物动机。

## 主线大纲
### 第一幕：开端
### 第二幕：发展
### 第三幕：高潮与结局

## 开篇钩子
- 60-120字。

## 用户确认
- 确认通过：`确认第2步`
- 需要重生成：`第2步重生成：<修改意见>`

## 错误输出格式（固定）
```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
