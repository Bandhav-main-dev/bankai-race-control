
"""
SOUL FORGE — AI Bridge integration.

This module provides one stable interface to the UI/backend.
"""

from __future__ import annotations

from typing import Any

from app.agentic.ruflo_openrouter_adapter import (
    ruflo_adapter,
)


def generate(
    prompt: str,
    task: str = "general",
    system_prompt: str | None = None,
) -> dict[str, Any]:

    return ruflo_adapter.execute(
        task=task,
        prompt=prompt,
        system_prompt=system_prompt,
    )


def coding(
    prompt: str,
) -> dict[str, Any]:

    return ruflo_adapter.coding(prompt)


def planning(
    prompt: str,
) -> dict[str, Any]:

    return ruflo_adapter.planning(prompt)


def review(
    prompt: str,
) -> dict[str, Any]:

    return ruflo_adapter.review(prompt)
