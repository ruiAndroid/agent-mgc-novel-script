import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


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


def _build_llm_service_base_url() -> Tuple[str, str]:
    explicit_base_url = os.getenv("LLM_SERVICE_BASE_URL", "").strip()
    if explicit_base_url:
        return explicit_base_url.rstrip("/"), "explicit"

    proxy_base_url = os.getenv("ZEROCLAW_LLM_PROXY_BASE_URL", "").strip()
    if proxy_base_url:
        return proxy_base_url.rstrip("/"), "zeroclaw-llm-proxy"

    # Keep these env names for validation hint only. They point to control plane UI proxy,
    # not LLM API endpoints.
    instance_id = os.getenv("ZEROCLAW_INSTANCE_ID", "").strip()
    instance_name = os.getenv("ZEROCLAW_INSTANCE_NAME", "").strip()
    if instance_id or instance_name:
        return "", "misconfigured:ui-controller-is-not-llm-api"

    return "", "missing"


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
    llm_service_base_url: str
    llm_service_source: str
    llm_service_api_style: str
    llm_service_auth_token: str
    llm_service_auth_scheme: str


def load_settings() -> Settings:
    env_file = os.getenv("APP_ENV_FILE", ".env.production")
    _load_env_file(env_file)

    llm_service_base_url, llm_service_source = _build_llm_service_base_url()
    llm_service_api_style = os.getenv("LLM_SERVICE_API_STYLE", "auto").strip().lower() or "auto"
    if llm_service_api_style not in {"auto", "chat_completions", "messages"}:
        raise ValueError("LLM_SERVICE_API_STYLE must be one of: auto, chat_completions, messages")
    llm_service_auth_token = (
        os.getenv("LLM_SERVICE_AUTH_TOKEN", "").strip()
        or os.getenv("ZEROCLAW_LLM_TOKEN", "").strip()
    )

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
        llm_service_base_url=llm_service_base_url,
        llm_service_source=llm_service_source,
        llm_service_api_style=llm_service_api_style,
        llm_service_auth_token=llm_service_auth_token,
        llm_service_auth_scheme=os.getenv("LLM_SERVICE_AUTH_SCHEME", "Bearer").strip()
        or "Bearer",
    )


settings = load_settings()
