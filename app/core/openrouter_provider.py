
"""
SOUL FORGE OpenRouter production provider.

Responsibilities:
    - model routing
    - three-model fallback chains
    - OpenRouter communication
    - response extraction
    - selected-model reporting
    - emergency Ollama fallback

This module never writes API keys to disk.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


# Resolve the repository root from this file so the provider works
# both locally in Colab and on Streamlit Cloud.
PROJECT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    PROJECT
    / "config"
    / "soul_forge_multi_tier_models.json"
)


class OpenRouterProvider:

    def __init__(
        self,
        config_path: Path | None = None,
    ) -> None:

        self.config_path = (
            config_path
            or CONFIG_FILE
        )

        self.api_key = os.environ.get(
            "OPENROUTER_API_KEY"
        )

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

        self.config = self._load_config()

        self.base_url = self.config[
            "openrouter"
        ][
            "base_url"
        ]

        self.timeout = self.config[
            "openrouter"
        ].get(
            "timeout_seconds",
            180,
        )

        try:

            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

        except Exception as exc:

            raise RuntimeError(
                "Unable to initialize OpenRouter client: "
                f"{exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # CONFIG
    # -------------------------------------------------------------------------

    def _load_config(self) -> dict[str, Any]:

        if not self.config_path.exists():

            raise FileNotFoundError(
                f"Missing configuration: "
                f"{self.config_path}"
            )

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # -------------------------------------------------------------------------
    # MODEL ROUTING
    # -------------------------------------------------------------------------

    def get_tier(
        self,
        task: str,
    ) -> str:

        task = (
            task
            .upper()
            .strip()
        )

        routing = self.config.get(
            "task_routing",
            {},
        )

        return routing.get(
            task,
            "tier_1_primary",
        )

    def get_models(
        self,
        task: str,
    ) -> list[str]:

        tier = self.get_tier(task)

        tiers = self.config.get(
            "tiers",
            {},
        )

        models = tiers.get(
            tier,
            [],
        )

        # OpenRouter model fallback requests
        # are intentionally limited to 3 models.
        return list(models[:3])

    # -------------------------------------------------------------------------
    # RESPONSE PARSER
    # -------------------------------------------------------------------------

    @staticmethod
    def extract_content(
        response: Any,
    ) -> str:

        if response is None:
            return ""

        choices = getattr(
            response,
            "choices",
            None,
        )

        if not choices:
            return ""

        message = getattr(
            choices[0],
            "message",
            None,
        )

        if message is None:
            return ""

        content = getattr(
            message,
            "content",
            None,
        )

        if isinstance(content, str):

            return content.strip()

        if isinstance(content, list):

            parts = []

            for item in content:

                if isinstance(
                    item,
                    str,
                ):

                    parts.append(item)

                elif isinstance(
                    item,
                    dict,
                ):

                    text = item.get(
                        "text"
                    )

                    if text:
                        parts.append(
                            str(text)
                        )

            return "".join(parts).strip()

        for attribute in (
            "text",
            "output",
            "answer",
        ):

            value = getattr(
                message,
                attribute,
                None,
            )

            if isinstance(
                value,
                str,
            ):

                return value.strip()

        return ""

    # -------------------------------------------------------------------------
    # REQUEST
    # -------------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system: str = "",
        task: str = "CHAT",
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:

        models = self.get_models(task)

        if not models:

            raise RuntimeError(
                f"No models configured for task {task}"
            )

        messages = []

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

        started = time.time()

        response = self.client.chat.completions.create(

            model=models[0],

            messages=messages,

            temperature=temperature,

            max_tokens=max_tokens,

            extra_body={
                "models": models,
            },
        )

        elapsed = (
            time.time()
            - started
        )

        content = self.extract_content(
            response
        )

        selected_model = getattr(
            response,
            "model",
            models[0],
        )

        return {
            "success": bool(content),

            "provider": "openrouter",

            "task": task,

            "tier": self.get_tier(task),

            "requested_model": models[0],

            "requested_models": models,

            "selected_model": selected_model,

            "content": content,

            "elapsed": elapsed,

            "response": response,
        }

    # -------------------------------------------------------------------------
    # SIMPLE COMPATIBILITY API
    # -------------------------------------------------------------------------

    def ask(
        self,
        prompt: str,
        system: str = "",
        task: str = "CHAT",
    ) -> str:

        result = self.generate(
            prompt=prompt,
            system=system,
            task=task,
        )

        return result["content"]


_provider: OpenRouterProvider | None = None


def get_openrouter_provider() -> OpenRouterProvider:

    global _provider

    if _provider is None:

        _provider = OpenRouterProvider()

    return _provider
