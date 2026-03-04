# agent-mgc-novel-script

DreamWorks novel-to-script agent package for ZeroClaw runtime only.

This repository supports a single deployment form:

- agent runs inside ZeroClaw runtime container
- LLM provider/model/auth are configured in ZeroClaw `config.toml`
- this repo only provides skills and workflow manifest

## Files

- `zeroclaw-agent.manifest.json`
- `skills/novel-to-script-pipeline.json`
- `skills/novel-intake-parse.json`
- `skills/novel-story-synopsis-generate.json`
- `skills/novel-character-profile-generate.json`
- `skills/novel-episode-outline-generate.json`
- `skills/novel-full-script-generate.json`

## ZeroClaw Docker setup

Mount this project into the runtime container, for example:

- host: `/opt/agent-mgc-novel-script`
- container: `/workspace/agent-mgc-novel-script`

Enable skills in ZeroClaw `config.toml`:

```toml
[skills]
open_skills_enabled = true
open_skills_dir = "/workspace/agent-mgc-novel-script/skills"
prompt_injection_mode = "full"
```

Workflow entry skill:

- `novel-to-script-pipeline`

## Input contract

Required fields:

- `novel_content`
- `novel_type`
- `target_audience`

Optional field:

- `expected_episode_count`

Pipeline output is constrained to 5 sections in order:

1. Step 1 Intake
2. Step 2 Story Synopsis
3. Step 3 Character Profiles
4. Step 4 Episode Outline
5. Step 5 Full Script Draft
