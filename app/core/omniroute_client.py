
"""
BANKAI OmniRoute Client

BANKAI communicates with OmniRoute through its
OpenAI-compatible API.

OmniRoute can then route the request to Ollama
or another configured AI provider.
"""

from __future__ import annotations

import os
from typing import Any

import requests


class OmniRouteClient:
    """Client for the local OmniRoute gateway."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:

        self.base_url = (
            base_url
            or os.getenv(
                "BANKAI_OMNIROUTE_URL",
                "http://127.0.0.1:20128/v1",
            )
        ).rstrip("/")

        self.api_key = (
            api_key
            or os.getenv(
                "BANKAI_OMNIROUTE_KEY",
                "local-bankai",
            )
        )

        self.model = (
            model
            or os.getenv(
                "BANKAI_MODEL",
                "qwen3:0.6b",
            )
        )

    def health(self) -> bool:
        """Check whether OmniRoute is reachable."""

        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    def models(self) -> list[dict[str, Any]]:
        """Return models exposed by OmniRoute."""

        response = requests.get(
            f"{self.base_url}/models",
            headers={
                "Authorization": f"Bearer {self.api_key}"
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("data", [])

    def chat(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Send a chat request through OmniRoute."""

        messages: list[dict[str, str]] = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["choices"][0]["message"]["content"]
        )


if __name__ == "__main__":
    client = OmniRouteClient()

    print("BANKAI OmniRoute Client")
    print("=======================")
    print(f"Endpoint : {client.base_url}")
    print(f"Model    : {client.model}")
    print(f"Healthy  : {client.health()}")
