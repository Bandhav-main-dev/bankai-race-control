
"""
SOUL FORGE — Ruflo / OpenRouter integration adapter.

Ruflo remains the agent orchestration layer.
OpenRouter remains the model gateway.
"""

from __future__ import annotations

import os
from typing import Any

from app.core.openrouter_provider import (
    ask_soul_forge,
)


class SoulForgeRufloAdapter:

    def __init__(self) -> None:

        if not os.environ.get(
            "OPENROUTER_API_KEY"
        ):

            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

    def execute(
        self,
        task: str,
        prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:

        return ask_soul_forge(
            prompt=prompt,
            task=task,
            system_prompt=system_prompt,
        )

    def coding(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        return self.execute(
            task="coding",
            prompt=prompt,
            system_prompt=(
                "You are the SOUL FORGE coding agent. "
                "Analyze carefully. "
                "Produce correct, maintainable code. "
                "Never claim a file was modified unless "
                "the tool actually modified it."
            ),
        )

    def planning(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        return self.execute(
            task="planning",
            prompt=prompt,
            system_prompt=(
                "You are the SOUL FORGE planning agent. "
                "Break complex work into precise steps."
            ),
        )

    def review(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        return self.execute(
            task="review",
            prompt=prompt,
            system_prompt=(
                "You are the SOUL FORGE review agent. "
                "Inspect the proposed solution for bugs, "
                "security issues, regressions, and correctness."
            ),
        )


ruflo_adapter = SoulForgeRufloAdapter()
