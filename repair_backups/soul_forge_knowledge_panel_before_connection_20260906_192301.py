from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from app.core import soul_forge_rag_engine as rag_engine
from app.services import soul_forge_ingestion as ingestion
from app.services import soul_forge_knowledge_service as knowledge_service
from app.agents import soul_forge_knowledge_agent as knowledge_agent


PROJECT_ROOT = Path("/content/BANKAI-RACE-CONTROL")

RAG_ROOT = PROJECT_ROOT / "data" / "soul_forge" / "rag"
INDEX_ROOT = RAG_ROOT / "index"
CHUNKS_FILE = INDEX_ROOT / "chunks.json"
HISTORY_ROOT = RAG_ROOT / "history"


def _safe_json(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, dict):
        return {
            str(k): _safe_json(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_safe_json(v) for v in value]

    try:
        return str(value)
    except Exception:
        return repr(value)


def _call_ingest_file(
    uploaded_file,
    notebook_id: str,
) -> dict[str, Any]:
    """
    Compatibility wrapper around the validated SF-004 ingestion API.

    It inspects the installed function signature so this UI remains
    compatible with the backend already installed in the Colab runtime.
    """

    suffix = Path(uploaded_file.name).suffix.lower()

    content = uploaded_file.getvalue()

    digest = hashlib.sha256(content).hexdigest()

    resource_id = (
        "sf_"
        + digest[:16]
        + "_"
        + datetime.now().strftime("%Y%m%d%H%M%S")
    )

    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False,
    ) as tmp:

        tmp.write(content)
        tmp_path = tmp.name

    try:
        fn = ingestion.ingest_file
        sig = inspect.signature(fn)

        kwargs = {}

        for name, param in sig.parameters.items():

            if name in {"file_path", "path", "source_path"}:
                kwargs[name] = tmp_path

            elif name in {"resource_id", "id"}:
                kwargs[name] = resource_id

            elif name in {"notebook_id", "notebook"}:
                kwargs[name] = notebook_id

            elif name in {"name", "resource_name", "filename"}:
                kwargs[name] = uploaded_file.name

            elif name in {"metadata", "meta"}:
                kwargs[name] = {
                    "original_filename": uploaded_file.name,
                    "content_type": uploaded_file.type,
                    "size_bytes": len(content),
                    "sha256": digest,
                    "source": "SOUL_FORGE_KNOWLEDGE_UI",
                }

        result = fn(**kwargs)

        if isinstance(result, dict):
            return result

        return {
            "result": str(result),
            "resource_id": resource_id,
            "notebook_id": notebook_id,
            "name": uploaded_file.name,
        }

    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


def _load_resource_inventory() -> list[dict[str, Any]]:
    """
    Build a lightweight resource inventory from the persistent RAG chunks.

    This does not modify the RAG engine.
    """

    if not CHUNKS_FILE.exists():
        return []

    try:
        raw = json.loads(
            CHUNKS_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return []

    if not isinstance(raw, list):
        return []

    resources: dict[str, dict[str, Any]] = {}

    for chunk in raw:

        if not isinstance(chunk, dict):
            continue

        resource_id = str(
            chunk.get("resource_id")
            or chunk.get("id")
            or "unknown"
        )

        item = resources.setdefault(
            resource_id,
            {
                "resource_id": resource_id,
                "name": chunk.get("name")
                or chunk.get("resource_name")
                or resource_id,
                "notebook_id": chunk.get("notebook_id")
                or "default",
                "chunks": 0,
                "characters": 0,
            },
        )

        item["chunks"] += 1

        text = str(
            chunk.get("text")
            or chunk.get("content")
            or ""
        )

        item["characters"] += len(text)

    return list(resources.values())


def _history(notebook_id: str) -> list[dict[str, Any]]:
    try:
        return knowledge_agent.load_history(
            notebook_id,
            limit=100,
        )
    except Exception:
        try:
            return knowledge_service.get_knowledge_history(
                notebook_id,
                limit=100,
            )
        except Exception:
            return []


def _render_source(source: dict[str, Any], index: int) -> None:

    resource_id = (
        source.get("resource_id")
        or source.get("id")
        or "unknown"
    )

    name = (
        source.get("name")
        or source.get("resource_name")
        or resource_id
    )

    score = source.get(
        "score",
        source.get(
            "hybrid_score",
            source.get("semantic_score", 0),
        ),
    )

    with st.expander(
        f"#{index}  {name}  ·  score {float(score):.3f}",
        expanded=(index == 1),
    ):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.caption("RESOURCE")
            st.write(str(resource_id))

        with c2:
            st.caption("SEMANTIC")
            st.write(
                str(
                    source.get(
                        "semantic_score",
                        "—",
                    )
                )
            )

        with c3:
            st.caption("KEYWORD")
            st.write(
                str(
                    source.get(
                        "keyword_score",
                        "—",
                    )
                )
            )

        text = (
            source.get("text")
            or source.get("content")
            or source.get("chunk")
            or ""
        )

        if text:
            st.markdown("**Retrieved content**")
            st.code(
                str(text)[:8000],
                language="text",
            )


def render_knowledge_panel() -> None:

    st.markdown(
        """
        <div class="bankai-header">
            <div class="header-kicker">
                SOUL FORGE // SF-004 KNOWLEDGE ENGINE
            </div>
            <div class="header-title">
                🧠 SOUL FORGE KNOWLEDGE
            </div>
            <div class="header-subtitle">
                NOTEBOOKLM-STYLE SOURCE-GROUNDED RAG COMMAND CENTER
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # NOTEBOOK
    # -------------------------------------------------------------------------

    notebook_id = st.text_input(
        "KNOWLEDGE NOTEBOOK",
        value=st.session_state.get(
            "sf004_notebook_id",
            "soul_forge",
        ),
        key="sf004_notebook_id_input",
        help=(
            "Use a separate notebook ID for each knowledge collection."
        ),
    ).strip()

    if not notebook_id:
        notebook_id = "soul_forge"

    st.session_state.sf004_notebook_id = notebook_id

    # -------------------------------------------------------------------------
    # STATS
    # -------------------------------------------------------------------------

    try:
        stats = rag_engine.index_stats()
    except Exception as exc:
        stats = {
            "error": f"{type(exc).__name__}: {exc}"
        }

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric(
            "RAG CHUNKS",
            stats.get(
                "chunks",
                stats.get(
                    "total_chunks",
                    "—",
                ),
            ),
        )

    with s2:
        st.metric(
            "RESOURCES",
            stats.get(
                "resources",
                stats.get(
                    "total_resources",
                    "—",
                ),
            ),
        )

    with s3:
        st.metric(
            "NOTEBOOKS",
            stats.get(
                "notebooks",
                "—",
            ),
        )

    with s4:
        st.metric(
            "EMBEDDING",
            "MiniLM",
        )

    st.divider()

    # -------------------------------------------------------------------------
    # TABS
    # -------------------------------------------------------------------------

    (
        ask_tab,
        ingest_tab,
        resources_tab,
        history_tab,
        system_tab,
    ) = st.tabs(
        [
            "💬 ASK KNOWLEDGE",
            "📥 ADD RESOURCES",
            "📚 RESOURCE LIBRARY",
            "🕘 QUESTION HISTORY",
            "⚙️ RAG STATUS",
        ]
    )

    # =========================================================================
    # ASK
    # =========================================================================

    with ask_tab:

        st.subheader("Ask your knowledge")

        st.caption(
            "Questions are answered from retrieved notebook resources. "
            "Knowledge requests use the dedicated Knowledge Agent."
        )

        question = st.text_area(
            "YOUR QUESTION",
            height=130,
            placeholder=(
                "Ask something about your uploaded resources..."
            ),
            key="sf004_question_input",
        )

        top_k = st.slider(
            "RETRIEVED CHUNKS",
            min_value=1,
            max_value=12,
            value=8,
            key="sf004_top_k",
        )

        ask = st.button(
            "⚡ ASK SOUL FORGE",
            key="sf004_ask_button",
            use_container_width=True,
            type="primary",
        )

        if ask:

            if not question.strip():
                st.warning("Enter a question first.")

            else:

                with st.spinner(
                    "SOUL FORGE · RETRIEVING KNOWLEDGE..."
                ):

                    try:

                        result = knowledge_agent.ask_knowledge(
                            question.strip(),
                            notebook_id,
                            top_k=top_k,
                            provider="gemini",
                        )

                        st.session_state.sf004_last_answer = result

                    except Exception as exc:

                        st.error(
                            "Knowledge Agent failed."
                        )

                        st.exception(exc)

        result = st.session_state.get(
            "sf004_last_answer"
        )

        if result:

            st.divider()

            st.markdown("### 🧠 ANSWER")

            answer = (
                result.get("answer")
                or result.get("response")
                or result.get("content")
                or result.get("message")
            )

            if answer:
                st.markdown(str(answer))
            else:
                st.json(_safe_json(result))

            # -----------------------------------------------------------------
            # AGENT METADATA
            # -----------------------------------------------------------------

            st.divider()

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.caption("AGENT")
                st.write(
                    result.get(
                        "agent",
                        "Knowledge Agent",
                    )
                )

            with m2:
                st.caption("PROVIDER")
                st.write(
                    result.get(
                        "provider",
                        "gemini",
                    )
                )

            with m3:
                st.caption("MODEL")
                st.write(
                    result.get(
                        "model",
                        "configured Gemini",
                    )
                )

            with m4:
                sources = (
                    result.get("sources")
                    or result.get("retrieved")
                    or []
                )

                st.caption("SOURCES")
                st.write(
                    len(sources)
                    if isinstance(sources, list)
                    else "—"
                )

            # -----------------------------------------------------------------
            # SOURCES
            # -----------------------------------------------------------------

            if isinstance(sources, list) and sources:

                st.divider()

                st.markdown("### 📌 SOURCES USED")

                for index, source in enumerate(
                    sources,
                    start=1,
                ):

                    if isinstance(source, dict):
                        _render_source(
                            source,
                            index,
                        )
                    else:
                        st.write(
                            f"#{index} · {source}"
                        )

            # -----------------------------------------------------------------
            # RAW RETRIEVAL
            # -----------------------------------------------------------------

            with st.expander(
                "🔎 RETRIEVAL / AGENT METADATA"
            ):

                st.json(
                    _safe_json(result)
                )

    # =========================================================================
    # INGEST
    # =========================================================================

    with ingest_tab:

        st.subheader("Add knowledge resources")

        st.caption(
            "Upload source material and send it into the SF-004 ingestion "
            "and semantic retrieval pipeline."
        )

        uploaded = st.file_uploader(
            "UPLOAD KNOWLEDGE",
            type=[
                "pdf",
                "docx",
                "txt",
                "md",
                "csv",
                "json",
                "py",
            ],
            accept_multiple_files=True,
            key="sf004_uploader",
        )

        if uploaded:

            st.write(
                f"**{len(uploaded)} resource(s) selected**"
            )

            for file in uploaded:

                size_kb = len(
                    file.getvalue()
                ) / 1024

                st.write(
                    f"📄 **{file.name}** · "
                    f"{size_kb:.1f} KB"
                )

            if st.button(
                "📥 INDEX ALL RESOURCES",
                key="sf004_index_all_button",
                use_container_width=True,
                type="primary",
            ):

                progress = st.progress(
                    0,
                    text="Preparing ingestion...",
                )

                results = []

                for index, file in enumerate(uploaded):

                    try:

                        result = _call_ingest_file(
                            file,
                            notebook_id,
                        )

                        results.append(
                            {
                                "name": file.name,
                                "status": "PASS",
                                "result": result,
                            }
                        )

                    except Exception as exc:

                        results.append(
                            {
                                "name": file.name,
                                "status": "FAIL",
                                "error": (
                                    f"{type(exc).__name__}: {exc}"
                                ),
                            }
                        )

                    progress.progress(
                        int(
                            ((index + 1) / len(uploaded))
                            * 100
                        ),
                        text=(
                            f"Indexed "
                            f"{index + 1}/{len(uploaded)}"
                        ),
                    )

                st.session_state.sf004_ingest_results = results

                st.success(
                    "Knowledge ingestion operation completed."
                )

        ingest_results = st.session_state.get(
            "sf004_ingest_results",
            [],
        )

        if ingest_results:

            st.divider()

            st.markdown(
                "### INGESTION RESULTS"
            )

            for item in ingest_results:

                if item["status"] == "PASS":

                    st.success(
                        f"{item['name']} · INDEXED"
                    )

                    with st.expander(
                        f"Metadata · {item['name']}"
                    ):
                        st.json(
                            _safe_json(
                                item["result"]
                            )
                        )

                else:

                    st.error(
                        f"{item['name']} · FAILED"
                    )

                    st.code(
                        item["error"]
                    )

    # =========================================================================
    # RESOURCES
    # =========================================================================

    with resources_tab:

        st.subheader("Resource library")

        resources = _load_resource_inventory()

        notebook_resources = [
            item
            for item in resources
            if str(
                item.get("notebook_id")
            ) == notebook_id
        ]

        if not notebook_resources:

            st.info(
                "No indexed resources found for this notebook."
            )

        else:

            for resource in notebook_resources:

                with st.container(
                    border=True
                ):

                    c1, c2, c3, c4 = st.columns(
                        [2.8, 1.2, 1.0, 1.0]
                    )

                    with c1:
                        st.write(
                            f"**{resource.get('name')}**"
                        )
                        st.caption(
                            str(
                                resource.get(
                                    "resource_id"
                                )
                            )
                        )

                    with c2:
                        st.caption("CHUNKS")
                        st.write(
                            resource.get(
                                "chunks",
                                0,
                            )
                        )

                    with c3:
                        st.caption("CHARS")
                        st.write(
                            resource.get(
                                "characters",
                                0,
                            )
                        )

                    with c4:
                        st.caption("STATUS")
                        st.success(
                            "INDEXED"
                        )

    # =========================================================================
    # HISTORY
    # =========================================================================

    with history_tab:

        st.subheader("Question history")

        history = _history(
            notebook_id
        )

        if not history:

            st.info(
                "No questions recorded for this notebook yet."
            )

        else:

            for index, item in enumerate(
                reversed(history),
                start=1,
            ):

                question_text = (
                    item.get("question")
                    or item.get("query")
                    or "Question"
                )

                with st.expander(
                    f"{index}. {question_text}"
                ):

                    answer_text = (
                        item.get("answer")
                        or item.get("response")
                        or ""
                    )

                    if answer_text:
                        st.markdown(
                            "**ANSWER**"
                        )
                        st.write(
                            answer_text
                        )

                    st.json(
                        _safe_json(item)
                    )

    # =========================================================================
    # STATUS
    # =========================================================================

    with system_tab:

        st.subheader("RAG system status")

        try:

            current_stats = (
                rag_engine.index_stats()
            )

            st.success(
                "RAG ENGINE · ONLINE"
            )

            st.json(
                _safe_json(
                    current_stats
                )
            )

        except Exception as exc:

            st.error(
                "RAG ENGINE · ERROR"
            )

            st.exception(exc)

        st.divider()

        st.write(
            "**Knowledge routing**"
        )

        st.code(
            "KNOWLEDGE → GEMINI\n"
            "RETRIEVAL → SEMANTIC + KEYWORD HYBRID\n"
            "EMBEDDINGS → all-MiniLM-L6-v2\n"
            "HISTORY → persistent JSONL\n"
            "NOTEBOOK → isolated namespace"
        )
