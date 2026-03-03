# agent-mgc-novel-script

Independent DreamWorks novel-to-script agent application.

## Features

- Single-purpose agent: novel -> script pipeline
- Skills are externalized as JSON files under `skills/`
- Reuses the same unified gateway protocol:
  - `GET /v1/models`
  - `POST /v1/messages`
- Built-in 5-step business flow:
  - `novel-intake-parse` (local deterministic summary)
  - `novel-story-synopsis-generate`
  - `novel-character-profile-generate`
  - `novel-episode-outline-generate`
  - `novel-full-script-generate`

## Quick start

```bash
cd agent-mgc-novel-script
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env.production
```

Edit `.env.production` and set at least:

```env
GATEWAY_TOKEN=replace-with-your-token
```

Skill files:

- `skills/novel-intake-parse.json`
- `skills/novel-story-synopsis-generate.json`
- `skills/novel-character-profile-generate.json`
- `skills/novel-episode-outline-generate.json`
- `skills/novel-full-script-generate.json`

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8110
```

## APIs

- `GET /health`
- `GET /v1/models`
- `POST /v1/novel-to-script`

Request example:

```json
{
  "novel_content": "your novel text...",
  "novel_type": "urban fantasy",
  "target_audience": "18-30",
  "expected_episode_count": 12,
  "model": "claude-sonnet-4-6",
  "max_tokens": 2048
}
```

## Linux systemd (zeroclaw)

Example unit file:

```ini
[Unit]
Description=agent-mgc-novel-script
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/agent-mgc-novel-script
Environment="APP_ENV_FILE=.env.production"
ExecStart=/opt/agent-mgc-novel-script/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8110
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
