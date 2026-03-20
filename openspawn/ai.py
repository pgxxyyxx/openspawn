from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from collections.abc import Generator

from .store import load_saved_api_key


class ClaudeError(Exception):
    """Raised when the Claude API request fails."""


class ClaudeClient:
    STREAM_TIMEOUT_SECONDS = 120

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def chat(self, system_prompt: str, user_message: str, max_tokens: int = 4000) -> str:
        return self.chat_multi(system_prompt, [{"role": "user", "content": user_message}], max_tokens=max_tokens)

    def chat_multi(self, system_prompt: str, messages: list[dict[str, str]], max_tokens: int = 4000) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages,
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

    def chat_multi_stream(
        self, system_prompt: str, messages: list[dict[str, str]], max_tokens: int = 4000
    ) -> Generator[str, None, None]:
        payload = json.dumps(
            {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages,
                "stream": True,
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
            with urllib.request.urlopen(request, timeout=self.STREAM_TIMEOUT_SECONDS) as response:
                yield from self._iter_sse_text(response)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ClaudeError(_normalize_http_error(exc.code, body)) from exc
        except urllib.error.URLError as exc:
            raise ClaudeError(f"Claude request failed: {exc.reason}") from exc
        except socket.timeout as exc:
            raise ClaudeError("Claude streaming request timed out.") from exc
        except OSError as exc:
            raise ClaudeError(f"Claude streaming request failed: {exc.strerror or exc}") from exc

    def _iter_sse_text(self, response) -> Generator[str, None, None]:
        event_type = ""
        data_lines: list[str] = []
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                if event_type == "content_block_delta" and data_lines:
                    payload = _parse_sse_payload(data_lines)
                    delta = payload.get("delta", {})
                    text = delta.get("text", "")
                    if text:
                        yield text
                elif event_type == "error" and data_lines:
                    payload = _parse_sse_payload(data_lines)
                    error = payload.get("error", {})
                    if isinstance(error, dict):
                        raise ClaudeError(_normalize_sse_error(error))
                    raise ClaudeError(str(error or payload))
                elif event_type == "message_stop":
                    return
                event_type = ""
                data_lines = []
                continue
            if line.startswith("event:"):
                event_type = line.partition(":")[2].strip()
                continue
            if line.startswith("data:"):
                data_lines.append(line.partition(":")[2].strip())


def get_api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or load_saved_api_key()


def _normalize_http_error(status_code: int, body: str) -> str:
    lowered = body.lower()
    if "credit balance is too low" in lowered or "purchase credits" in lowered:
        return "Claude API credits are too low for this key or workspace. Check Anthropic Plans & Billing."
    if "invalid x-api-key" in lowered or "authentication_error" in lowered:
        return "Claude rejected this API key. Run `setup` to replace it."
    return f"Claude request failed: {status_code} {body}"


def _parse_sse_payload(data_lines: list[str]) -> dict[str, object]:
    try:
        return json.loads("\n".join(data_lines))
    except json.JSONDecodeError as exc:
        raise ClaudeError("Claude returned an invalid streaming event.") from exc


def _normalize_sse_error(error: dict[str, object]) -> str:
    return _normalize_http_error(400, json.dumps(error))
