from __future__ import annotations

import os
from typing import Any


DEFAULT_ROUTES = {
    "knowledge": "openrouter",
    "research": "openrouter",
    "reasoning": "openrouter",
    "coding": "openrouter",
    "review": "openrouter",
}


def get_provider(
    task: str,
) -> str:

    task = (
        task or "knowledge"
    ).lower()

    environment_key = (
        "SOUL_FORGE_"
        + task.upper()
        + "_PROVIDER"
    )

    return os.getenv(
        environment_key,
        DEFAULT_ROUTES.get(
            task,
            "openrouter",
        ),
    )


def route(
    task: str,
) -> dict[str, Any]:

    provider = get_provider(
        task
    )

    return {
        "task": task,
        "provider": provider,
        "architecture": (
            "SOUL_FORGE_AGENT_ROUTER"
        ),
    }
