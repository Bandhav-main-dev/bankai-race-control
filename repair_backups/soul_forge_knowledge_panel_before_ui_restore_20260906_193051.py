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

def _ingest_uploaded_file(uploaded_file, notebook_id: str):
    """
    Safely adapt to the actual ingest_file() signature.

    The SF-004 ingestion module has evolved during development, so this
    adapter inspects its signature rather than assuming one fixed API.
    """

    if ingest_file is None:
        raise RuntimeError(
            "SF-004 ingestion service is unavailable."
        )

    suffix = Path(uploaded_file.name).suffix.lower()

    temp_dir = (
        Path(tempfile.gettempdir())
        / "soul_forge_sf004_uploads"
    )

    temp_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = temp_dir / uploaded_file.name

    temp_path.write_bytes(
        uploaded_file.getvalue()
    )

    signature = inspect.signature(ingest_file)

    parameters = list(signature.parameters.values())

    kwargs = {}
    args = []

    path_parameter = None
    notebook_parameter = None
    name_parameter = None

    for parameter in parameters:

        name = parameter.name.lower()

        if any(
            token in name
            for token in (
                "path",
                "file_path",
                "filepath",
            )
        ):
            path_parameter = parameter

        elif any(
            token in name
            for token in (
                "notebook",
                "notebook_id",
            )
        ):
            notebook_parameter = parameter

        elif name in (
            "name",
            "filename",
            "file_name",
            "resource_name",
        ):
            name_parameter = parameter

    # Prefer keyword arguments when possible.
    if path_parameter is not None:
        kwargs[path_parameter.name] = str(temp_path)

    if notebook_parameter is not None:
        kwargs[notebook_parameter.name] = notebook_id

    if name_parameter is not None:
        kwargs[name_parameter.name] = uploaded_file.name

    try:
        return ingest_file(**kwargs)
    except TypeError:

        # Compatibility fallback 1:
        try:
            return ingest_file(
                str(temp_path),
                notebook_id,
            )
        except TypeError:
            pass

        # Compatibility fallback 2:
        try:
            return ingest_file(
                temp_path,
                notebook_id,
            )
        except TypeError:
            pass

        # Compatibility fallback 3:
        try:
            return ingest_file(
                str(temp_path),
            )
        except TypeError:
            pass

        # Re-raise with useful context.
        raise


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
    SF-004 Knowledge Workspace.

    This is the public renderer consumed by:
        app.ui.bankai_race_control.render_knowledge()

    The function intentionally depends on the existing SF-004 service layer
    instead of implementing RAG logic inside the UI.
    """

    import inspect

    import streamlit as st

    # -------------------------------------------------------------------------
    # SF-004 service imports
    # -------------------------------------------------------------------------

    try:
        from app.services.soul_forge_knowledge_service import (
            ask_knowledge,
            build_knowledge_context,
            get_knowledge_history,
            get_rag_stats,
            search_knowledge,
        )
    except Exception as exc:
        st.error("SF-004 Knowledge Service could not be loaded.")
        st.exception(exc)
        return

    # -------------------------------------------------------------------------
    # Optional ingestion service
    # -------------------------------------------------------------------------

    try:
        from app.services.soul_forge_ingestion import ingest_file
    except Exception:
        ingest_file = None

    # -------------------------------------------------------------------------
    # Page header
    # -------------------------------------------------------------------------

    st.markdown(
        """
        <div style="
            padding: 18px 22px;
            margin-bottom: 18px;
            border-radius: 14px;
            background:
                linear-gradient(
                    135deg,
                    rgba(177,18,38,0.20),
                    rgba(20,70,140,0.16),
                    rgba(0,0,0,0.50)
                );
            border: 1px solid rgba(255,255,255,0.10);
        ">
            <div style="
                font-size: 28px;
                font-weight: 800;
                letter-spacing: 1px;
            ">
                📚 SOUL FORGE — KNOWLEDGE
            </div>

            <div style="
                margin-top: 6px;
                opacity: 0.78;
                font-size: 14px;
            ">
                SF-004 Retrieval-Augmented Knowledge Command Center
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # Notebook
    # -------------------------------------------------------------------------

    notebook_id = st.text_input(
        "Knowledge Notebook",
        value="soul_forge",
        help="Logical SF-004 knowledge namespace.",
    ).strip() or "soul_forge"

    # -------------------------------------------------------------------------
    # RAG statistics
    # -------------------------------------------------------------------------

    st.subheader("⚙️ Knowledge Engine")

    try:
        stats = get_rag_stats()
    except Exception as exc:
        stats = {}
        st.warning(
            f"RAG statistics unavailable: {exc}"
        )

    if isinstance(stats, dict):

        stat_items = []

        preferred_keys = [
            "chunks",
            "documents",
            "resources",
            "embeddings",
            "index_size",
            "indexed_chunks",
        ]

        for key in preferred_keys:
            if key in stats:
                stat_items.append(
                    (key.replace("_", " ").title(), stats[key])
                )

        if stat_items:

            columns = st.columns(
                min(len(stat_items), 4)
            )

            for column, (label, value) in zip(
                columns,
                stat_items
            ):
                column.metric(
                    label,
                    str(value)
                )

        with st.expander(
            "🔎 Raw RAG Diagnostics",
            expanded=False,
        ):
            st.json(stats)

    # -------------------------------------------------------------------------
    # Resource ingestion
    # -------------------------------------------------------------------------

    st.subheader("📥 Add Knowledge")

    uploaded_file = st.file_uploader(
        "Upload a knowledge resource",
        type=[
            "pdf",
            "docx",
            "txt",
            "md",
            "csv",
            "json",
            "py",
        ],
        help=(
            "Supported SF-004 resource formats: "
            "PDF, DOCX, TXT, Markdown, CSV, JSON and Python."
        ),
    )

    if uploaded_file is not None:

        st.caption(
            f"Selected: {uploaded_file.name} "
            f"({uploaded_file.size:,} bytes)"
        )

        if st.button(
            "⚡ INGEST INTO SOUL FORGE",
            type="primary",
            use_container_width=True,
        ):

            if ingest_file is None:
                st.error(
                    "SF-004 ingestion service is unavailable."
                )

            else:

                try:
                    file_bytes = uploaded_file.getvalue()

                    # ---------------------------------------------------------
                    # Adapt to the installed ingestion function signature.
                    # ---------------------------------------------------------

                    signature = inspect.signature(
                        ingest_file
                    )

                    parameters = signature.parameters

                    kwargs = {}

                    if "notebook_id" in parameters:
                        kwargs["notebook_id"] = notebook_id

                    if "resource_id" in parameters:
                        kwargs["resource_id"] = (
                            f"{notebook_id}:{uploaded_file.name}"
                        )

                    if "name" in parameters:
                        kwargs["name"] = uploaded_file.name

                    if "filename" in parameters:
                        kwargs["filename"] = uploaded_file.name

                    if "file_name" in parameters:
                        kwargs["file_name"] = uploaded_file.name

                    if "content" in parameters:
                        try:
                            kwargs["content"] = (
                                file_bytes.decode("utf-8")
                            )
                        except UnicodeDecodeError:
                            kwargs["content"] = file_bytes

                    if "data" in parameters:
                        kwargs["data"] = file_bytes

                    if "file_bytes" in parameters:
                        kwargs["file_bytes"] = file_bytes

                    if "uploaded_file" in parameters:
                        kwargs["uploaded_file"] = uploaded_file

                    if "file" in parameters:
                        kwargs["file"] = uploaded_file

                    # ---------------------------------------------------------
                    # Prefer keyword-compatible invocation.
                    # ---------------------------------------------------------

                    result = ingest_file(
                        **kwargs
                    )

                    st.success(
                        f"✅ {uploaded_file.name} ingested successfully."
                    )

                    if result is not None:
                        with st.expander(
                            "Ingestion Result",
                            expanded=True,
                        ):
                            if isinstance(result, dict):
                                st.json(result)
                            else:
                                st.write(result)

                    st.cache_data.clear()

                except TypeError as exc:

                    st.error(
                        "The installed SF-004 ingestion API has a "
                        "different signature."
                    )

                    st.code(
                        str(
                            inspect.signature(
                                ingest_file
                            )
                        )
                    )

                    st.exception(exc)

                except Exception as exc:

                    st.error(
                        f"Knowledge ingestion failed: {exc}"
                    )
                    st.exception(exc)

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    st.subheader("🔍 Knowledge Search")

    search_query = st.text_input(
        "Search the knowledge base",
        placeholder=(
            "Example: Einstein relativity, F1 race strategy, "
            "Soul Forge architecture..."
        ),
        key="sf004_search_query",
    ).strip()

    search_col1, search_col2 = st.columns(
        [4, 1]
    )

    with search_col2:

        search_clicked = st.button(
            "SEARCH",
            use_container_width=True,
        )

    if search_clicked and search_query:

        try:

            results = search_knowledge(
                search_query,
                notebook_id=notebook_id,
            )

            st.session_state[
                "sf004_last_search_results"
            ] = results

        except Exception as exc:

            st.error(
                f"Knowledge search failed: {exc}"
            )

    # -------------------------------------------------------------------------
    # Display search results
    # -------------------------------------------------------------------------

    search_results = st.session_state.get(
        "sf004_last_search_results"
    )

    if search_results:

        st.markdown("### Search Results")

        if isinstance(search_results, (list, tuple)):

            for index, result in enumerate(
                search_results,
                start=1,
            ):

                with st.expander(
                    f"Result {index}",
                    expanded=index <= 3,
                ):

                    if isinstance(result, dict):
                        st.json(result)
                    else:
                        st.write(result)

        else:

            st.write(search_results)

    # -------------------------------------------------------------------------
    # Ask Knowledge
    # -------------------------------------------------------------------------

    st.subheader("🧠 Ask Soul Forge")

    question = st.text_area(
        "Question",
        placeholder=(
            "Ask a question using the indexed knowledge..."
        ),
        height=110,
        key="sf004_question",
    ).strip()

    ask_col1, ask_col2 = st.columns(
        [4, 1]
    )

    with ask_col2:

        ask_clicked = st.button(
            "ASK",
            type="primary",
            use_container_width=True,
        )

    if ask_clicked:

        if not question:

            st.warning(
                "Enter a question first."
            )

        else:

            try:

                with st.spinner(
                    "SOUL FORGE is researching..."
                ):

                    answer = ask_knowledge(
                        question,
                        notebook_id=notebook_id,
                        top_k=8,
                        provider="gemini",
                    )

                st.session_state[
                    "sf004_last_answer"
                ] = answer

            except TypeError:

                # Compatibility fallback for an older API.
                try:

                    answer = ask_knowledge(
                        question,
                        notebook_id=notebook_id,
                    )

                    st.session_state[
                        "sf004_last_answer"
                    ] = answer

                except Exception as exc:

                    st.error(
                        f"Knowledge research failed: {exc}"
                    )
                    st.exception(exc)

            except Exception as exc:

                st.error(
                    f"Knowledge research failed: {exc}"
                )
                st.exception(exc)

    # -------------------------------------------------------------------------
    # Display answer
    # -------------------------------------------------------------------------

    answer = st.session_state.get(
        "sf004_last_answer"
    )

    if answer is not None:

        st.markdown("### 🧾 Answer")

        if isinstance(answer, dict):

            answer_text = (
                answer.get("answer")
                or answer.get("response")
                or answer.get("text")
            )

            if answer_text:
                st.markdown(
                    answer_text
                )
            else:
                st.json(answer)

            sources = (
                answer.get("sources")
                or answer.get("citations")
                or answer.get("references")
            )

            if sources:

                st.markdown("### 📎 Sources")

                if isinstance(
                    sources,
                    (list, tuple),
                ):

                    for source in sources:
                        st.write(source)

                else:

                    st.write(sources)

        else:

            st.markdown(
                str(answer)
            )

    # -------------------------------------------------------------------------
    # Context builder diagnostics
    # -------------------------------------------------------------------------

    with st.expander(
        "🧩 Retrieval Context",
        expanded=False,
    ):

        context_query = st.text_input(
            "Context query",
            key="sf004_context_query",
        ).strip()

        if st.button(
            "BUILD CONTEXT",
            key="sf004_build_context",
        ):

            if not context_query:

                st.warning(
                    "Enter a context query."
                )

            else:

                try:

                    resources, context = (
                        build_knowledge_context(
                            context_query,
                            notebook_id=notebook_id,
                            max_resources=10,
                        )
                    )

                    st.markdown(
                        "#### Retrieved Resources"
                    )

                    st.write(
                        resources
                    )

                    st.markdown(
                        "#### Built Context"
                    )

                    st.text_area(
                        "Context",
                        value=str(context),
                        height=300,
                    )

                except Exception as exc:

                    st.error(
                        f"Context construction failed: {exc}"
                    )
                    st.exception(exc)

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------

    with st.expander(
        "🕘 Knowledge History",
        expanded=False,
    ):

        try:

            history = get_knowledge_history(
                notebook_id,
                limit=50,
            )

            if history:

                for item in history:

                    if isinstance(item, dict):

                        st.json(item)

                    else:

                        st.write(item)

            else:

                st.info(
                    "No Knowledge history recorded yet."
                )

        except Exception as exc:

            st.warning(
                f"Knowledge history unavailable: {exc}"
            )

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------

    st.caption(
        "SF-004 Knowledge UI V2 • "
        "RAG retrieval • source-aware research • "
        "Soul Forge"
    )
