
from pathlib import Path
from datetime import datetime
import time

import streamlit as st


# =============================================================================
# SOUL FORGE
# =============================================================================

PROJECT_ROOT = Path(
    "/content/BANKAI-RACE-CONTROL"
)


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="SOUL FORGE",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# SESSION STATE
# =============================================================================

DEFAULTS = {

    "page":
        "Command Center",

    "selected_project":
        "BANKAI-RACE-CONTROL",

    "chat_messages":
        [],

    "agentic_result":
        None,

    "agentic_prompt":
        "",

    "agentic_user_tested":
        False,

    "agentic_accepted":
        False,

    # PITMYDORO
    "pit_running":
        False,

    "pit_started_at":
        None,

    "pit_elapsed":
        0.0,

    "pit_lap":
        1,

    "pit_duration":
        25 * 60,

    "pit_task":
        "",

}


for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =============================================================================
# BACKEND
# =============================================================================

def bankai_request(
    prompt,
    intent=None,
):

    """
    Production AI path.

    UI
      ↓
    BANKAI AI BRIDGE
      ↓
    RUFLO
      ↓
    OPENROUTER
      ↓
    MODEL
    """

    try:

        from app.core.bankai_ai_bridge import (
            bankai_chat,
        )

        kwargs = {}

        if intent:

            kwargs["force_intent"] = intent

        return bankai_chat(
            prompt,
            **kwargs,
        )

    except Exception as exc:

        return {
            "text":
                (
                    "BANKAI AI BRIDGE ERROR\n\n"
                    f"{type(exc).__name__}: {exc}"
                ),
            "status":
                "error",
        }


def result_text(result):

    if isinstance(result, dict):

        return (
            result.get("text")
            or result.get("response")
            or result.get("content")
            or result.get("message")
            or "No response."
        )

    return str(result)


def project_name():

    return st.session_state.get(
        "selected_project",
        "BANKAI-RACE-CONTROL",
    )


# =============================================================================
# HEADER
# =============================================================================

left, right = st.columns(
    [6, 1],
    gap="small",
)

with left:

    st.title(
        "⚔️ SOUL FORGE"
    )

    st.caption(
        "Personal Agentic AI Development Platform"
    )

    st.caption(
        "BLEACH × RED BULL RACING"
        "  •  BUILD WITH DISCIPLINE"
        "  •  SHIP WITH CONTROL"
    )

with right:

    st.metric(
        "SYSTEM",
        "ONLINE",
    )

    st.caption(
        datetime.now().strftime(
            "%H:%M:%S"
        )
    )


# =============================================================================
# MOTIVATION
# =============================================================================

MOTIVATION = [

    (
        "BLEACH INSPIRED",
        "A blade becomes stronger through discipline, repetition, and resolve.",
    ),

    (
        "RACING MINDSET",
        "Stay focused on the next lap. Improve the next decision.",
    ),

    (
        "MAX-INSPIRED",
        "Pressure is part of racing. The goal is to keep improving anyway.",
    ),

    (
        "SOUL FORGE",
        "Don't wait for perfect conditions. Forge the next step.",
    ),

]

if "quote_index" not in st.session_state:

    st.session_state.quote_index = 0


quote_title, quote_text = MOTIVATION[
    st.session_state.quote_index
    % len(MOTIVATION)
]

st.info(
    f"**{quote_title}** — {quote_text}"
)


# =============================================================================
# TOP TASKBAR
# =============================================================================

PAGES = [

    ("🏠", "Command Center"),

    ("📁", "Projects"),

    ("📚", "Knowledge"),

    ("💬", "Chat"),

    ("🤖", "Agentic AI"),

    ("⏱️", "PITMYDORO"),

]

columns = st.columns(
    len(PAGES),
    gap="small",
)

for column, (emoji, page) in zip(
    columns,
    PAGES,
):

    with column:

        if st.button(
            f"{emoji} {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page
                else "secondary"
            ),
        ):

            st.session_state.page = page

            st.rerun()


st.divider()


# =============================================================================
# COMMAND CENTER
# =============================================================================

def render_command_center():

    st.subheader(
        "🏠 Command Center"
    )

    c1, c2, c3, c4 = st.columns(
        4,
        gap="small",
    )

    with c1:

        st.metric(
            "AI CORE",
            "READY",
        )

    with c2:

        st.metric(
            "AGENTIC ENGINE",
            "READY",
        )

    with c3:

        st.metric(
            "PROJECT",
            project_name(),
        )

    with c4:

        st.metric(
            "FOCUS LAP",
            f"{st.session_state.pit_lap:02d}",
        )

    st.markdown(
        "### ⚡ System"
    )

    c1, c2, c3 = st.columns(
        3,
        gap="small",
    )

    with c1:

        st.success(
            "BANKAI AI BRIDGE"
        )

    with c2:

        st.success(
            "RUFLO"
        )

    with c3:

        st.success(
            "OPENROUTER"
        )

    st.markdown(
        "### 🧠 SOUL FORGE CORE"
    )

    modules = [

        ("Conversation", 94),

        ("Planning", 88),

        ("Coding", 86),

        ("Knowledge", 80),

        ("Agentic Reasoning", 92),

    ]

    for name, value in modules:

        st.caption(
            f"{name} · {value}%"
        )

        st.progress(
            value / 100
        )

    st.markdown(
        "### 🏎️ Current Mission"
    )

    st.info(
        st.session_state.pit_task
        or "No active PITMYDORO mission."
    )


# =============================================================================
# PROJECTS
# =============================================================================

def render_projects():

    st.subheader(
        "📁 Projects"
    )

    projects = [

        "BANKAI-RACE-CONTROL",

        "Einstain-ai-brain-v2",

    ]

    current = project_name()

    selected = st.selectbox(
        "Current Project",
        projects,
        index=(
            projects.index(current)
            if current in projects
            else 0
        ),
    )

    if selected != current:

        st.session_state.selected_project = (
            selected
        )

        st.rerun()

    c1, c2, c3 = st.columns(
        3,
        gap="small",
    )

    with c1:

        st.metric(
            "PROJECT",
            selected,
        )

    with c2:

        st.metric(
            "MODE",
            "DEVELOPMENT",
        )

    with c3:

        st.metric(
            "FOCUS",
            "PITMYDORO",
        )

    st.markdown(
        "### 🔍 Project Signals"
    )

    signals = [

        (
            "AI Architecture",
            "RUFLO + OPENROUTER",
        ),

        (
            "Model Routing",
            "MULTI-MODEL",
        ),

        (
            "Development",
            "ACTIVE",
        ),

        (
            "Focus System",
            "PITMYDORO",
        ),

    ]

    for label, value in signals:

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [2, 5],
                gap="small",
            )

            with c1:

                st.caption(label)

            with c2:

                st.write(value)


# =============================================================================
# KNOWLEDGE
# =============================================================================


def render_knowledge():

    st.subheader(
        "📚 Knowledge Studio"
    )

    st.caption(
        "NotebookLM-inspired source-grounded research workspace."
    )

    # -------------------------------------------------------------------------
    # SESSION STATE
    # -------------------------------------------------------------------------

    if "knowledge_sources" not in st.session_state:

        st.session_state.knowledge_sources = []

    if "knowledge_selected" not in st.session_state:

        st.session_state.knowledge_selected = []

    if "knowledge_answer" not in st.session_state:

        st.session_state.knowledge_answer = ""

    if "knowledge_question" not in st.session_state:

        st.session_state.knowledge_question = ""

    if "knowledge_notes" not in st.session_state:

        st.session_state.knowledge_notes = ""

    # -------------------------------------------------------------------------
    # SOURCE COUNTS
    # -------------------------------------------------------------------------

    sources = st.session_state.knowledge_sources

    source_count = len(sources)

    total_words = sum(
        item.get("words", 0)
        for item in sources
        if isinstance(item, dict)
    )

    # -------------------------------------------------------------------------
    # HEADER METRICS
    # -------------------------------------------------------------------------

    m1, m2, m3, m4 = st.columns(
        4,
        gap="small",
    )

    with m1:

        st.metric(
            "SOURCES",
            source_count,
        )

    with m2:

        st.metric(
            "WORDS",
            f"{total_words:,}",
        )

    with m3:

        st.metric(
            "SELECTED",
            len(
                st.session_state.knowledge_selected
            ),
        )

    with m4:

        st.metric(
            "INDEX",
            "READY"
            if source_count
            else "EMPTY",
        )

    st.divider()

    # =========================================================================
    # MAIN WORKSPACE
    # =========================================================================

    source_col, research_col = st.columns(
        [1, 2.5],
        gap="large",
    )

    # =========================================================================
    # SOURCE LIBRARY
    # =========================================================================

    with source_col:

        st.markdown(
            "### 📄 Sources"
        )

        st.caption(
            "Add documents and choose which sources SOUL FORGE can use."
        )

        uploaded_files = st.file_uploader(
            "Add sources",
            type=[
                "txt",
                "md",
                "pdf",
                "csv",
                "json",
                "py",
            ],
            accept_multiple_files=True,
            key="knowledge_uploads",
        )

        if uploaded_files:

            for uploaded in uploaded_files:

                existing_names = [
                    item.get("name")
                    for item in sources
                    if isinstance(item, dict)
                ]

                if uploaded.name not in existing_names:

                    try:

                        raw = uploaded.read()

                        text = raw.decode(
                            "utf-8",
                            errors="replace",
                        )

                        words = len(
                            re.findall(
                                r"\b\w+\b",
                                text,
                            )
                        )

                        sources.append(
                            {
                                "name":
                                    uploaded.name,

                                "text":
                                    text,

                                "words":
                                    words,

                                "size":
                                    len(raw),

                                "added":
                                    datetime.now().isoformat(
                                        timespec="seconds"
                                    ),
                            }
                        )

                        st.session_state.knowledge_sources = (
                            sources
                        )

                    except Exception as exc:

                        st.error(
                            f"{uploaded.name}: {exc}"
                        )

            st.rerun()

        st.divider()

        if sources:

            st.markdown(
                "#### Source Library"
            )

            for index, source in enumerate(
                sources
            ):

                name = source.get(
                    "name",
                    f"Source {index + 1}",
                )

                selected = (
                    index
                    in st.session_state.knowledge_selected
                )

                toggle = st.checkbox(
                    name,
                    value=selected,
                    key=f"knowledge_source_{index}",
                )

                if toggle:

                    if (
                        index
                        not in st.session_state.knowledge_selected
                    ):

                        st.session_state.knowledge_selected.append(
                            index
                        )

                else:

                    if (
                        index
                        in st.session_state.knowledge_selected
                    ):

                        st.session_state.knowledge_selected.remove(
                            index
                        )

            st.divider()

            st.markdown(
                "#### Source Actions"
            )

            c1, c2 = st.columns(
                2,
                gap="small",
            )

            with c1:

                if st.button(
                    "✓ ALL",
                    use_container_width=True,
                ):

                    st.session_state.knowledge_selected = (
                        list(range(len(sources)))
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "CLEAR",
                    use_container_width=True,
                ):

                    st.session_state.knowledge_selected = []

                    st.rerun()

        else:

            st.info(
                "No sources yet.\n\n"
                "Upload Markdown, text, PDF, CSV, JSON or Python files."
            )

        st.divider()

        st.markdown(
            "#### 📊 Source Status"
        )

        if sources:

            st.success(
                "SOURCE INDEX READY"
            )

            st.caption(
                f"{source_count} source(s) loaded"
            )

            st.caption(
                f"{total_words:,} words available"
            )

        else:

            st.warning(
                "SOURCE LIBRARY EMPTY"
            )

    # =========================================================================
    # RESEARCH CHAT
    # =========================================================================

    with research_col:

        st.markdown(
            "### 🧠 Research Chat"
        )

        selected_sources = [

            sources[index]

            for index
            in st.session_state.knowledge_selected

            if (
                0 <= index < len(sources)
            )

        ]

        if selected_sources:

            source_names = ", ".join(
                source.get(
                    "name",
                    "Unknown",
                )
                for source in selected_sources
            )

            st.success(
                f"Using {len(selected_sources)} source(s)"
            )

            st.caption(
                source_names
            )

        else:

            st.info(
                "Select one or more sources from the left."
            )

        question = st.text_area(
            "Research Question",
            value=(
                st.session_state.knowledge_question
            ),
            placeholder=(
                "Ask a question about your selected sources..."
            ),
            height=130,
            key="knowledge_question_input",
        )

        st.session_state.knowledge_question = question

        c1, c2 = st.columns(
            [3, 1],
            gap="small",
        )

        with c1:

            ask = st.button(
                "🔍 ASK SOUL FORGE",
                use_container_width=True,
                type="primary",
            )

        with c2:

            clear_answer = st.button(
                "CLEAR",
                use_container_width=True,
            )

        if clear_answer:

            st.session_state.knowledge_answer = ""

            st.rerun()

        if ask:

            if not selected_sources:

                st.warning(
                    "Select at least one source."
                )

            elif not question.strip():

                st.warning(
                    "Enter a research question."
                )

            else:

                combined_context = "\n\n".join(

                    (
                        f"=== SOURCE: "
                        f"{source.get('name', 'Unknown')} ===\n"
                        f"{source.get('text', '')}"
                    )

                    for source
                    in selected_sources

                )

                research_prompt = f"""
You are SOUL FORGE Knowledge Research.

Answer the user's question using ONLY the supplied source material.

If the answer is not supported by the sources, clearly say that
the available sources do not provide enough evidence.

Be precise and structured.

USER QUESTION:
{question.strip()}

SOURCE MATERIAL:
{combined_context}
"""

                with st.spinner(
                    "SOUL FORGE is researching..."
                ):

                    try:

                        result = bankai_request(
                            research_prompt,
                        )

                        answer = result_text(
                            result
                        )

                        st.session_state.knowledge_answer = (
                            answer
                        )

                    except Exception as exc:

                        st.session_state.knowledge_answer = (
                            f"Knowledge research error: {exc}"
                        )

        # ---------------------------------------------------------------------
        # ANSWER
        # ---------------------------------------------------------------------

        if (
            st.session_state.knowledge_answer
        ):

            st.divider()

            st.markdown(
                "### 💡 Answer"
            )

            st.write(
                st.session_state.knowledge_answer
            )

            st.divider()

            st.markdown(
                "### 📌 Sources Used"
            )

            for source in selected_sources:

                st.caption(
                    f"📄 {source.get('name', 'Unknown')}"
                )

        # ---------------------------------------------------------------------
        # NOTES
        # ---------------------------------------------------------------------

        st.divider()

        st.markdown(
            "### 📝 Research Notes"
        )

        st.session_state.knowledge_notes = (
            st.text_area(
                "Notes",
                value=(
                    st.session_state.knowledge_notes
                ),
                placeholder=(
                    "Save ideas, findings, hypotheses or follow-up questions..."
                ),
                height=150,
                label_visibility="collapsed",
                key="knowledge_notes_input",
            )
        )

    # =========================================================================
    # BOTTOM RESEARCH TOOLS
    # =========================================================================

    st.divider()

    st.markdown(
        "### 📖 Research Workspace"
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "📄 SOURCES",
            "💬 CHAT",
            "🎯 STUDY",
        ]
    )

    with tab1:

        if sources:

            for source in sources:

                with st.expander(
                    f"📄 {source.get('name', 'Unknown')}"
                ):

                    st.caption(
                        f"{source.get('words', 0):,} words"
                    )

                    text = source.get(
                        "text",
                        "",
                    )

                    if len(text) > 5000:

                        st.text(
                            text[:5000]
                        )

                        st.caption(
                            "Preview limited to 5,000 characters."
                        )

                    else:

                        st.text(
                            text
                        )

        else:

            st.info(
                "Upload sources to inspect them here."
            )

    with tab2:

        if st.session_state.knowledge_answer:

            st.write(
                st.session_state.knowledge_answer
            )

        else:

            st.info(
                "Your research answers will appear here."
            )

    with tab3:

        st.markdown(
            "#### 🎯 Study Mode"
        )

        st.caption(
            "Turn your sources into active learning."
        )

        if sources:

            study_topics = [

                source.get(
                    "name",
                    "Source",
                )

                for source
                in sources

            ]

            topic = st.selectbox(
                "Study Source",
                study_topics,
            )

            st.write(
                "Use Research Chat to ask for:"
            )

            st.write(
                "• summaries"
            )

            st.write(
                "• explanations"
            )

            st.write(
                "• key concepts"
            )

            st.write(
                "• comparisons"
            )

            st.write(
                "• questions"
            )

            st.write(
                "• revision material"
            )

        else:

            st.info(
                "Add sources to activate Study Mode."
            )


# =============================================================================
# CHAT
# =============================================================================

def render_chat():

    st.subheader(
        "💬 SOUL FORGE Chat"
    )

    st.caption(
        "SOUL FORGE → RUFLO → OPENROUTER"
    )

    for message in (
        st.session_state.chat_messages
    ):

        with st.chat_message(
            message.get(
                "role",
                "user",
            )
        ):

            st.write(
                message.get(
                    "content",
                    "",
                )
            )

    prompt = st.chat_input(
        "Ask SOUL FORGE..."
    )

    if prompt:

        st.session_state.chat_messages.append(
            {
                "role":
                    "user",

                "content":
                    prompt,
            }
        )

        with st.chat_message(
            "user"
        ):

            st.write(prompt)

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "BANKAI THINKING..."
            ):

                result = bankai_request(
                    prompt,
                    intent="CHAT",
                )

            response = result_text(
                result
            )

            st.write(
                response
            )

            st.session_state.chat_messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        response,
                }
            )

        st.rerun()


# =============================================================================
# AGENTIC AI
# =============================================================================

def render_agentic():

    st.subheader(
        "🤖 Agentic AI"
    )

    st.caption(
        "UNDERSTAND → PLAN → IMPLEMENT → "
        "VALIDATE → REVIEW → FINALIZE"
    )

    prompt = st.text_area(
        "Mission",
        value=(
            st.session_state.agentic_prompt
        ),
        placeholder=(
            "Describe the development mission..."
        ),
        height=120,
    )

    st.session_state.agentic_prompt = prompt

    if st.button(
        "🚀 START AGENTIC WORKFLOW",
        use_container_width=True,
    ):

        if not prompt.strip():

            st.warning(
                "Enter a mission first."
            )

        else:

            with st.status(
                "RUFLO workflow running...",
                expanded=True,
            ) as status:

                st.write(
                    "🧠 UNDERSTAND"
                )

                st.write(
                    "📋 PLAN"
                )

                st.write(
                    "⚙️ IMPLEMENT"
                )

                st.write(
                    "🧪 VALIDATE"
                )

                st.write(
                    "🔎 REVIEW"
                )

                st.write(
                    "🏁 FINALIZE"
                )

                result = bankai_request(
                    prompt,
                    intent="AGENTIC",
                )

                st.session_state.agentic_result = (
                    result
                )

                status.update(
                    label="Workflow complete",
                    state="complete",
                )

    if (
        st.session_state.agentic_result
        is not None
    ):

        st.markdown(
            "### 🧩 Result"
        )

        st.write(
            result_text(
                st.session_state.agentic_result
            )
        )

    st.markdown(
        "### 👨‍💻 User Control"
    )

    c1, c2 = st.columns(
        2,
        gap="small",
    )

    with c1:

        if st.button(
            "🧪 USER TEST",
            use_container_width=True,
        ):

            st.session_state.agentic_user_tested = (
                True
            )

            st.success(
                "Marked for user testing."
            )

    with c2:

        if st.button(
            "✓ ACCEPT",
            use_container_width=True,
        ):

            st.session_state.agentic_accepted = (
                True
            )

            st.success(
                "User acceptance recorded."
            )


# =============================================================================
# PITMYDORO
# =============================================================================

def render_pitmydoro():

    st.subheader(
        "⏱️ PITMYDORO"
    )

    st.caption(
        "Focus timer for developers — "
        "one lap, one mission, one improvement."
    )

    # -------------------------------------------------------------------------
    # CURRENT TIMER
    # -------------------------------------------------------------------------

    if st.session_state.pit_running:

        if (
            st.session_state.pit_started_at
            is None
        ):

            st.session_state.pit_started_at = (
                time.time()
            )

        elapsed = (
            st.session_state.pit_elapsed
            + (
                time.time()
                - st.session_state.pit_started_at
            )
        )

    else:

        elapsed = (
            st.session_state.pit_elapsed
        )

    remaining = max(
        0,
        st.session_state.pit_duration
        - elapsed,
    )

    # -------------------------------------------------------------------------
    # SIDE-BY-SIDE LAYOUT
    # -------------------------------------------------------------------------

    timer_col, focus_col = st.columns(
        [1.25, 1],
        gap="large",
    )

    # -------------------------------------------------------------------------
    # TIMER
    # -------------------------------------------------------------------------

    with timer_col:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🏁 LAP TIMER"
            )

            st.metric(
                "LAP",
                f"{st.session_state.pit_lap:02d}",
            )

            minutes = int(
                remaining // 60
            )

            seconds = int(
                remaining % 60
            )

            st.metric(
                "TIME REMAINING",
                f"{minutes:02d}:{seconds:02d}",
            )

            progress = (

                min(
                    1.0,
                    elapsed
                    / st.session_state.pit_duration,
                )

                if st.session_state.pit_duration
                else 0
            )

            st.progress(
                progress
            )

            if st.session_state.pit_running:

                st.success(
                    "🔴 RACING"
                )

                st.caption(
                    "FULL FOCUS • STAY ON THE LAP"
                )

            else:

                st.info(
                    "⚫ STANDBY"
                )

                st.caption(
                    "READY TO START"
                )

    # -------------------------------------------------------------------------
    # PITMYDORO SIDE
    # -------------------------------------------------------------------------

    with focus_col:

        with st.container(
            border=True
        ):

            st.markdown(
                "### 🏎️ PITMYDORO"
            )

            st.caption(
                "FOCUS SESSION"
            )

            st.markdown(
                "#### 🎯 Current Mission"
            )

            task = st.text_input(
                "Mission",
                value=(
                    st.session_state.pit_task
                ),
                placeholder=(
                    "What are you focusing on?"
                ),
            )

            st.session_state.pit_task = task

            st.markdown(
                "#### ⚙️ Session"
            )

            duration = st.selectbox(
                "Duration",
                [
                    15,
                    25,
                    45,
                    60,
                ],
                index=(
                    [15, 25, 45, 60].index(
                        st.session_state.pit_duration
                        // 60
                    )
                    if (
                        st.session_state.pit_duration
                        // 60
                    ) in [15, 25, 45, 60]
                    else 1
                ),
                format_func=lambda value:
                    f"{value} minutes",
            )

            if (
                not st.session_state.pit_running
                and duration * 60
                != st.session_state.pit_duration
            ):

                st.session_state.pit_duration = (
                    duration * 60
                )

                st.session_state.pit_elapsed = (
                    0.0
                )

            st.markdown(
                "#### 🏎️ Controls"
            )

            c1, c2 = st.columns(
                2,
                gap="small",
            )

            with c1:

                if not st.session_state.pit_running:

                    if st.button(
                        "🏁 START",
                        use_container_width=True,
                    ):

                        st.session_state.pit_running = (
                            True
                        )

                        st.session_state.pit_started_at = (
                            time.time()
                        )

                        st.rerun()

                else:

                    if st.button(
                        "⏸ PAUSE",
                        use_container_width=True,
                    ):

                        st.session_state.pit_elapsed = (
                            elapsed
                        )

                        st.session_state.pit_running = (
                            False
                        )

                        st.session_state.pit_started_at = (
                            None
                        )

                        st.rerun()

            with c2:

                if st.button(
                    "🔄 RESET",
                    use_container_width=True,
                ):

                    st.session_state.pit_running = (
                        False
                    )

                    st.session_state.pit_started_at = (
                        None
                    )

                    st.session_state.pit_elapsed = (
                        0.0
                    )

                    st.rerun()

            st.divider()

            st.markdown(
                "### 🧠 DRIVER MINDSET"
            )

            st.info(
                "One task.\n\n"
                "One decision.\n\n"
                "One improvement."
            )

    # -------------------------------------------------------------------------
    # LAP CONTROL
    # -------------------------------------------------------------------------

    st.divider()

    st.markdown(
        "### 🏎️ RACE CONTROL"
    )

    c1, c2, c3 = st.columns(
        3,
        gap="small",
    )

    with c1:

        if st.button(
            "⏭️ NEXT LAP",
            use_container_width=True,
        ):

            st.session_state.pit_lap += 1

            st.session_state.pit_elapsed = (
                0.0
            )

            st.session_state.pit_started_at = (

                time.time()

                if st.session_state.pit_running

                else None

            )

            st.rerun()

    with c2:

        if st.button(
            "🏁 NEW SESSION",
            use_container_width=True,
        ):

            st.session_state.pit_running = (
                False
            )

            st.session_state.pit_started_at = (
                None
            )

            st.session_state.pit_elapsed = (
                0.0
            )

            st.session_state.pit_lap = 1

            st.rerun()

    with c3:

        if st.button(
            "🎯 FOCUS MODE",
            use_container_width=True,
        ):

            st.session_state.pit_running = (
                True
            )

            st.session_state.pit_started_at = (
                time.time()
            )

            st.rerun()

    # -------------------------------------------------------------------------
    # LIVE REFRESH
    # -------------------------------------------------------------------------

    if st.session_state.pit_running:

        @st.fragment(
            run_every="1s"
        )
        def pitmydoro_live():

            if (
                st.session_state.pit_started_at
                is None
            ):

                return

            current = (
                st.session_state.pit_elapsed
                + (
                    time.time()
                    - st.session_state.pit_started_at
                )
            )

            remaining_live = max(
                0,
                st.session_state.pit_duration
                - current,
            )

            minutes_live = int(
                remaining_live // 60
            )

            seconds_live = int(
                remaining_live % 60
            )

            st.metric(
                "LIVE COUNTDOWN",
                f"{minutes_live:02d}:{seconds_live:02d}",
            )

            if remaining_live <= 0:

                st.warning(
                    "🏁 LAP COMPLETE"
                )

        pitmydoro_live()


# =============================================================================
# ROUTER
# =============================================================================

if (
    st.session_state.page
    == "Command Center"
):

    render_command_center()

elif (
    st.session_state.page
    == "Projects"
):

    render_projects()

elif (
    st.session_state.page
    == "Knowledge"
):

    render_knowledge()

elif (
    st.session_state.page
    == "Chat"
):

    render_chat()

elif (
    st.session_state.page
    == "Agentic AI"
):

    render_agentic()

elif (
    st.session_state.page
    == "PITMYDORO"
):

    render_pitmydoro()


# =============================================================================
# FOOTER
# =============================================================================

st.divider()

c1, c2, c3 = st.columns(
    [2, 5, 2],
    gap="small",
)

with c1:

    st.caption(
        "⚔️ SOUL FORGE"
    )

with c2:

    st.caption(
        f"PROJECT • {project_name()}"
    )

with c3:

    st.caption(
        datetime.now().strftime(
            "%H:%M"
        )
    )
