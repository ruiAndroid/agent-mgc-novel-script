from typing import Any, Dict, Optional, Tuple

import httpx


class GatewayClient:
    def __init__(
        self,
        base_url: str,
        api_style: str,
        auth_token: str,
        auth_scheme: str,
        timeout_seconds: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_style = api_style
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
            return {
                "object": "list",
                "data": [{"id": "unknown", "object": "model"}],
                "source": "synthetic-fallback",
                "reason": self._format_gateway_error(response),
            }
        return self._parse_json(response, endpoint)

    async def messages(
        self,
        *,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: Optional[float] = None,
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        self._assert_base_url()
        style = self.api_style
        if style == "chat_completions":
            return await self._chat_completions(model, prompt, max_tokens, temperature)
        if style == "messages":
            return await self._messages(model, prompt, max_tokens, temperature)

        # auto mode: prefer ZeroClaw/OpenAI chat-completions endpoint,
        # fallback to legacy /messages endpoint.
        try:
            return await self._chat_completions(model, prompt, max_tokens, temperature)
        except RuntimeError as exc:
            if not self._is_endpoint_not_supported(str(exc)):
                raise
        return await self._messages(model, prompt, max_tokens, temperature)

    async def _chat_completions(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: Optional[float],
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        headers = self._build_headers()
        headers["Content-Type"] = "application/json"
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        endpoint = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(self._format_gateway_error(response))
        body = self._parse_json(response, endpoint)
        text = self._extract_chat_completions_text(body)
        if not text:
            raise RuntimeError("Gateway returned empty content for /v1/chat/completions.")
        usage = body.get("usage")
        return text, usage if isinstance(usage, dict) else None

    async def _messages(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: Optional[float],
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
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
        body = self._parse_json(response, endpoint)
        text = self._extract_messages_text(body)
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

    def _is_endpoint_not_supported(self, error_text: str) -> bool:
        normalized = error_text.lower()
        return "http 404" in normalized or "http 405" in normalized or "http 501" in normalized

    def _parse_json(self, response: httpx.Response, endpoint: str) -> Dict[str, Any]:
        try:
            body = response.json()
        except ValueError as exc:
            content_type = response.headers.get("content-type", "")
            snippet = response.text.strip().replace("\n", " ")
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            raise RuntimeError(
                "Gateway returned non-JSON response: "
                f"endpoint={endpoint}, status={response.status_code}, "
                f"content_type={content_type}, body={snippet}"
            ) from exc
        if not isinstance(body, dict):
            raise RuntimeError(
                f"Gateway returned invalid JSON payload type for {endpoint}: {type(body).__name__}"
            )
        return body

    def _extract_messages_text(self, payload: Dict[str, Any]) -> str:
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

    def _extract_chat_completions_text(self, payload: Dict[str, Any]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first = choices[0]
        if not isinstance(first, dict):
            return ""
        message = first.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if not isinstance(content, list):
            return ""
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
        return "\n".join(chunks).strip()
