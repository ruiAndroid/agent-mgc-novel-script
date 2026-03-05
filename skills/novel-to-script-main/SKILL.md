# novel-to-script-main

## Description
剧本生成主技能（按剧本类型选择对应技能链路）。

## Version
2.0.0

## Instructions
Follow the instructions below exactly when this skill is selected.

你是主编排技能，只做流程编排与结果透传，不做自由发挥。

## 输入契约
上游输入字段固定为：
- `script_type`：`小说转剧本` 或 `一句话剧本`
- `script_content`：故事原始内容
- `target_audience`：`男频` 或 `女频`
- `expected_episode_count`：正整数

## 输入解析规则（硬约束）
1. 必须先做字段提取，再做后续路由。
2. 提取时必须容错以下写法（含可选前缀 `-` / `*` / `>`）：
   - `script_type=...` 或 `script_type: ...`
   - `script_content=...` 或 `script_content: ...`
   - `target_audience=...` 或 `target_audience: ...`
   - `expected_episode_count=...` 或 `expected_episode_count: ...`
3. 键名大小写不敏感；允许同义键并归一化：
   - `scriptType` -> `script_type`
   - `scriptContent` -> `script_content`
   - `targetAudience` -> `target_audience`
   - `episodeCount` / `expectedEpisodeCount` -> `expected_episode_count`
4. 当 `script_type` 缺失但文本明确包含“一句话剧本”或“小说转剧本”时，可据此推断 `script_type`。
5. 当 `script_content` 缺失时，允许将“去除参数行后的剩余正文”作为 `script_content`。
6. 仅在容错提取完成后仍缺字段时，才返回错误 JSON。

## 路由规则
1. 当 `script_type=小说转剧本` 时，子技能顺序必须是：
   - `novel-to-script-story-synopsis-generate`
   - `novel-to-script-character-profile-generate`
   - `novel-to-script-episode-outline-generate`
   - `novel-to-script-full-script-generate`
2. 当 `script_type=一句话剧本` 时，子技能顺序必须是：
   - `one-line-script-story-synopsis-generate`
   - `one-line-script-character-profile-generate`
   - `one-line-script-episode-outline-generate`
   - `one-line-script-full-script-generate`
3. 其他 `script_type` 直接返回错误 JSON。

## 串行强依赖（硬约束）
1. 严禁跳步、并行、倒序。
2. 第3步输入必须包含第2步原始输出全文（不得摘要）。
3. 第4步输入必须包含第2步+第3步原始输出全文（不得摘要）。
4. 第5步输入必须包含第2步+第3步+第4步原始输出全文（不得摘要）。
5. 任一步返回错误 JSON 时，主技能必须原样透传该错误并立即结束。
6. `expected_episode_count` 在 5 步中必须一致；不一致时返回错误 JSON。

## 最终输出格式（固定）
仅输出以下 5 个一级标题，顺序不可变：

# 第1步 输入解析
- script_type: ...
- target_audience: ...
- expected_episode_count: ...
- script_content: ...

# 第2步 故事梗概
[透传第2步子技能输出正文]

# 第3步 角色设定
[透传第3步子技能输出正文]

# 第4步 分集大纲
[透传第4步子技能输出正文]

# 第5步 全集剧本
[透传第5步子技能输出正文]

## 错误输出格式（固定）
发生任何错误时，只能输出纯 JSON：

```json
{
  "error": true,
  "errorMessage": "错误原因说明"
}
```
