from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .store import load_saved_api_key


class ClaudeError(Exception):
    """Raised when the Claude API request fails."""


class ClaudeClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def chat(self, system_prompt: str, user_message: str, max_tokens: int = 4000) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ClaudeError(_normalize_http_error(exc.code, body)) from exc
        except urllib.error.URLError as exc:
            raise ClaudeError(f"Claude request failed: {exc.reason}") from exc
        text_blocks = data.get("content", [])
        if not text_blocks:
            raise ClaudeError("Claude returned an empty response.")
        return "".join(block.get("text", "") for block in text_blocks).strip()


def get_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or load_saved_api_key()


def _normalize_http_error(status_code: int, body: str) -> str:
    lowered = body.lower()
    if "credit balance is too low" in lowered or "purchase credits" in lowered:
        return "Claude API credits are too low for this key or workspace. Check Anthropic Plans & Billing."
    if "invalid x-api-key" in lowered or "authentication_error" in lowered:
        return "Claude rejected this API key. Run `setup` to replace it."
    return f"Claude request failed: {status_code} {body}"
