# one-line-script-full-script-generate

## Description
一句话剧本：全集剧本生成。

## Version
2.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你只负责第5步：全集剧本生成。

## 输入契约
必须同时包含：
- `story_output`：第2步原始全文输出
- `character_output`：第3步原始全文输出
- `outline_output`：第4步原始全文输出
- `expected_episode_count`

## 强依赖校验（硬约束）
1. `story_output` 必须包含 `[STEP_ID]: step2_story_synopsis`。
2. `character_output` 必须包含 `[STEP_ID]: step3_character_profile`。
3. `outline_output` 必须包含 `[STEP_ID]: step4_episode_outline`。
4. 三个上游输出中的 `EXPECTED_EPISODE_COUNT` 必须和当前一致。
5. 任一校验失败直接返回错误 JSON。

## 输出格式（固定）
直接输出 Markdown，且必须包含以下标记行：

[STEP_ID]: step5_full_script
[STEP_STATUS]: ok
[SCRIPT_TYPE]: 一句话剧本
[EXPECTED_EPISODE_COUNT]: <数字>

然后输出完整剧本正文：
- 必须从 `# 第1集` 写到 `# 第N集`（N=expected_episode_count）。
- 每集至少 3 个场景。
- 每集必须在结尾保留“集末钩子”。

示例结构：
# 第1集
## 场景一：地点/内外景/时间
【镜头1】...
【角色名】：...

## 场景二：...
...

## 约束
1. 不得改写第4步已确定的集标题和核心事件方向。
2. 不得新增与第3步设定冲突的新主角。
3. 不得输出解释性文字、流程说明、代码块围栏。

## 错误输出格式（固定）

```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
