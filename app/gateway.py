from typing import Any, Dict, Optional, Tuple

import httpx


class GatewayClient:
    def __init__(
        self,
        base_url: str,
        auth_token: str,
        auth_scheme: str,
        timeout_seconds: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token.strip()
        self.auth_scheme = auth_scheme.strip() or "Bearer"
        self.timeout = httpx.Timeout(timeout_seconds)

    def is_configured(self) -> bool:
        return bool(self.base_url)

    async def list_models(self) -> Dict[str, Any]:
        self._assert_base_url()
        headers = self._build_headers()
        endpoint = f"{self.base_url}/models"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError(self._format_gateway_error(response))
        return response.json()

    async def messages(
        self,
        *,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: Optional[float] = None,
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        self._assert_base_url()
        headers = self._build_headers()
        headers["Content-Type"] = "application/json"
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        endpoint = f"{self.base_url}/messages"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(self._format_gateway_error(response))

        body = response.json()
        text = self._extract_text(body)
        if not text:
            raise RuntimeError("Gateway returned empty content for /v1/messages.")
        usage = body.get("usage")
        return text, usage if isinstance(usage, dict) else None

    def _assert_base_url(self) -> None:
        if not self.base_url:
            raise RuntimeError("LLM_SERVICE_BASE_URL is not configured.")

    def _build_headers(self) -> Dict[str, str]:
        if not self.auth_token:
            return {}
        return {"Authorization": f"{self.auth_scheme} {self.auth_token}"}

    def _format_gateway_error(self, response: httpx.Response) -> str:
        raw = response.text.strip()
        if not raw:
            return f"Gateway request failed: HTTP {response.status_code}"
        return f"Gateway request failed: HTTP {response.status_code}, body={raw}"

    def _extract_text(self, payload: Dict[str, Any]) -> str:
        content = payload.get("content")
        if isinstance(content, str):
            return content.strip()
        if not isinstance(content, list):
            return ""

        chunks: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
        return "\n".join(chunks).strip()
