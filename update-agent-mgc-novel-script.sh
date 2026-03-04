#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/agent-mgc-novel-script}"
SERVICE_NAME="${SERVICE_NAME:-agent-mgc-novel-script}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
GIT_BRANCH="${GIT_BRANCH:-main}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8110/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-20}"
HEALTH_WAIT_SECONDS="${HEALTH_WAIT_SECONDS:-2}"
PYTHON_BIN="${PYTHON_BIN:-}"
PIP_EXTRA_ARGS="${PIP_EXTRA_ARGS:-}"
RECREATE_VENV="${RECREATE_VENV:-false}"
DEPLOY_MODE="${DEPLOY_MODE:-systemd}"   # systemd | docker
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.agent.yml}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_cmd() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || fail "${cmd} not found"
}

python_major_minor() {
  local bin="$1"
  "${bin}" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")'
}

python_is_supported() {
  local bin="$1"
  local major_minor
  major_minor="$(python_major_minor "${bin}")"
  local major="${major_minor%%.*}"
  local minor="${major_minor##*.}"
  [[ "${major}" -gt 3 ]] || ([[ "${major}" -eq 3 ]] && [[ "${minor}" -ge 8 ]])
}

resolve_python_bin() {
  if [[ -n "${PYTHON_BIN}" ]]; then
    require_cmd "${PYTHON_BIN}"
    python_is_supported "${PYTHON_BIN}" || fail "Python ${PYTHON_BIN} is too old ($(python_major_minor "${PYTHON_BIN}")). Need >= 3.8."
    return
  fi

  local candidates=(
    python3.12 python3.11 python3.10 python3.9 python3.8 python3
    /usr/local/bin/python3.12 /usr/local/bin/python3.11 /usr/local/bin/python3.10 /usr/local/bin/python3.9 /usr/local/bin/python3.8
    /usr/bin/python3.12 /usr/bin/python3.11 /usr/bin/python3.10 /usr/bin/python3.9 /usr/bin/python3.8
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ "${c}" = /* ]]; then
      if [[ -x "${c}" ]] && python_is_supported "${c}"; then
        PYTHON_BIN="${c}"
        return
      fi
    else
      if command -v "${c}" >/dev/null 2>&1 && python_is_supported "${c}"; then
        PYTHON_BIN="${c}"
        return
      fi
    fi
  done

  fail "No supported Python found (>=3.8). Install python3.11 or set PYTHON_BIN=/path/to/python."
}

ensure_venv_python() {
  local target_major_minor
  target_major_minor="$(python_major_minor "${PYTHON_BIN}")"

  if [[ "${RECREATE_VENV}" == "true" ]]; then
    echo "RECREATE_VENV=true, removing existing .venv"
    rm -rf .venv
  fi

  if [[ -d ".venv" && -x ".venv/bin/python" ]]; then
    local venv_major_minor
    venv_major_minor="$(python_major_minor ".venv/bin/python" || true)"
    if [[ -z "${venv_major_minor}" || "${venv_major_minor}" != "${target_major_minor}" ]]; then
      echo "Existing .venv Python is ${venv_major_minor:-unknown}, target is ${target_major_minor}; recreating"
      rm -rf .venv
    fi
  elif [[ -d ".venv" ]]; then
    echo "Existing .venv is broken, recreating"
    rm -rf .venv
  fi

  if [[ ! -d ".venv" ]]; then
    "${PYTHON_BIN}" -m venv .venv
  fi
}

check_health() {
  local i
  for ((i=1; i<=HEALTH_RETRIES; i++)); do
    if curl -fsS "${HEALTH_URL}" >/dev/null 2>&1; then
      echo "SUCCESS: health check passed (${HEALTH_URL})"
      return 0
    fi
    sleep "${HEALTH_WAIT_SECONDS}"
  done
  return 1
}

if [[ ! -d "${APP_DIR}" ]]; then
  fail "APP_DIR is invalid: ${APP_DIR}"
fi

require_cmd git
require_cmd curl

if ! git -C "${APP_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "APP_DIR is not a git repository: ${APP_DIR}"
fi

cd "${APP_DIR}"

if [[ -n "$(git status --porcelain)" ]]; then
  fail "Working tree has local changes. Commit/stash them before update."
fi

echo "[1/5] Pull latest code from ${GIT_REMOTE}/${GIT_BRANCH}"
git fetch "${GIT_REMOTE}" "${GIT_BRANCH}"
git checkout "${GIT_BRANCH}"
git pull --ff-only "${GIT_REMOTE}" "${GIT_BRANCH}"

if [[ "${DEPLOY_MODE}" == "systemd" ]]; then
  require_cmd systemctl
  resolve_python_bin

  echo "[2/5] Sync venv and dependencies"
  ensure_venv_python
  .venv/bin/python -m pip install --upgrade pip
  # shellcheck disable=SC2086
  .venv/bin/python -m pip install ${PIP_EXTRA_ARGS} -r requirements.txt

  echo "[3/5] Restart service ${SERVICE_NAME}"
  systemctl restart "${SERVICE_NAME}"

  echo "[4/5] Health check ${HEALTH_URL}"
  if ! check_health; then
    echo "ERROR: health check failed"
    systemctl --no-pager --full status "${SERVICE_NAME}" || true
    journalctl -u "${SERVICE_NAME}" -n 100 --no-pager || true
    exit 1
  fi

  echo "[5/5] Show service status"
  systemctl --no-pager --full status "${SERVICE_NAME}" | head -n 20
  exit 0
fi

if [[ "${DEPLOY_MODE}" == "docker" ]]; then
  require_cmd docker

  echo "[2/4] Build and restart docker service"
  docker compose -f "${COMPOSE_FILE}" up -d --build

  echo "[3/4] Health check ${HEALTH_URL}"
  if ! check_health; then
    echo "ERROR: health check failed"
    docker compose -f "${COMPOSE_FILE}" ps || true
    docker compose -f "${COMPOSE_FILE}" logs --tail 100 || true
    exit 1
  fi

  echo "[4/4] Show compose status"
  docker compose -f "${COMPOSE_FILE}" ps
  exit 0
fi

fail "Unsupported DEPLOY_MODE=${DEPLOY_MODE}. Use systemd or docker."
