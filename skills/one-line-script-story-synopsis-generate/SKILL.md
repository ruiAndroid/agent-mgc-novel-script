# one-line-script-story-synopsis-generate

## Description
一句话剧本：故事梗概生成。

## Version
2.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第2步：故事梗概生成。

## 输入契约
必须同时包含：
- `script_type`（必须等于`一句话剧本`）
- `script_content`
- `target_audience`
- `expected_episode_count`

任一字段缺失，或 `script_type` 不匹配，返回错误 JSON。

## 输出格式（固定）
直接输出 Markdown，且必须包含以下标记行：

[STEP_ID]: step2_story_synopsis
[STEP_STATUS]: ok
[SCRIPT_TYPE]: 一句话剧本
[EXPECTED_EPISODE_COUNT]: <数字>

## 故事梗概
- 300-500字，聚焦主冲突与主角目标。

## 主线大纲
### 第一幕：开端
### 第二幕：发展
### 第三幕：高潮与结局

## 开篇钩子
- 第一集开场冲突，80-150字。

## 约束
1. 必须与 `target_audience` 风格匹配。
2. 不得输出多余解释、前后缀说明、代码块围栏。
3. 不得输出与输入矛盾的人物身份或结局导向。

## 错误输出格式（固定）

```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
