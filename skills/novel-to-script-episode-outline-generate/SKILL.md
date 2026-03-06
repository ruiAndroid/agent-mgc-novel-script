# novel-to-script-episode-outline-generate

## Description
小说转剧本：第4步分集大纲生成（可确认）。

## Version
3.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第4步，不得生成第5步正文。

## 输入契约
必需：
- `script_type`（必须为 `小说转剧本`）
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
[STEP_ID]: step4_episode_outline
[STEP_STATUS]: draft
[SCRIPT_TYPE]: 小说转剧本
[EXPECTED_EPISODE_COUNT]: <数字>
[NEXT_STEP]: step5_full_script
[USER_CONFIRM_REQUIRED]: true

## 第4步 分集大纲
按 `expected_episode_count` 输出第1集到第N集，每集包含：
- 核心事件
- 卡点/反转
- 集末钩子

## 用户确认
- 确认通过：`确认第4步`
- 需要重生成：`第4步重生成：<修改意见>`

## 错误输出格式（固定）
```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
