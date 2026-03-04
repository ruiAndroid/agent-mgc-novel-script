# agent-mgc-novel-script

Independent DreamWorks novel-to-script agent application.

## Features

- Single-purpose agent: novel -> script pipeline
- Skills are externalized as JSON files under `skills/`
- Uses framework-level LLM service protocol (typically ZeroClaw in Docker):
  - Preferred: `POST /v1/chat/completions`
  - Compatible fallback: `POST /v1/messages`
  - Optional: `GET /v1/models`
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
LLM_SERVICE_BASE_URL=http://<zeroclaw-host-or-container-ip>:<gateway-host-port>/v1
LLM_SERVICE_API_STYLE=auto
```

Or:

```env
ZEROCLAW_LLM_PROXY_BASE_URL=http://<your-llm-proxy>/v1
```

Optional:

```env
# Explicit preferred key
LLM_SERVICE_BASE_URL=http://<custom-llm-service>/v1
LLM_SERVICE_API_STYLE=chat_completions
```

Optional (only if your ZeroClaw gateway has `ZEROCLAW_API_KEY` enabled):

```env
LLM_SERVICE_AUTH_TOKEN=replace-with-token
LLM_SERVICE_AUTH_SCHEME=Bearer
```

`LLM_SERVICE_API_STYLE` values:

- `auto` (recommended): try `/chat/completions`, fallback to `/messages`
- `chat_completions`: force `/chat/completions`
- `messages`: force `/messages`

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
- `zeroclaw-llm-proxy`

Health response also includes `llm_service_api_style` for troubleshooting.

Important: in current `fun-ai-claw-plane`, zeroclaw containers are started with
`<image> gateway ...`. Your FastAPI agent should run as a separate container service
and call the framework LLM service URL. Keep vendor tokens in framework/runtime side,
not in agent business code.

Note: `ZEROCLAW_CONTROL_API_BASE_URL` + `/fun-claw/ui-controller/{instanceId}` is UI proxy path,
not LLM API path. Do not use it as `LLM_SERVICE_BASE_URL`.
