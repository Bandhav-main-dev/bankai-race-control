from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMMARY_DIR = (
    PROJECT_ROOT
    / "data"
    / "soul_forge"
    / "rag"
    / "summaries"
)

SUMMARY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _now() -> str:

    return datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    ).isoformat()


def summarize_resource(
    resource_id: str,
    resource_name: str,
    content: str,
    *,
    provider: str = "gemini",
    model: str | None = None,
) -> dict[str, Any]:

    if not content.strip():
        return {
            "resource_id": resource_id,
            "resource_name": resource_name,
            "summary": "",
            "status": "empty",
        }

    # Keep very large resources manageable.
    source = content[:50000]

    prompt = f"""
Create a structured knowledge summary of this resource.

RESOURCE:
{resource_name}

CONTENT:
{source}

Return:

SUMMARY:
A concise but useful overview.

KEY TOPICS:
A bullet list.

KEY CONCEPTS:
A bullet list.

IMPORTANT ENTITIES:
A bullet list.

KEY FACTS:
A bullet list of facts supported directly by the resource.

DOCUMENT PURPOSE:
One paragraph.

Do not invent information.
"""

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required for summaries."
        )

    model = (
        model
        or os.getenv(
            "SOUL_FORGE_GEMINI_MODEL",
            "gemini-2.5-flash",
        )
    )

    response = requests.post(
        (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
        ),
        params={
            "key": api_key,
        },
        json={
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    summary = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )

    result = {
        "resource_id": resource_id,
        "resource_name": resource_name,
        "created_at": _now(),
        "provider": "gemini",
        "model": model,
        "summary": summary,
        "word_count": len(
            content.split()
        ),
    }

    path = (
        SUMMARY_DIR
        / f"{resource_id}.json"
    )

    path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return result


def get_summary(
    resource_id: str,
) -> dict[str, Any] | None:

    path = (
        SUMMARY_DIR
        / f"{resource_id}.json"
    )

    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None
