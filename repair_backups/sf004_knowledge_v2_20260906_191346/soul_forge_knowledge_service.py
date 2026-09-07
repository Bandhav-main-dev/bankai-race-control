from __future__ import annotations

from typing import Any

from . import soul_forge_notebook_manager as notebook_manager
from . import soul_forge_resource_vault as resource_vault

FUNCTIONAL_RESOURCE_ID = "RES-00002"


def get_resource_with_content(
    resource_id: str,
) -> dict[str, Any] | None:
    """
    Return a fully hydrated Resource Vault record.
    """

    return resource_vault.get_resource_with_content(
        resource_id
    )


def hydrate_resource(
    resource_id: str,
) -> dict[str, Any] | None:
    """
    Hydrate a resource and expose its stored content.

    This is intentionally thin: Resource Vault remains
    the persistence authority.
    """

    resource = resource_vault.get_resource_with_content(
        resource_id
    )

    if resource is None:
        return None

    if "content" not in resource:
        return None

    return resource


def list_notebook_resources(
    notebook_id: str,
) -> list[dict[str, Any]]:
    """
    Return hydrated resources belonging to a notebook.
    """

    resource_ids = (
        notebook_manager.list_notebook_resources(
            notebook_id
        )
    )

    resources = []

    for resource_id in resource_ids:

        resource = hydrate_resource(
            resource_id
        )

        if resource is not None:
            resources.append(resource)

    return resources


def answerable_resources(
    notebook_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Return resources that contain usable text content.

    Resources with empty or missing content are not
    considered answerable.
    """

    if notebook_id is None:
        candidates = resource_vault.list_resources()
    else:
        candidates = resource_vault.list_resources(
            notebook_id
        )

    answerable = []

    for candidate in candidates:

        resource_id = candidate.get("id")

        if not resource_id:
            continue

        resource = hydrate_resource(
            resource_id
        )

        if resource is None:
            continue

        content = resource.get(
            "content",
            ""
        )

        if isinstance(content, str) and content.strip():
            answerable.append(resource)

    return answerable


def search_knowledge(
    query: str,
    notebook_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search Resource Vault content and metadata.

    Matching is intentionally deterministic and local.
    """

    query = (query or "").strip().lower()

    if not query:
        return []

    resources = answerable_resources(
        notebook_id
    )

    results = []

    for resource in resources:

        searchable_parts = [
            str(resource.get("id", "")),
            str(resource.get("name", "")),
            str(resource.get("source_type", "")),
            str(resource.get("notebook_id", "")),
            str(resource.get("content", "")),
        ]

        searchable_text = " ".join(
            searchable_parts
        ).lower()

        if query in searchable_text:
            results.append(resource)

    return results


def build_knowledge_context(
    query: str,
    notebook_id: str | None = None,
    *,
    max_resources: int = 10,
) -> tuple[list[dict[str, Any]], str]:
    """
    Build deterministic context for the Agentic AI layer.

    Returns:
        (
            selected_resources,
            context_text
        )
    """

    max_resources = max(max_resources, 1)

    matches = search_knowledge(
        query,
        notebook_id
    )

    selected = matches[:max_resources]

    context_parts = []

    for resource in selected:

        resource_id = resource.get(
            "id",
            "UNKNOWN"
        )

        name = resource.get(
            "name",
            "Unnamed Resource"
        )

        source_type = resource.get(
            "source_type",
            "unknown"
        )

        notebook = resource.get(
            "notebook_id",
            "unknown"
        )

        content = resource.get(
            "content",
            ""
        )

        context_parts.append(
            "\n".join(
                [
                    f"[RESOURCE_ID] {resource_id}",
                    f"[RESOURCE_NAME] {name}",
                    f"[SOURCE_TYPE] {source_type}",
                    f"[NOTEBOOK_ID] {notebook}",
                    "[CONTENT]",
                    str(content),
                    "[END_RESOURCE]",
                ]
            )
        )

    context_text = "\n\n".join(
        context_parts
    )

    return selected, context_text
