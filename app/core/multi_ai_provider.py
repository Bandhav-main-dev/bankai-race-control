from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any


class ProviderError(RuntimeError):
    pass


class MultiAIProviderEngine:
    """
    BANKAI V0.5 provider engine.

    Ollama:
        Local HTTP API.

    OpenAI:
        Official OpenAI-compatible HTTP API.

    Anthropic:
        Official Anthropic Messages API.

    Google:
        Gemini generateContent REST API.
    """

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url.rstrip("/")

    # -------------------------------------------------------------------------
    # Generic HTTP
    # -------------------------------------------------------------------------

    def _post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        timeout: int = 180,
    ) -> dict[str, Any]:

        request_headers = {
            "Content-Type": "application/json",
        }

        if headers:
            request_headers.update(headers)

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=request_headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout,
            ) as response:

                raw = response.read().decode("utf-8")
                return json.loads(raw)

        except urllib.error.HTTPError as exc:

            body = exc.read().decode("utf-8", errors="replace")

            raise ProviderError(
                f"HTTP {exc.code}: {body[:1000]}"
            ) from exc

        except urllib.error.URLError as exc:

            raise ProviderError(
                f"Connection failed: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Ollama
    # -------------------------------------------------------------------------

    def ollama(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        data = self._post_json(
            f"{self.ollama_url}/api/chat",
            payload,
        )

        content = (
            data.get("message", {})
            .get("content", "")
        )

        if not content:
            raise ProviderError(
                "Ollama returned an empty response"
            )

        return {
            "provider": "ollama",
            "model": model,
            "content": content,
            "usage": {
                "prompt_tokens": data.get(
                    "prompt_eval_count",
                    0,
                ),
                "completion_tokens": data.get(
                    "eval_count",
                    0,
                ),
            },
        }

    # -------------------------------------------------------------------------
    # OpenAI
    # -------------------------------------------------------------------------

    def openai(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:

        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ProviderError(
                "OPENAI_API_KEY is not configured"
            )

        data = self._post_json(
            "https://api.openai.com/v1/chat/completions",
            {
                "model": model,
                "messages": messages,
            },
            {
                "Authorization": f"Bearer {api_key}",
            },
        )

        choices = data.get("choices", [])

        if not choices:
            raise ProviderError(
                "OpenAI returned no choices"
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        return {
            "provider": "openai",
            "model": model,
            "content": content,
            "usage": data.get("usage", {}),
        }

    # -------------------------------------------------------------------------
    # Anthropic
    # -------------------------------------------------------------------------

    def anthropic(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:

        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            raise ProviderError(
                "ANTHROPIC_API_KEY is not configured"
            )

        system_parts = []

        user_messages = []

        for message in messages:

            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                system_parts.append(content)

            elif role in ("user", "assistant"):
                user_messages.append({
                    "role": role,
                    "content": content,
                })

        payload = {
            "model": model,
            "max_tokens": 2048,
            "messages": user_messages,
        }

        if system_parts:
            payload["system"] = "\n\n".join(system_parts)

        data = self._post_json(
            "https://api.anthropic.com/v1/messages",
            payload,
            {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        blocks = data.get("content", [])

        content = "".join(
            block.get("text", "")
            for block in blocks
            if block.get("type") == "text"
        )

        return {
            "provider": "anthropic",
            "model": model,
            "content": content,
            "usage": data.get("usage", {}),
        }

    # -------------------------------------------------------------------------
    # Google Gemini
    # -------------------------------------------------------------------------

    def google(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:

        api_key = (
            os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )

        if not api_key:
            raise ProviderError(
                "GOOGLE_API_KEY / GEMINI_API_KEY is not configured"
            )

        contents = []

        for message in messages:

            role = message.get("role", "user")

            if role == "system":
                continue

            gemini_role = (
                "model"
                if role == "assistant"
                else "user"
            )

            contents.append({
                "role": gemini_role,
                "parts": [
                    {
                        "text": message.get(
                            "content",
                            "",
                        )
                    }
                ],
            })

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
            f"?key={api_key}"
        )

        data = self._post_json(
            url,
            {
                "contents": contents,
            },
        )

        candidates = data.get("candidates", [])

        if not candidates:
            raise ProviderError(
                "Gemini returned no candidates"
            )

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        content = "".join(
            part.get("text", "")
            for part in parts
        )

        return {
            "provider": "google",
            "model": model,
            "content": content,
            "usage": data.get("usageMetadata", {}),
        }

    # -------------------------------------------------------------------------
    # Unified call
    # -------------------------------------------------------------------------

    def complete(
        self,
        provider: str,
        model: str,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:

        if provider == "ollama":
            return self.ollama(model, messages)

        if provider == "openai":
            return self.openai(model, messages)

        if provider == "anthropic":
            return self.anthropic(model, messages)

        if provider == "google":
            return self.google(model, messages)

        raise ProviderError(
            f"Unsupported provider: {provider}"
        )
