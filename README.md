# agent-mgc-novel-script

Independent DreamWorks novel-to-script agent application.

## Features

- Single-purpose agent: novel -> script pipeline
- Skills are externalized as JSON files under `skills/`
- Uses framework-level LLM service protocol (typically ZeroClaw):
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
ZEROCLAW_CONTROL_API_BASE_URL=http://fun-ai-claw-api:8080
ZEROCLAW_INSTANCE_NAME=mgc-novel-agent
```

Then the app automatically resolves:

`{ZEROCLAW_CONTROL_API_BASE_URL}/fun-claw/ui-controller/{resolved-instance-id}/v1`

Optional:

```env
# Explicit override, has higher priority than ZEROCLAW_* variables.
LLM_SERVICE_BASE_URL=http://<custom-llm-service>/v1
# If you already know UUID, it has higher priority than instance name lookup.
ZEROCLAW_INSTANCE_ID=<your-claw-instance-uuid>
# Timeout for auto lookup via GET /v1/instances
ZEROCLAW_CONTROL_API_TIMEOUT_SECONDS=3
```

Optional (only if your ZeroClaw gateway has `ZEROCLAW_API_KEY` enabled):

```env
LLM_SERVICE_AUTH_TOKEN=replace-with-token
LLM_SERVICE_AUTH_SCHEME=Bearer
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
- `GET /v1/health`
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

## Docker deploy (with zeroclaw environment)

Build image:

```bash
docker build -t mgc-novel-agent:latest .
```

Run as independent service container:

```bash
docker run -d --name mgc-novel-agent \
  --restart unless-stopped \
  --env-file .env.production \
  -e APP_ENV_FILE=/app/.env.production \
  -e SKILLS_DIR=/app/skills \
  -p 8110:8110 \
  mgc-novel-agent:latest
```

Or use compose:

```bash
export ZEROCLAW_DOCKER_NETWORK=fun-ai-claw-net
docker compose -f docker-compose.agent.yml up -d --build
```

Check runtime wiring:

```bash
curl http://127.0.0.1:8110/health
```

`llm_service_source` should be one of:
- `explicit`
- `claw-api-proxy:instance-id`
- `claw-api-proxy:instance-name(...)`

Important: in current `fun-ai-claw-plane`, zeroclaw containers are started with
`<image> gateway ...`. Your FastAPI agent should run as a separate container service
and call the framework LLM service URL. Keep vendor tokens in framework/runtime side,
not in agent business code.
