"""
SOUL FORGE routing telemetry.

This module contains application-owned telemetry only.
API keys are never stored here.
"""

from __future__ import annotations

from typing import Any


def normalize_telemetry(
    data: dict[str, Any] | None,
) -> dict[str, Any]:

    data = data or {}

    requested_models = data.get(
        "requested_models",
        [],
    )

    if not isinstance(
        requested_models,
        list,
    ):
        requested_models = [
            str(requested_models)
        ]

    requested_model = (
        data.get(
            "requested_model"
        )
        or (
            requested_models[0]
            if requested_models
            else ""
        )
    )

    actual_model = (
        data.get(
            "actual_model"
        )
        or data.get(
            "selected_model"
        )
        or data.get(
            "model"
        )
        or ""
    )

    fallback = bool(
        requested_model
        and actual_model
        and requested_model != actual_model
    )

    return {
        "task": str(
            data.get(
                "task",
                "",
            )
        ),
        "provider": str(
            data.get(
                "provider",
                "openrouter",
            )
        ),
        "tier": str(
            data.get(
                "tier",
                "",
            )
        ),
        "requested_model": str(
            requested_model
        ),
        "actual_model": str(
            actual_model
        ),
        "requested_models": requested_models,
        "latency_seconds": data.get(
            "latency_seconds",
            data.get(
                "elapsed",
                0,
            ),
        ),
        "status": str(
            data.get(
                "status",
                "",
            )
        ),
        "fallback": fallback,
    }


def format_model_name(
    model_id: str,
) -> str:

    if not model_id:
        return "Unknown"

    if "/" in model_id:
        model_id = model_id.split(
            "/",
            1,
        )[1]

    return (
        model_id
        .replace(
            "-",
            " ",
        )
        .replace(
            "_",
            " ",
        )
        .title()
    )
