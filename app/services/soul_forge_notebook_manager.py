from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "soul_forge"

NOTEBOOK_DIR = DATA_ROOT / "notebooks"
NOTEBOOK_INDEX = DATA_ROOT / "index" / "notebooks.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()


def _ensure():
    NOTEBOOK_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    NOTEBOOK_INDEX.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not NOTEBOOK_INDEX.exists():
        NOTEBOOK_INDEX.write_text(
            "[]",
            encoding="utf-8",
        )


def _load() -> list[dict[str, Any]]:
    _ensure()

    try:
        value = json.loads(
            NOTEBOOK_INDEX.read_text(
                encoding="utf-8"
            )
        )

        return value if isinstance(value, list) else []

    except (OSError, json.JSONDecodeError):
        return []


def _save(items: list[dict[str, Any]]):
    _ensure()

    tmp = NOTEBOOK_INDEX.with_suffix(".tmp")

    tmp.write_text(
        json.dumps(
            items,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    tmp.replace(NOTEBOOK_INDEX)


def register_notebook(
    notebook_id: str,
    *,
    name: str,
    description: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if not notebook_id:
        raise ValueError(
            "notebook_id is required"
        )

    if not name:
        raise ValueError(
            "name is required"
        )

    notebooks = _load()

    notebook = {
        "id": notebook_id,
        "name": name,
        "description": description,
        "created_at": _now(),
        "updated_at": _now(),
        "metadata": metadata or {},
    }

    notebooks = [
        item
        for item in notebooks
        if item.get("id") != notebook_id
    ]

    notebooks.append(notebook)

    notebook_file = (
        NOTEBOOK_DIR /
        f"{notebook_id}.json"
    )

    notebook_file.write_text(
        json.dumps(
            notebook,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    _save(notebooks)

    return notebook


def get_notebook(
    notebook_id: str,
) -> dict[str, Any] | None:

    path = (
        NOTEBOOK_DIR /
        f"{notebook_id}.json"
    )

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


def list_notebooks() -> list[dict[str, Any]]:
    return _load()


def notebook_exists(
    notebook_id: str,
) -> bool:

    return get_notebook(
        notebook_id
    ) is not None


def add_resource_to_notebook(
    notebook_id: str,
    resource_id: str,
) -> dict[str, Any]:

    notebook = get_notebook(
        notebook_id
    )

    if notebook is None:
        raise ValueError(
            f"Notebook not found: {notebook_id}"
        )

    resources = list(
        notebook.get(
            "resource_ids",
            []
        )
    )

    if resource_id not in resources:
        resources.append(
            resource_id
        )

    notebook["resource_ids"] = resources
    notebook["updated_at"] = _now()

    notebook_file = (
        NOTEBOOK_DIR /
        f"{notebook_id}.json"
    )

    notebook_file.write_text(
        json.dumps(
            notebook,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    notebooks = _load()

    for index, item in enumerate(notebooks):

        if item.get("id") == notebook_id:
            notebooks[index] = notebook

    _save(notebooks)

    return notebook


def list_notebook_resources(
    notebook_id: str,
) -> list[str]:

    notebook = get_notebook(
        notebook_id
    )

    if notebook is None:
        return []

    return list(
        notebook.get(
            "resource_ids",
            []
        )
    )
