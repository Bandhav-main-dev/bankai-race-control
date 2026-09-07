from __future__ import annotations

from typing import Any

from app.core import soul_forge_rag_engine as rag_engine
from app.agents import soul_forge_knowledge_agent as knowledge_agent


def search_knowledge(
    query: str,
    notebook_id: str | None = None,
) -> list[dict[str, Any]]:

    return rag_engine.search(
        query,
        notebook_id,
        top_k=10,
    )


def build_knowledge_context(
    query: str,
    notebook_id: str | None = None,
    *,
    max_resources: int = 10,
) -> tuple[
    list[dict[str, Any]],
    str,
]:

    results, context = (
        rag_engine.build_context(
            query,
            notebook_id,
            top_k=max_resources,
        )
    )

    return results, context


def ask_knowledge(
    question: str,
    notebook_id: str | None = None,
    *,
    top_k: int = 8,
    provider: str = "openrouter",
    model: str | None = None,
) -> dict[str, Any]:

    return knowledge_agent.ask_knowledge(
        question,
        notebook_id,
        top_k=top_k,
        provider=provider,
        model=model,
    )


def get_knowledge_history(
    notebook_id: str,
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:

    return knowledge_agent.load_history(
        notebook_id,
        limit=limit,
    )


def get_rag_stats() -> dict[str, Any]:

    return rag_engine.index_stats()
