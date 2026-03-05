# one-line-script-character-profile-generate

## Description
一句话剧本：角色设定生成。

## Version
2.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第3步：角色设定生成。

## 输入契约
必须同时包含：
- `story_output`：第2步原始全文输出
- `script_content`
- `target_audience`
- `expected_episode_count`

## 强依赖校验（硬约束）
1. `story_output` 中必须包含：`[STEP_ID]: step2_story_synopsis`。
2. `story_output` 中必须包含：`[EXPECTED_EPISODE_COUNT]: <数字>`，且与当前 `expected_episode_count` 一致。
3. 校验失败必须直接返回错误 JSON，不得继续生成正文。

## 输出格式（固定）
直接输出 Markdown，且必须包含以下标记行：

[STEP_ID]: step3_character_profile
[STEP_STATUS]: ok
[SCRIPT_TYPE]: 一句话剧本
[EXPECTED_EPISODE_COUNT]: <数字>

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

## 约束
1. 主要角色 2-4 人，次要角色 3-6 人。
2. 每个主要角色必须含：身份、目标、弱点、成长终点。
3. 角色关系不得与第2步故事梗概冲突。

## 错误输出格式（固定）

```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
