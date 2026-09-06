from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "soul_forge"

RESOURCE_DIR = DATA_ROOT / "resources"
INDEX_DIR = DATA_ROOT / "index"

RESOURCE_INDEX = INDEX_DIR / "resources.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()


def _ensure():
    RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if not RESOURCE_INDEX.exists():
        RESOURCE_INDEX.write_text(
            "[]",
            encoding="utf-8",
        )


def _load_index() -> list[dict[str, Any]]:
    _ensure()

    try:
        value = json.loads(
            RESOURCE_INDEX.read_text(
                encoding="utf-8"
            )
        )

        return value if isinstance(value, list) else []

    except (OSError, json.JSONDecodeError):
        return []


def _save_index(resources: list[dict[str, Any]]) -> None:
    _ensure()

    tmp = RESOURCE_INDEX.with_suffix(".tmp")

    tmp.write_text(
        json.dumps(
            resources,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    tmp.replace(RESOURCE_INDEX)


def _resource_path(resource_id: str) -> Path:
    return RESOURCE_DIR / f"{resource_id}.json"


def _content_hash(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def register_resource(
    resource_id: str,
    *,
    notebook_id: str,
    name: str,
    content: str,
    source_type: str = "text",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if not resource_id:
        raise ValueError("resource_id is required")

    if not notebook_id:
        raise ValueError("notebook_id is required")

    if not name:
        raise ValueError("name is required")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    resources = _load_index()

    resource = {
        "id": resource_id,
        "notebook_id": notebook_id,
        "name": name,
        "source_type": source_type,
        "content_length": len(content),
        "content_hash": _content_hash(content),
        "created_at": _now(),
        "updated_at": _now(),
        "metadata": metadata or {},
    }

    resources = [
        item
        for item in resources
        if item.get("id") != resource_id
    ]

    resources.append(resource)

    atomic = _resource_path(resource_id)

    atomic.write_text(
        json.dumps(
            {
                **resource,
                "content": content,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    _save_index(resources)

    return resource


def get_resource(
    resource_id: str,
) -> dict[str, Any] | None:

    path = _resource_path(resource_id)

    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError):
        return None


def get_resource_with_content(
    resource_id: str,
) -> dict[str, Any] | None:

    return get_resource(resource_id)


def list_resources(
    notebook_id: str | None = None,
) -> list[dict[str, Any]]:

    resources = _load_index()

    if notebook_id is None:
        return resources

    return [
        item
        for item in resources
        if item.get("notebook_id") == notebook_id
    ]


def search_resources(
    query: str,
    notebook_id: str | None = None,
) -> list[dict[str, Any]]:

    query = (query or "").strip().lower()

    if not query:
        return []

    resources = list_resources(notebook_id)

    results = []

    for resource in resources:

        haystack = " ".join(
            [
                str(resource.get("id", "")),
                str(resource.get("name", "")),
                str(resource.get("source_type", "")),
                json.dumps(
                    resource.get("metadata", {}),
                    ensure_ascii=False,
                ),
            ]
        ).lower()

        if query in haystack:

            full = get_resource(
                resource["id"]
            )

            if full:
                results.append(full)

    return results


def delete_resource(
    resource_id: str,
) -> bool:

    path = _resource_path(resource_id)

    if not path.exists():
        return False

    path.unlink()

    resources = [
        item
        for item in _load_index()
        if item.get("id") != resource_id
    ]

    _save_index(resources)

    return True
