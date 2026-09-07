# =============================================================================
# SOUL FORGE — SF-004 KNOWLEDGE PANEL
# =============================================================================
"""
SF-004 Knowledge UI.

This module is intentionally isolated from the main Streamlit UI.

Responsibilities:
    - Notebook selection
    - Knowledge resource ingestion
    - RAG statistics
    - Semantic/keyword retrieval
    - Gemini/OpenRouter knowledge answering
    - Retrieval source display
    - Knowledge history
"""

from __future__ import annotations

from pathlib import Path
import inspect
import json
import tempfile
from typing import Any

import streamlit as st


# -----------------------------------------------------------------------------
# Project / backend imports
# -----------------------------------------------------------------------------

try:
    from app.services.soul_forge_knowledge_service import (
        ask_knowledge,
        build_knowledge_context,
        get_knowledge_history,
        get_rag_stats,
        search_knowledge,
    )
except Exception as exc:
    ask_knowledge = None
    build_knowledge_context = None
    get_knowledge_history = None
    get_rag_stats = None
    search_knowledge = None
    _KNOWLEDGE_SERVICE_ERROR = str(exc)


try:
    from app.services.soul_forge_ingestion import ingest_file
except Exception as exc:
    ingest_file = None
    _INGESTION_ERROR = str(exc)


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

DEFAULT_NOTEBOOK = "soul_forge"

SUPPORTED_EXTENSIONS = [
    "pdf",
    "docx",
    "txt",
    "md",
    "csv",
    "json",
    "py",
]


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def _safe_call(function, *args, **kwargs):
    """Call a backend function without allowing UI failure."""
    if function is None:
        return None

    try:
        return function(*args, **kwargs)
    except Exception:
        return None


def _normalise_result_list(value):
    """Convert common backend result containers to a list."""
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, dict):
        for key in ("results", "sources", "resources", "items", "matches"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return candidate

        return [value]

    return []


def _result_text(item: Any) -> str:
    if isinstance(item, str):
        return item

    if not isinstance(item, dict):
        return str(item)

    for key in (
        "text",
        "content",
        "chunk_text",
        "excerpt",
        "snippet",
        "answer",
    ):
        value = item.get(key)

        if value:
            return str(value)

    return ""


def _result_name(item: Any) -> str:
    if isinstance(item, str):
        return item

    if not isinstance(item, dict):
        return "Knowledge source"

    for key in (
        "name",
        "resource_name",
        "filename",
        "file_name",
        "resource_id",
        "source",
    ):
        value = item.get(key)

        if value:
            return str(value)

    return "Knowledge source"


def _result_score(item: Any):
    if not isinstance(item, dict):
        return None

    for key in (
        "score",
        "hybrid_score",
        "semantic_score",
        "similarity",
    ):
        value = item.get(key)

        if value is not None:
            try:
                return float(value)
            except Exception:
                return value

    return None


# -----------------------------------------------------------------------------
# Ingestion compatibility adapter
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# Stats
# -----------------------------------------------------------------------------

def _get_stats():
    if get_rag_stats is None:
        return {}

    try:
        value = get_rag_stats()

        if isinstance(value, dict):
            return value

        return {}

    except Exception:
        return {}


# -----------------------------------------------------------------------------
# Main renderer
# -----------------------------------------------------------------------------

def render_soul_forge_knowledge_panel():
    """
    Render the complete SF-004 Knowledge workspace.
    """

    st.markdown(
        """
        <style>
        .sf004-hero {
            padding: 1.2rem 1.4rem;
            border-radius: 16px;
            border: 1px solid rgba(180, 18, 38, 0.45);
            background:
                linear-gradient(
                    135deg,
                    rgba(177,18,38,0.16),
                    rgba(0,0,0,0.72)
                );
            margin-bottom: 1rem;
        }

        .sf004-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        }

        .sf004-subtitle {
            opacity: 0.72;
            font-size: 0.92rem;
        }

        .sf004-chip {
            display: inline-block;
            padding: 0.25rem 0.55rem;
            margin-right: 0.35rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.12);
            font-size: 0.75rem;
        }
        </style>

        <div class="sf004-hero">
            <div class="sf004-title">
                📚 SOUL FORGE KNOWLEDGE CORE
            </div>
            <div class="sf004-subtitle">
                SF-004 • Retrieval-Augmented Knowledge Interface
            </div>
            <br>
            <span class="sf004-chip">RAG</span>
            <span class="sf004-chip">Gemini</span>
            <span class="sf004-chip">Semantic Search</span>
            <span class="sf004-chip">Knowledge Memory</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # Session state
    # -------------------------------------------------------------------------

    st.session_state.setdefault(
        "sf004_notebook_id",
        DEFAULT_NOTEBOOK,
    )

    st.session_state.setdefault(
        "sf004_question",
        "",
    )

    st.session_state.setdefault(
        "sf004_last_answer",
        None,
    )

    st.session_state.setdefault(
        "sf004_last_sources",
        [],
    )

    st.session_state.setdefault(
        "sf004_search_results",
        [],
    )

    # -------------------------------------------------------------------------
    # Notebook / stats
    # -------------------------------------------------------------------------

    top_left, top_right = st.columns([2.2, 1])

    with top_left:
        notebook_id = st.text_input(
            "Knowledge Notebook",
            value=st.session_state.sf004_notebook_id,
            key="sf004_notebook_input",
            help="RAG notebook namespace used for SF-004 knowledge.",
        )

        if notebook_id.strip():
            st.session_state.sf004_notebook_id = notebook_id.strip()

    stats = _get_stats()

    with top_right:
        st.metric(
            "Indexed Chunks",
            stats.get(
                "chunks",
                stats.get(
                    "chunk_count",
                    "—",
                ),
            ),
        )

    # -------------------------------------------------------------------------
    # Upload / ingestion
    # -------------------------------------------------------------------------

    st.markdown("### 📥 Knowledge Ingestion")

    uploaded_files = st.file_uploader(
        "Add knowledge resources",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
        key="sf004_knowledge_uploader",
        help=(
            "Supported: PDF, DOCX, TXT, Markdown, CSV, JSON and Python."
        ),
    )

    ingest_col, refresh_col = st.columns([2, 1])

    with ingest_col:
        ingest_clicked = st.button(
            "⚡ INGEST INTO SOUL FORGE",
            key="sf004_ingest_button",
            use_container_width=True,
        )

    with refresh_col:
        refresh_clicked = st.button(
            "↻ Refresh Index",
            key="sf004_refresh_button",
            use_container_width=True,
        )

    if ingest_clicked:

        if not uploaded_files:
            st.warning(
                "Select at least one knowledge resource first."
            )
        else:

            success_count = 0

            for uploaded in uploaded_files:

                with st.spinner(
                    f"Ingesting {uploaded.name}..."
                ):

                    try:
                        result = _ingest_uploaded_file(
                            uploaded,
                            st.session_state.sf004_notebook_id,
                        )

                        success_count += 1

                        st.success(
                            f"✓ {uploaded.name} indexed"
                        )

                        if isinstance(result, dict):
                            with st.expander(
                                f"Ingestion details — {uploaded.name}",
                                expanded=False,
                            ):
                                st.json(result)

                    except Exception as exc:
                        st.error(
                            f"✗ Failed to ingest {uploaded.name}: {exc}"
                        )

            if success_count:
                st.cache_data.clear()
                st.rerun()

    if refresh_clicked:
        st.rerun()

    # -------------------------------------------------------------------------
    # Current index metrics
    # -------------------------------------------------------------------------

    stats = _get_stats()

    metric_a, metric_b, metric_c, metric_d = st.columns(4)

    with metric_a:
        st.metric(
            "Chunks",
            stats.get(
                "chunks",
                stats.get(
                    "chunk_count",
                    "—",
                ),
            ),
        )

    with metric_b:
        st.metric(
            "Resources",
            stats.get(
                "resources",
                stats.get(
                    "resource_count",
                    "—",
                ),
            ),
        )

    with metric_c:
        st.metric(
            "Notebooks",
            stats.get(
                "notebooks",
                stats.get(
                    "notebook_count",
                    "—",
                ),
            ),
        )

    with metric_d:
        st.metric(
            "Engine",
            "ONLINE" if get_rag_stats else "OFFLINE",
        )

    st.divider()

    # -------------------------------------------------------------------------
    # Ask Knowledge
    # -------------------------------------------------------------------------

    st.markdown("### 🧠 Ask Soul Forge")

    question = st.text_area(
        "Knowledge question",
        value=st.session_state.sf004_question,
        key="sf004_question_input",
        height=120,
        placeholder=(
            "Ask something about the knowledge stored in Soul Forge..."
        ),
    )

    ask_col, search_col = st.columns(2)

    with ask_col:
        ask_clicked = st.button(
            "⚔️ ASK KNOWLEDGE CORE",
            key="sf004_ask_button",
            type="primary",
            use_container_width=True,
        )

    with search_col:
        search_clicked = st.button(
            "🔎 SEARCH RAG",
            key="sf004_search_button",
            use_container_width=True,
        )

    # -------------------------------------------------------------------------
    # Retrieval-only search
    # -------------------------------------------------------------------------

    if search_clicked:

        if not question.strip():
            st.warning(
                "Enter a question or search query first."
            )

        elif search_knowledge is None:
            st.error(
                "SF-004 search service is unavailable."
            )

        else:

            with st.spinner("Searching Soul Forge memory..."):

                try:
                    results = search_knowledge(
                        question.strip(),
                        notebook_id=st.session_state.sf004_notebook_id,
                    )

                    results = _normalise_result_list(results)

                    st.session_state.sf004_search_results = results

                except Exception as exc:
                    st.error(
                        f"Knowledge search failed: {exc}"
                    )
                    st.session_state.sf004_search_results = []

    # -------------------------------------------------------------------------
    # Gemini / Knowledge Agent answer
    # -------------------------------------------------------------------------

    if ask_clicked:

        if not question.strip():
            st.warning(
                "Enter a question first."
            )

        elif ask_knowledge is None:
            st.error(
                "SF-004 Knowledge Agent is unavailable."
            )

        else:

            st.session_state.sf004_question = question.strip()

            with st.spinner(
                "Soul Forge is retrieving knowledge and reasoning..."
            ):

                try:
                    result = ask_knowledge(
                        question.strip(),
                        notebook_id=st.session_state.sf004_notebook_id,
                        provider="gemini",
                    )

                    st.session_state.sf004_last_answer = result

                    if isinstance(result, dict):
                        st.session_state.sf004_last_sources = (
                            _normalise_result_list(
                                result.get(
                                    "sources",
                                    result.get(
                                        "retrieval",
                                        [],
                                    ),
                                )
                            )
                        )
                    else:
                        st.session_state.sf004_last_sources = []

                except Exception as exc:

                    st.error(
                        f"Knowledge Agent failed: {exc}"
                    )

    # -------------------------------------------------------------------------
    # Search results
    # -------------------------------------------------------------------------

    search_results = st.session_state.sf004_search_results

    if search_results:

        st.markdown("### 🔎 Retrieval Results")

        for index, item in enumerate(search_results, start=1):

            name = _result_name(item)
            score = _result_score(item)
            text = _result_text(item)

            score_text = (
                f" • score={score:.4f}"
                if isinstance(score, float)
                else ""
            )

            with st.expander(
                f"{index}. {name}{score_text}",
                expanded=index == 1,
            ):

                if text:
                    st.write(text)

                if isinstance(item, dict):

                    metadata = {
                        key: value
                        for key, value in item.items()
                        if key not in (
                            "text",
                            "content",
                            "chunk_text",
                        )
                    }

                    if metadata:
                        st.caption("Retrieval metadata")

                        try:
                            st.json(metadata)
                        except Exception:
                            st.write(metadata)

    # -------------------------------------------------------------------------
    # Answer
    # -------------------------------------------------------------------------

    answer = st.session_state.sf004_last_answer

    if answer:

        st.markdown("### ⚔️ Knowledge Core Answer")

        if isinstance(answer, dict):

            answer_text = (
                answer.get("answer")
                or answer.get("text")
                or answer.get("response")
                or answer.get("content")
            )

            if answer_text:
                st.markdown(answer_text)
            else:
                st.json(answer)

            provider = answer.get("provider")
            model = answer.get("model")

            if provider or model:

                metadata_parts = []

                if provider:
                    metadata_parts.append(
                        f"Provider: `{provider}`"
                    )

                if model:
                    metadata_parts.append(
                        f"Model: `{model}`"
                    )

                st.caption(
                    " • ".join(metadata_parts)
                )

        else:
            st.markdown(str(answer))

    # -------------------------------------------------------------------------
    # Sources
    # -------------------------------------------------------------------------

    sources = st.session_state.sf004_last_sources

    if sources:

        st.markdown("### 📖 Retrieved Sources")

        for index, item in enumerate(
            sources,
            start=1,
        ):

            name = _result_name(item)
            score = _result_score(item)
            text = _result_text(item)

            title = f"{index}. {name}"

            if isinstance(score, float):
                title += f" • {score:.4f}"

            with st.expander(
                title,
                expanded=False,
            ):

                if text:
                    st.write(text)

                if isinstance(item, dict):
                    st.json(item)

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------

    st.divider()

    with st.expander(
        "🧾 Knowledge History",
        expanded=False,
    ):

        if get_knowledge_history is None:
            st.info(
                "Knowledge history service is unavailable."
            )

        else:

            try:

                history = get_knowledge_history(
                    st.session_state.sf004_notebook_id,
                    limit=20,
                )

                history = _normalise_result_list(history)

                if not history:
                    st.info(
                        "No knowledge queries recorded yet."
                    )

                else:

                    for index, record in enumerate(
                        reversed(history),
                        start=1,
                    ):

                        if isinstance(record, dict):

                            question_text = (
                                record.get("question")
                                or record.get("query")
                                or "Knowledge query"
                            )

                            with st.expander(
                                f"{index}. {question_text}",
                                expanded=False,
                            ):
                                st.json(record)

                        else:
                            st.write(record)

            except Exception as exc:
                st.warning(
                    f"History unavailable: {exc}"
                )

    # -------------------------------------------------------------------------
    # Backend diagnostics
    # -------------------------------------------------------------------------

    with st.expander(
        "🛠 SF-004 Backend Diagnostics",
        expanded=False,
    ):

        if get_rag_stats is not None:
            st.success(
                "RAG statistics service: ONLINE"
            )
        else:
            st.error(
                "RAG statistics service: OFFLINE"
            )

        if search_knowledge is not None:
            st.success(
                "Semantic search service: ONLINE"
            )
        else:
            st.error(
                "Semantic search service: OFFLINE"
            )

        if ask_knowledge is not None:
            st.success(
                "Knowledge Agent: ONLINE"
            )
        else:
            st.error(
                "Knowledge Agent: OFFLINE"
            )

        if ingest_file is not None:
            st.success(
                "Ingestion service: ONLINE"
            )
        else:
            st.error(
                "Ingestion service: OFFLINE"
            )

def _ingest_uploaded_file(
    uploaded_file,
    notebook_id="soul_forge",
):
    """
    SF-004 Streamlit upload adapter.

    The real ingestion service expects:
        ingest_file(path=...)

    Streamlit UploadedFile objects are therefore written to a temporary
    filesystem path before being passed to the ingestion service.
    """

    import inspect
    import tempfile
    from pathlib import Path

    from app.services.soul_forge_ingestion import ingest_file

    if uploaded_file is None:
        raise ValueError(
            "No uploaded file was supplied."
        )

    filename = getattr(
        uploaded_file,
        "name",
        "uploaded_resource",
    )

    suffix = Path(filename).suffix

    # -------------------------------------------------------------------------
    # Materialize Streamlit upload to a real filesystem path.
    # -------------------------------------------------------------------------

    file_bytes = uploaded_file.getvalue()

    temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        prefix="sf004_",
        delete=False,
    )

    try:

        temp_file.write(file_bytes)
        temp_file.flush()
        temp_file.close()

        temp_path = temp_file.name

        # ---------------------------------------------------------------------
        # Inspect actual ingestion signature.
        # ---------------------------------------------------------------------

        signature = inspect.signature(
            ingest_file
        )

        parameters = signature.parameters

        kwargs = {}

        if "notebook_id" in parameters:
            kwargs["notebook_id"] = notebook_id

        if "resource_id" in parameters:
            kwargs["resource_id"] = (
                f"{notebook_id}:{filename}"
            )

        if "name" in parameters:
            kwargs["name"] = filename

        if "filename" in parameters:
            kwargs["filename"] = filename

        if "file_name" in parameters:
            kwargs["file_name"] = filename

        # ---------------------------------------------------------------------
        # The actual service requires path.
        # ---------------------------------------------------------------------

        if "path" not in parameters:
            raise RuntimeError(
                "SF-004 ingest_file() no longer exposes "
                "the required path parameter."
            )

        kwargs["path"] = temp_path

        # ---------------------------------------------------------------------
        # Call the real ingestion service.
        # ---------------------------------------------------------------------

        return ingest_file(
            **kwargs
        )

    finally:

        # ---------------------------------------------------------------------
        # Remove temporary file after ingestion has consumed it.
        # ---------------------------------------------------------------------

        try:
            Path(
                temp_file.name
            ).unlink(
                missing_ok=True
            )
        except Exception:
            pass

