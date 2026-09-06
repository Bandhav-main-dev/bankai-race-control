from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from app.core import soul_forge_rag_engine as rag_engine


def _clean(text: str) -> str:

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


def _sha256(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def extract_text(
    path: str | Path,
) -> tuple[str, dict[str, Any]]:

    path = Path(path)

    suffix = path.suffix.lower()

    if suffix == ".pdf":

        from pypdf import PdfReader

        reader = PdfReader(
            str(path)
        )

        pages = []

        for number, page in enumerate(
            reader.pages,
            start=1,
        ):

            text = page.extract_text() or ""

            if text.strip():

                pages.append(
                    f"\n[PAGE {number}]\n{text}"
                )

        content = "\n".join(
            pages
        )

        metadata = {
            "format": "pdf",
            "pages": len(
                reader.pages
            ),
        }

    elif suffix == ".docx":

        from docx import Document

        document = Document(
            str(path)
        )

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        content = "\n".join(
            paragraphs
        )

        metadata = {
            "format": "docx",
            "paragraphs": len(
                paragraphs
            ),
        }

    elif suffix in {
        ".txt",
        ".md",
        ".markdown",
        ".py",
        ".json",
        ".csv",
    }:

        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        metadata = {
            "format": suffix.lstrip("."),
        }

    else:

        raise ValueError(
            f"Unsupported resource type: {suffix}"
        )

    content = _clean(
        content
    )

    metadata.update(
        {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
            "word_count": len(
                content.split()
            ),
            "character_count": len(
                content
            ),
        }
    )

    return content, metadata


def ingest_file(
    path: str | Path,
    resource_id: str,
    notebook_id: str,
    *,
    name: str | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    path = Path(path)

    content, metadata = extract_text(
        path
    )

    if extra_metadata:
        metadata.update(
            extra_metadata
        )

    result = rag_engine.index_resource(
        resource_id=resource_id,
        notebook_id=notebook_id,
        resource_name=(
            name or path.name
        ),
        content=content,
        metadata=metadata,
    )

    result.update(
        {
            "name": (
                name or path.name
            ),
            "metadata": metadata,
            "content": content,
        }
    )

    return result


def ingest_text(
    resource_id: str,
    notebook_id: str,
    name: str,
    content: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    metadata = metadata or {}

    metadata.update(
        {
            "format": "text",
            "word_count": len(
                content.split()
            ),
            "character_count": len(
                content
            ),
        }
    )

    return rag_engine.index_resource(
        resource_id=resource_id,
        notebook_id=notebook_id,
        resource_name=name,
        content=content,
        metadata=metadata,
    )
