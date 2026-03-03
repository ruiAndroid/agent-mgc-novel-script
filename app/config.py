import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _load_env_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists() or not env_path.is_file():
        return
    try:
        content = env_path.read_text(encoding="utf-8")
    except OSError:
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _read_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def _read_float(name: str) -> Optional[float]:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    agent_id: str
    workflow_id: str
    skills_dir: str
    default_model: str
    default_max_tokens: int
    default_temperature: Optional[float]
    request_timeout_seconds: int
    gateway_base_url: str
    gateway_token: str
    gateway_anthropic_version: str


def load_settings() -> Settings:
    env_file = os.getenv("APP_ENV_FILE", ".env.production")
    _load_env_file(env_file)

    return Settings(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=_read_int("APP_PORT", 8110, minimum=1),
        agent_id=os.getenv("AGENT_ID", "mgc-novel-to-script").strip() or "mgc-novel-to-script",
        workflow_id=os.getenv("WORKFLOW_ID", "novel-to-script-pipeline").strip()
        or "novel-to-script-pipeline",
        skills_dir=os.getenv("SKILLS_DIR", "./skills").strip() or "./skills",
        default_model=os.getenv("DEFAULT_MODEL", "claude-sonnet-4-6").strip()
        or "claude-sonnet-4-6",
        default_max_tokens=_read_int("DEFAULT_MAX_TOKENS", 2048, minimum=1),
        default_temperature=_read_float("DEFAULT_TEMPERATURE"),
        request_timeout_seconds=_read_int("REQUEST_TIMEOUT_SECONDS", 120, minimum=1),
        gateway_base_url=os.getenv("GATEWAY_BASE_URL", "https://api.ai.fun.tv/v1").strip()
        or "https://api.ai.fun.tv/v1",
        gateway_token=os.getenv("GATEWAY_TOKEN", "").strip(),
        gateway_anthropic_version=os.getenv(
            "GATEWAY_ANTHROPIC_VERSION", "2023-06-01"
        ).strip()
        or "2023-06-01",
    )


settings = load_settings()
