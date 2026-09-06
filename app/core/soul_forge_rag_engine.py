from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "data" / "soul_forge" / "rag"

INDEX_FILE = DATA_ROOT / "index" / "chunks.json"
EMBEDDINGS_FILE = DATA_ROOT / "index" / "embeddings.npy"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_CHUNK_CACHE: list[dict[str, Any]] | None = None
_EMBEDDING_CACHE: np.ndarray | None = None
_MODEL = None


def _now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()


def _ensure() -> None:
    INDEX_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def _load_model():
    global _MODEL

    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)

    return _MODEL


def _load_chunks() -> list[dict[str, Any]]:
    global _CHUNK_CACHE

    _ensure()

    if not INDEX_FILE.exists():
        return []

    try:
        value = json.loads(
            INDEX_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(value, list):
            _CHUNK_CACHE = value
            return value

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return []


def _save_chunks(chunks: list[dict[str, Any]]) -> None:
    global _CHUNK_CACHE

    _ensure()

    tmp = INDEX_FILE.with_suffix(".tmp")

    tmp.write_text(
        json.dumps(
            chunks,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    tmp.replace(INDEX_FILE)

    _CHUNK_CACHE = chunks


def _load_embeddings() -> np.ndarray | None:
    global _EMBEDDING_CACHE

    if not EMBEDDINGS_FILE.exists():
        return None

    try:
        _EMBEDDING_CACHE = np.load(
            EMBEDDINGS_FILE
        )

        return _EMBEDDING_CACHE

    except Exception:
        return None


def _save_embeddings(
    embeddings: np.ndarray,
) -> None:

    global _EMBEDDING_CACHE

    EMBEDDINGS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.save(
        EMBEDDINGS_FILE,
        embeddings,
    )

    _EMBEDDING_CACHE = embeddings


def normalize_text(text: str) -> str:

    text = text.replace(
        "\x00",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def chunk_text(
    text: str,
    *,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[str]:

    text = normalize_text(text)

    if not text:
        return []

    if overlap >= chunk_size:
        overlap = max(
            0,
            chunk_size // 5,
        )

    chunks = []

    start = 0
    length = len(text)

    while start < length:

        end = min(
            start + chunk_size,
            length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = end - overlap

    return chunks


def _chunk_id(
    resource_id: str,
    chunk_index: int,
    text: str,
) -> str:

    raw = (
        f"{resource_id}:"
        f"{chunk_index}:"
        f"{text}"
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]

    return f"CH-{digest}"


def index_resource(
    resource_id: str,
    notebook_id: str,
    resource_name: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    metadata = metadata or {}

    chunks_text = chunk_text(content)

    all_chunks = _load_chunks()

    all_chunks = [
        item
        for item in all_chunks
        if item.get("resource_id") != resource_id
    ]

    new_chunks = []

    for index, text in enumerate(
        chunks_text
    ):

        new_chunks.append(
            {
                "chunk_id": _chunk_id(
                    resource_id,
                    index,
                    text,
                ),
                "resource_id": resource_id,
                "notebook_id": notebook_id,
                "resource_name": resource_name,
                "chunk_index": index,
                "text": text,
                "metadata": metadata,
                "created_at": _now(),
            }
        )

    all_chunks.extend(new_chunks)

    model = _load_model()

    embeddings = model.encode(
        [
            item["text"]
            for item in all_chunks
        ],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    _save_chunks(all_chunks)
    _save_embeddings(embeddings)

    return {
        "resource_id": resource_id,
        "chunks": len(new_chunks),
        "total_indexed_chunks": len(
            all_chunks
        ),
    }


def rebuild_index() -> dict[str, Any]:

    chunks = _load_chunks()

    if not chunks:
        return {
            "chunks": 0,
            "status": "empty",
        }

    model = _load_model()

    embeddings = model.encode(
        [
            item["text"]
            for item in chunks
        ],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    _save_embeddings(
        embeddings
    )

    return {
        "chunks": len(chunks),
        "status": "rebuilt",
    }


def _keyword_score(
    query: str,
    text: str,
) -> float:

    query_terms = {
        token.lower()
        for token in re.findall(
            r"\b\w+\b",
            query,
        )
        if len(token) > 2
    }

    if not query_terms:
        return 0.0

    text_terms = {
        token.lower()
        for token in re.findall(
            r"\b\w+\b",
            text,
        )
    }

    overlap = query_terms.intersection(
        text_terms
    )

    return len(overlap) / len(
        query_terms
    )


def search(
    query: str,
    notebook_id: str | None = None,
    *,
    top_k: int = 8,
) -> list[dict[str, Any]]:

    query = normalize_text(query)

    if not query:
        return []

    chunks = _load_chunks()

    if not chunks:
        return []

    if notebook_id:
        candidates = [
            (index, item)
            for index, item in enumerate(
                chunks
            )
            if item.get("notebook_id")
            == notebook_id
        ]
    else:
        candidates = list(
            enumerate(chunks)
        )

    if not candidates:
        return []

    embeddings = _load_embeddings()

    if (
        embeddings is None
        or len(embeddings) != len(chunks)
    ):
        rebuild_index()
        embeddings = _load_embeddings()

    model = _load_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

    results = []

    for original_index, item in candidates:

        semantic = float(
            np.dot(
                query_embedding,
                embeddings[original_index],
            )
        )

        keyword = _keyword_score(
            query,
            item["text"],
        )

        combined = (
            0.78 * semantic
            + 0.22 * keyword
        )

        results.append(
            {
                **item,
                "semantic_score": round(
                    semantic,
                    6,
                ),
                "keyword_score": round(
                    keyword,
                    6,
                ),
                "score": round(
                    combined,
                    6,
                ),
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:max(1, top_k)]


def build_context(
    query: str,
    notebook_id: str | None = None,
    *,
    top_k: int = 8,
) -> tuple[
    list[dict[str, Any]],
    str,
]:

    results = search(
        query,
        notebook_id,
        top_k=top_k,
    )

    context_parts = []

    for rank, result in enumerate(
        results,
        start=1,
    ):

        context_parts.append(
            "\n".join(
                [
                    f"[SOURCE {rank}]",
                    f"CHUNK_ID: {result['chunk_id']}",
                    f"RESOURCE_ID: {result['resource_id']}",
                    f"RESOURCE: {result['resource_name']}",
                    f"SCORE: {result['score']}",
                    f"CONTENT:",
                    result["text"],
                    "[END SOURCE]",
                ]
            )
        )

    return (
        results,
        "\n\n".join(
            context_parts
        ),
    )


def index_stats() -> dict[str, Any]:

    chunks = _load_chunks()

    resources = {
        item.get("resource_id")
        for item in chunks
    }

    notebooks = {
        item.get("notebook_id")
        for item in chunks
    }

    return {
        "chunks": len(chunks),
        "resources": len(
            resources
        ),
        "notebooks": len(
            notebooks
        ),
        "embedding_model": MODEL_NAME,
    }
