from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from app.core import soul_forge_rag_engine as rag_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HISTORY_DIR = (
    PROJECT_ROOT
    / "data"
    / "soul_forge"
    / "rag"
    / "history"
)

HISTORY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


KNOWLEDGE_SYSTEM_PROMPT = """
You are the SOUL FORGE Knowledge Agent.

You are a source-grounded RAG assistant.

Answer the user's question using ONLY the
retrieved notebook sources supplied to you.

Rules:

1. Do not invent facts.
2. Do not claim that a source was used unless it
   appears in the supplied context.
3. Prefer direct evidence from the sources.
4. If the sources do not contain enough information,
   explicitly say that the notebook does not contain
   sufficient evidence.
5. You may synthesize information across sources.
6. Clearly distinguish synthesis from direct source facts.
7. Keep answers useful and structured.
8. Preserve source IDs in the final answer when useful.
"""


def _now() -> str:

    return datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    ).isoformat()


def _gemini(
    prompt: str,
    *,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    model = (
        model
        or os.getenv(
            "SOUL_FORGE_GEMINI_MODEL",
            "gemini-2.5-flash",
        )
    )

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            KNOWLEDGE_SYSTEM_PROMPT
                            + "\n\n"
                            + prompt
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }

    response = requests.post(
        url,
        params={
            "key": api_key,
        },
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )

    return text, {
        "provider": "gemini",
        "model": model,
    }


def _openrouter(
    prompt: str,
    *,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:

    from app.core.openrouter_provider import (
        get_openrouter_provider,
    )

    provider = get_openrouter_provider()

    result = provider.generate(
        prompt=prompt,
        system=KNOWLEDGE_SYSTEM_PROMPT,
        task="KNOWLEDGE",
    )

    text = result.get("content", "")

    if not text:
        raise RuntimeError(
            "OpenRouterProvider returned empty content."
        )

    return text, {
        "provider": "openrouter",
        "model": result.get(
            "selected_model",
            result.get(
                "attempted_model",
                model,
            ),
        ),
        "requested_model": result.get(
            "requested_model"
        ),
        "requested_models": result.get(
            "requested_models"
        ),
        "attempted_model": result.get(
            "attempted_model"
        ),
        "attempt_number": result.get(
            "attempt_number"
        ),
    }


def _save_history(
    notebook_id: str,
    record: dict[str, Any],
) -> None:

    history_file = (
        HISTORY_DIR
        / f"{notebook_id}.jsonl"
    )

    with history_file.open(
        "a",
        encoding="utf-8",
    ) as handle:

        handle.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )


def load_history(
    notebook_id: str,
    *,
    limit: int = 100,
) -> list[dict[str, Any]]:

    history_file = (
        HISTORY_DIR
        / f"{notebook_id}.jsonl"
    )

    if not history_file.exists():
        return []

    records = []

    for line in history_file.read_text(
        encoding="utf-8"
    ).splitlines():

        try:
            records.append(
                json.loads(line)
            )
        except json.JSONDecodeError:
            continue

    return records[-limit:]


def ask_knowledge(
    question: str,
    notebook_id: str | None = None,
    *,
    top_k: int = 8,
    provider: str = "openrouter",
    model: str | None = None,
) -> dict[str, Any]:

    question = (
        question or ""
    ).strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    sources, context = (
        rag_engine.build_context(
            question,
            notebook_id,
            top_k=top_k,
        )
    )

    if not sources:

        answer = (
            "I could not find relevant information "
            "in the selected notebook resources."
        )

        record = {
            "timestamp": _now(),
            "question": question,
            "answer": answer,
            "notebook_id": notebook_id,
            "provider": "none",
            "model": None,
            "retrieval": {
                "strategy": "hybrid_rag",
                "chunks_retrieved": 0,
            },
            "sources": [],
        }

        if notebook_id:
            _save_history(
                notebook_id,
                record,
            )

        return record

    prompt = f"""
USER QUESTION:
{question}

RETRIEVED NOTEBOOK SOURCES:
{context}

Answer the question from these sources.

At the end include:

SOURCES USED:
- [RESOURCE_ID] resource name
- [RESOURCE_ID] resource name

Do not list a source unless it was actually
present in the retrieved context.
"""

    provider_name = (provider or "openrouter").strip().lower()

    if provider_name == "openrouter":

        answer, model_info = _openrouter(
            prompt,
            model=model,
        )

    elif provider_name == "ollama":

        raise RuntimeError(
            "Ollama is configured as an emergency/local fallback, "
            "but no Ollama Knowledge Agent implementation is currently "
            "wired into ask_knowledge()."
        )

    else:

        raise ValueError(
            f"Unsupported Knowledge provider: {provider_name}. "
            "Use 'openrouter'. Gemini is accessed through OpenRouter."
        )

    source_records = []

    for source in sources:

        source_records.append(
            {
                "resource_id": source[
                    "resource_id"
                ],
                "resource_name": source[
                    "resource_name"
                ],
                "chunk_id": source[
                    "chunk_id"
                ],
                "chunk_index": source[
                    "chunk_index"
                ],
                "score": source[
                    "score"
                ],
                "semantic_score": source[
                    "semantic_score"
                ],
                "keyword_score": source[
                    "keyword_score"
                ],
            }
        )

    record = {
        "timestamp": _now(),
        "question": question,
        "answer": answer,
        "notebook_id": notebook_id,
        "agent": "knowledge_agent",
        **model_info,
        "retrieval": {
            "strategy": "hybrid_rag",
            "top_k": top_k,
            "chunks_retrieved": len(
                sources
            ),
            "chunks_used": len(
                sources
            ),
        },
        "sources": source_records,
    }

    if notebook_id:
        _save_history(
            notebook_id,
            record,
        )

    return record
