import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from urllib import error as url_error
from urllib import request as url_request


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


def _resolve_instance_id_by_name(
    control_api_base_url: str,
    instance_name: str,
    timeout_seconds: int,
) -> str:
    endpoint = f"{control_api_base_url.rstrip('/')}/v1/instances"
    request = url_request.Request(
        endpoint,
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with url_request.urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read().decode("utf-8", errors="replace")
    except (url_error.URLError, TimeoutError, ValueError):
        return ""

    try:
        body = json.loads(payload)
    except json.JSONDecodeError:
        return ""

    items = []
    if isinstance(body, dict):
        if isinstance(body.get("items"), list):
            items = body["items"]
        elif isinstance(body.get("data"), list):
            items = body["data"]
    if not isinstance(items, list):
        return ""

    normalized_target = instance_name.strip().lower()
    if not normalized_target:
        return ""

    matched = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        instance_id = item.get("id")
        if not isinstance(name, str) or not isinstance(instance_id, str):
            continue
        if name.strip().lower() == normalized_target:
            matched.append(item)

    if not matched:
        return ""

    for item in matched:
        status = item.get("status")
        if isinstance(status, str) and status.strip().upper() == "RUNNING":
            return item["id"].strip()

    return matched[0]["id"].strip()


def _build_llm_service_base_url() -> Tuple[str, str]:
    explicit_base_url = os.getenv("LLM_SERVICE_BASE_URL", "").strip()
    if explicit_base_url:
        return explicit_base_url.rstrip("/"), "explicit"

    control_api_base_url = os.getenv(
        "ZEROCLAW_CONTROL_API_BASE_URL", "http://fun-ai-claw-api:8080"
    ).strip()
    instance_id = os.getenv("ZEROCLAW_INSTANCE_ID", "").strip()
    if control_api_base_url and instance_id:
        return (
            f"{control_api_base_url.rstrip('/')}/fun-claw/ui-controller/{instance_id}/v1",
            "claw-api-proxy:instance-id",
        )

    instance_name = (
        os.getenv("ZEROCLAW_INSTANCE_NAME", "").strip()
        or os.getenv("AGENT_ID", "").strip()
    )
    if control_api_base_url and instance_name:
        timeout_seconds = _read_int("ZEROCLAW_CONTROL_API_TIMEOUT_SECONDS", 3, minimum=1)
        resolved_instance_id = _resolve_instance_id_by_name(
            control_api_base_url=control_api_base_url,
            instance_name=instance_name,
            timeout_seconds=timeout_seconds,
        )
        if resolved_instance_id:
            return (
                f"{control_api_base_url.rstrip('/')}/fun-claw/ui-controller/{resolved_instance_id}/v1",
                f"claw-api-proxy:instance-name({instance_name})",
            )
        return "", f"missing:instance-name-not-found({instance_name})"

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
    llm_service_auth_token: str
    llm_service_auth_scheme: str


def load_settings() -> Settings:
    env_file = os.getenv("APP_ENV_FILE", ".env.production")
    _load_env_file(env_file)

    llm_service_base_url, llm_service_source = _build_llm_service_base_url()
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
        llm_service_auth_token=llm_service_auth_token,
        llm_service_auth_scheme=os.getenv("LLM_SERVICE_AUTH_SCHEME", "Bearer").strip()
        or "Bearer",
    )


settings = load_settings()
