# novel-to-script-episode-outline-generate

## Description
小说转剧本：分集大纲生成。

## Version
2.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第4步：分集大纲生成。

## 输入契约
必须同时包含：
- `story_output`：第2步原始全文输出
- `character_output`：第3步原始全文输出
- `script_content`
- `expected_episode_count`

## 强依赖校验（硬约束）
1. `story_output` 必须包含 `[STEP_ID]: step2_story_synopsis`。
2. `character_output` 必须包含 `[STEP_ID]: step3_character_profile`。
3. 两个上游输出中的 `EXPECTED_EPISODE_COUNT` 必须和当前一致。
4. 任一校验失败直接返回错误 JSON。

## 输出格式（固定）
直接输出 Markdown，且必须包含以下标记行：

[STEP_ID]: step4_episode_outline
[STEP_STATUS]: ok
[SCRIPT_TYPE]: 小说转剧本
[EXPECTED_EPISODE_COUNT]: <数字>

随后严格输出第1集到第N集（N=expected_episode_count）：

## 第1集 <标题>
- 核心事件：...
- 卡点/反转：...
- 集末钩子：...

...

## 第N集 <标题>
- 核心事件：...
- 卡点/反转：...
- 集末钩子：...

## 约束
1. 集数必须严格等于 `expected_episode_count`。
2. 每集都必须出现“核心事件/卡点或反转/集末钩子”三项。
3. 内容可压缩改编小说，但不得背离第2步主线与第3步角色弧光。

## 错误输出格式（固定）

```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
