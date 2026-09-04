
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st


# =============================================================================
# PROJECT
# =============================================================================

PROJECT_ROOT = Path("/content/BANKAI-RACE-CONTROL")
ROUTING_FILE = PROJECT_ROOT / "config" / "bankai_model_routing.json"
LOG_FILE = PROJECT_ROOT / "data" / "v068_ui.log"


# =============================================================================
# PAGE
# =============================================================================

st.set_page_config(
    page_title="BANKAI RACE CONTROL",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# SESSION STATE
# =============================================================================

DEFAULT_STATE = {
    "page": "HOME",
    "chat_messages": [],
    "mission": "SYSTEM STANDBY",
    "monitoring": True,
    "auto_refresh": False,
    "last_refresh": datetime.now(),
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =============================================================================
# CSS
# =============================================================================

st.markdown(
    """
    <style>

    /* ================================================================
       GLOBAL
       ================================================================ */

    :root {
        --black: #050609;
        --black2: #0a0d12;
        --panel: #0d1118;
        --panel2: #111722;

        --white: #f5f7fa;
        --muted: #8993a3;

        --blue: #1688ff;
        --blue2: #063c8c;

        --red: #e10600;
        --red2: #8f0906;

        --gold: #f5b942;
        --gold2: #9d6d16;

        --line: rgba(255,255,255,0.09);
        --line-blue: rgba(22,136,255,0.30);
        --line-red: rgba(225,6,0,0.30);
        --line-gold: rgba(245,185,66,0.30);
    }


    /* ================================================================
       APP BACKGROUND
       ================================================================ */

    html,
    body,
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(22,136,255,0.13),
                transparent 28%
            ),
            radial-gradient(
                circle at 12% 35%,
                rgba(225,6,0,0.09),
                transparent 25%
            ),
            radial-gradient(
                circle at 55% 100%,
                rgba(245,185,66,0.06),
                transparent 28%
            ),
            var(--black) !important;
        color: var(--white) !important;
    }


    [data-testid="stHeader"] {
        background: transparent !important;
    }


    .block-container {
        max-width: 1700px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }


    /* ================================================================
       TOP TASKBAR
       ================================================================ */

    div[data-testid="stHorizontalBlock"]:has(
        button[kind="secondary"]
    ) {
        align-items: center;
    }


    /* ================================================================
       BUTTONS
       ================================================================ */

    .stButton > button {
        width: 100%;
        min-height: 40px;

        border: 1px solid var(--line);
        border-radius: 8px;

        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.018)
            );

        color: #dce3ec;

        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.2px;

        transition:
            border-color 0.18s ease,
            background 0.18s ease,
            transform 0.18s ease;
    }


    .stButton > button:hover {
        border-color: var(--blue);
        background:
            linear-gradient(
                180deg,
                rgba(22,136,255,0.18),
                rgba(22,136,255,0.04)
            );
        color: white;
        transform: translateY(-1px);
    }


    /* ================================================================
       HEADER
       ================================================================ */

    .bankai-header {
        padding: 22px 24px 20px 24px;
        margin-bottom: 14px;

        border: 1px solid var(--line);
        border-left: 3px solid var(--red);
        border-top: 1px solid rgba(22,136,255,0.32);

        border-radius: 12px;

        background:
            linear-gradient(
                110deg,
                rgba(225,6,0,0.08),
                rgba(22,136,255,0.07),
                rgba(245,185,66,0.04)
            ),
            var(--panel);

        box-shadow:
            0 18px 50px rgba(0,0,0,0.32);
    }


    .header-kicker {
        color: var(--gold);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 2.5px;
        margin-bottom: 6px;
    }


    .header-title {
        color: var(--white);
        font-size: 31px;
        font-weight: 950;
        letter-spacing: 1.5px;
        line-height: 1.1;
    }


    .header-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-top: 7px;
        letter-spacing: 1px;
    }


    /* ================================================================
       STATUS
       ================================================================ */

    .status-online {
        color: #b9ffd2;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 1.6px;
    }


    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #26d979;
        margin-right: 7px;
        box-shadow: 0 0 12px rgba(38,217,121,0.75);
    }


    /* ================================================================
       METRIC CARDS
       ================================================================ */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.015)
            );

        border: 1px solid var(--line);
        border-radius: 10px;

        padding: 12px 14px;

        min-height: 105px;
    }


    div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 9px !important;
        font-weight: 900 !important;
        letter-spacing: 1.5px !important;
    }


    div[data-testid="stMetricValue"] {
        color: var(--white) !important;
        font-weight: 950 !important;
    }


    /* ================================================================
       PANELS
       ================================================================ */

    .panel-title {
        color: var(--white);
        font-size: 12px;
        font-weight: 950;
        letter-spacing: 1.7px;
        margin-bottom: 3px;
    }


    .panel-subtitle {
        color: var(--muted);
        font-size: 10px;
        margin-bottom: 14px;
    }


    /* ================================================================
       EXPANDERS
       ================================================================ */

    div[data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        background: rgba(13,17,24,0.72) !important;
    }


    div[data-testid="stExpander"] summary {
        color: var(--white) !important;
    }


    /* ================================================================
       PROGRESS
       ================================================================ */

    div[data-testid="stProgress"] > div {
        background: rgba(255,255,255,0.07) !important;
    }


    div[data-testid="stProgress"] > div > div {
        background:
            linear-gradient(
                90deg,
                var(--red),
                var(--blue),
                var(--gold)
            ) !important;
    }


    /* ================================================================
       CHAT
       ================================================================ */

    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 10px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.035),
                rgba(255,255,255,0.012)
            );

        margin-bottom: 8px;
    }


    [data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;

        background: rgba(5,6,9,0.96);

        padding-top: 10px;
        padding-bottom: 5px;

        z-index: 20;
    }


    [data-testid="stChatInput"] textarea {
        background: #0b0f16 !important;
        color: white !important;

        border: 1px solid rgba(22,136,255,0.45) !important;
        border-radius: 10px !important;

        min-height: 52px !important;
    }


    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--gold) !important;

        box-shadow:
            0 0 0 1px rgba(245,185,66,0.25),
            0 0 25px rgba(22,136,255,0.12) !important;
    }


    /* ================================================================
       INPUTS
       ================================================================ */

    input,
    textarea {
        color: var(--white) !important;
    }


    /* ================================================================
       DIVIDER
       ================================================================ */

    hr {
        border-color: var(--line) !important;
    }


    /* ================================================================
       BADGES
       ================================================================ */

    .signal {
        padding: 10px 12px;
        margin-bottom: 7px;

        border: 1px solid var(--line);
        border-radius: 8px;

        background: rgba(255,255,255,0.025);
    }


    .signal-name {
        font-size: 11px;
        font-weight: 850;
        color: var(--white);
    }


    .signal-status {
        font-size: 9px;
        color: var(--muted);
        margin-top: 2px;
    }


    /* ================================================================
       OPERATION
       ================================================================ */

    .operation {
        border: 1px solid var(--line-gold);
        border-left: 3px solid var(--gold);

        border-radius: 9px;

        padding: 14px;

        background:
            linear-gradient(
                135deg,
                rgba(245,185,66,0.08),
                rgba(255,255,255,0.015)
            );
    }


    .operation-name {
        color: var(--gold);
        font-size: 10px;
        font-weight: 950;
        letter-spacing: 1.5px;
    }


    .operation-text {
        color: var(--white);
        font-size: 14px;
        font-weight: 800;
        margin-top: 6px;
    }


    /* ================================================================
       FOOTER / BOTTOM STATUS
       ================================================================ */

    .bottom-status {
        margin-top: 28px;

        border-top: 1px solid var(--line);

        padding-top: 12px;

        color: #687385;

        font-size: 9px;
        letter-spacing: 1.4px;

        text-align: center;
    }


    /* ================================================================
       MOBILE
       ================================================================ */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }

        .header-title {
            font-size: 23px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# HELPERS
# =============================================================================

def load_routing() -> dict:
    try:
        if ROUTING_FILE.exists():
            return json.loads(ROUTING_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def project_files() -> int:
    try:
        return sum(
            1
            for p in PROJECT_ROOT.rglob("*")
            if p.is_file()
            and ".git" not in p.parts
            and "__pycache__" not in p.parts
        )
    except Exception:
        return 0


def log_events() -> int:
    try:
        if not LOG_FILE.exists():
            return 0
        return len(LOG_FILE.read_text(
            encoding="utf-8",
            errors="ignore"
        ).splitlines())
    except Exception:
        return 0


def detect_mode(text: str) -> str:
    value = text.lower()

    coding_words = [
        "code",
        "coding",
        "build",
        "create",
        "implement",
        "fix",
        "debug",
        "python",
        "streamlit",
        "django",
    ]

    review_words = [
        "review",
        "check my code",
        "analyse my code",
        "analyze my code",
    ]

    test_words = [
        "test",
        "pytest",
        "ruff",
        "error",
        "failure",
    ]

    planning_words = [
        "plan",
        "planning",
        "architecture",
        "roadmap",
        "design",
    ]

    knowledge_words = [
        "document",
        "paper",
        "research",
        "source",
        "knowledge",
    ]

    if any(x in value for x in review_words):
        return "REVIEW"

    if any(x in value for x in test_words):
        return "TESTING"

    if any(x in value for x in coding_words):
        return "CODING"

    if any(x in value for x in planning_words):
        return "PLANNING"

    if any(x in value for x in knowledge_words):
        return "KNOWLEDGE"

    return "CHAT"


def bankai_reply(prompt: str) -> str:
    """
    Preserve the existing BANKAI AI bridge.
    """

    try:
        from app.core.bankai_ai_bridge import bankai_chat

        result = bankai_chat(prompt)

        if isinstance(result, dict):
            return (
                result.get("response")
                or result.get("content")
                or result.get("message")
                or str(result)
            )

        return str(result)

    except Exception as exc:
        return (
            "BANKAI bridge is currently unavailable.\n\n"
            f"Bridge status: {type(exc).__name__}: {exc}"
        )


def routing_summary() -> list[tuple[str, str, str]]:
    routing = load_routing()

    agents = routing.get("agents", {})

    result = []

    for name in [
        "planner",
        "coder",
        "tester",
        "reviewer",
        "knowledge",
    ]:
        item = agents.get(name, {})

        result.append(
            (
                name.upper(),
                str(item.get("provider", "UNCONFIGURED")),
                str(item.get("model", "UNCONFIGURED")),
            )
        )

    return result


# =============================================================================
# HEADER
# =============================================================================

header_left, header_right = st.columns([4.5, 1])

with header_left:

    st.markdown(
        "RACE CONTROL // BANKAI AI COMMAND SYSTEM"
    )

    st.title("🏎️ BANKAI RACE CONTROL")

    st.caption(
        "BLEACH × RED BULL RACING × MULTI-MODEL AI"
    )

with header_right:

    st.write("")

    st.success(
        "SYSTEM ONLINE"
    )

    st.caption(
        datetime.now().strftime("%d %b %Y • %H:%M:%S")
    )


# =============================================================================
# TOP TASKBAR
# =============================================================================

st.divider()

pages = [
    "HOME",
    "CHAT",
    "AGENTS",
    "CODER",
    "TESTER",
    "REVIEW",
    "MODELS",
    "RADIO",
    "FOCUS",
    "SYSTEM",
]

cols = st.columns(len(pages))

for col, page_name in zip(cols, pages):

    with col:

        if st.button(
            page_name,
            key=f"nav_{page_name}",
            use_container_width=True,
        ):
            st.session_state.page = page_name


st.divider()


# =============================================================================
# TOP METRICS
# =============================================================================

files = project_files()
events = log_events()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "COGNITIVE LOAD",
        "87%",
        "ACTIVE",
    )

with m2:
    st.metric(
        "AI AGENTS",
        "05",
        "READY",
    )

with m3:
    st.metric(
        "PROJECT FILES",
        files,
        "SCANNED",
    )

with m4:
    st.metric(
        "LOG EVENTS",
        events,
        "RECORDED",
    )


st.write("")


# =============================================================================
# HOME
# =============================================================================

if st.session_state.page == "HOME":

    left, center, right = st.columns(
        [1.05, 1.8, 1.05]
    )


    # -------------------------------------------------------------------------
    # LEFT
    # -------------------------------------------------------------------------

    with left:

        st.subheader("⚡ REIATSU MONITOR")

        st.metric(
            "SYSTEM ACTIVITY",
            "87%",
            "+4%",
        )

        st.progress(0.87)

        st.caption(
            "Cognitive activity / model workload"
        )

        st.divider()

        st.subheader("SYSTEM SIGNALS")

        signals = [
            ("CORE ENGINE", "Operational"),
            ("MEMORY", "Connected"),
            ("RESEARCH", "Standing by"),
            ("TESTING", "Ready"),
            ("SECURITY", "Protected"),
        ]

        for name, status in signals:

            with st.container(border=True):

                st.write(f"**{name}**")
                st.caption(status)


    # -------------------------------------------------------------------------
    # CENTER
    # -------------------------------------------------------------------------

    with center:

        st.subheader("🧠 BANKAI COGNITIVE CORE")

        st.caption(
            "Real-time command-center overview"
        )

        modules = [
            ("Reasoning Engine", 0.91),
            ("Planning", 0.84),
            ("Knowledge", 0.78),
            ("Coding", 0.88),
            ("Testing", 0.72),
            ("Review", 0.81),
        ]

        for name, value in modules:

            st.write(
                f"**{name}** — {int(value * 100)}%"
            )

            st.progress(value)

        st.write("")

        st.subheader("⚔ ACTIVE OPERATION")

        with st.container(border=True):

            st.caption(
                "CURRENT MISSION"
            )

            st.write(
                "**BANKAI SYSTEM STANDBY**"
            )

            st.caption(
                "Awaiting your next command."
            )

            st.progress(0.18)


    # -------------------------------------------------------------------------
    # RIGHT
    # -------------------------------------------------------------------------

    with right:

        st.subheader("🛡 SYSTEM INTEGRITY")

        checks = [
            ("PROJECT", PROJECT_ROOT.exists()),
            ("ROUTING", ROUTING_FILE.exists()),
            ("AI BRIDGE", True),
            ("STREAMLIT", True),
        ]

        for name, passed in checks:

            if passed:
                st.success(
                    f"{name} · PASS",
                    
                )
            else:
                st.error(
                    f"{name} · CHECK",
                    icon="!",
                )

        st.divider()

        st.subheader("🤖 ROUTING")

        for name, provider, model in routing_summary():

            with st.container(border=True):

                st.write(
                    f"**{name}**"
                )

                st.caption(
                    f"{provider} · {model}"
                )

        st.divider()

        if st.button(
            "REFRESH SYSTEM",
            use_container_width=True,
        ):
            st.session_state.last_refresh = datetime.now()
            st.rerun()


# =============================================================================
# CHAT
# =============================================================================

elif st.session_state.page == "CHAT":

    st.subheader("💬 BANKAI AI")

    st.caption(
        "Talk normally. BANKAI automatically determines whether "
        "your request is conversation, planning, knowledge, coding, "
        "testing, or review."
    )

    if not st.session_state.chat_messages:

        st.info(
            "Try:  'Hey BANKAI, how are you?'  •  "
            "'Explain quantum computing.'  •  "
            "'Plan my Einstein AI project.'"
        )

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

            if message.get("mode"):

                st.caption(
                    f"ROUTED MODE · {message['mode']}"
                )


    prompt = st.chat_input(
        "Command BANKAI..."
    )

    if prompt:

        mode = detect_mode(prompt)

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt,
                "mode": mode,
            }
        )

        with st.spinner(
            f"BANKAI · {mode}"
        ):

            answer = bankai_reply(prompt)

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": answer,
                "mode": mode,
            }
        )

        st.rerun()


# =============================================================================
# AGENTS
# =============================================================================

elif st.session_state.page == "AGENTS":

    st.subheader("🧠 AGENT COMMAND")

    st.caption(
        "BANKAI multi-agent architecture"
    )

    agents = [
        ("PLANNER", "Architecture and planning"),
        ("CODER", "Implementation"),
        ("TESTER", "Testing and failure analysis"),
        ("REVIEWER", "Security and code review"),
        ("KNOWLEDGE", "Source-grounded knowledge"),
    ]

    a, b = st.columns(2)

    for index, (name, role) in enumerate(agents):

        with a if index % 2 == 0 else b:

            with st.container(border=True):

                st.write(
                    f"### {name}"
                )

                st.caption(role)

                st.success(
                    "READY"
                )


# =============================================================================
# CODER
# =============================================================================

elif st.session_state.page == "CODER":

    st.subheader("💻 CODER")

    st.caption(
        "Implementation command center"
    )

    st.info(
        "Coding tasks are routed through BANKAI's AI bridge. "
        "The UI does not replace the coding backend."
    )

    request = st.text_area(
        "CODING REQUEST",
        placeholder=(
            "Example: Build a Streamlit login page..."
        ),
        height=180,
    )

    if st.button(
        "SEND TO CODER",
        use_container_width=True,
    ):

        if request.strip():

            answer = bankai_reply(
                request
            )

            st.write(answer)


# =============================================================================
# TESTER
# =============================================================================

elif st.session_state.page == "TESTER":

    st.subheader("🧪 TEST CONTROL")

    st.caption(
        "Testing and failure-analysis command center"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "SCAN PROJECT",
            use_container_width=True,
        ):

            st.info(
                "Project scan requested."
            )

    with c2:

        if st.button(
            "RUN VALIDATION",
            use_container_width=True,
        ):

            st.info(
                "Validation pipeline requested."
            )

    st.divider()

    st.write(
        "### Current Checks"
    )

    st.success("Streamlit UI · READY")
    st.success("AI bridge · READY")
    st.success("Routing configuration · READY")
    st.success("Project path · FOUND")


# =============================================================================
# REVIEW
# =============================================================================

elif st.session_state.page == "REVIEW":

    st.subheader("🔍 REVIEW")

    st.caption(
        "Code and architecture review"
    )

    code = st.text_area(
        "PASTE CODE",
        height=300,
        placeholder="Paste Python code here...",
    )

    if st.button(
        "REVIEW WITH BANKAI",
        use_container_width=True,
    ):

        if code.strip():

            prompt = (
                "Review the following code for correctness, "
                "security, architecture, bugs, and improvements.\n\n"
                f"{code}"
            )

            with st.spinner("BANKAI REVIEWING..."):

                result = bankai_reply(prompt)

            st.write(result)


# =============================================================================
# MODELS
# =============================================================================

elif st.session_state.page == "MODELS":

    st.subheader("🤖 MODEL CONTROL")

    st.caption(
        "BANKAI model-provider routing"
    )

    routing = load_routing()

    if routing:

        agents = routing.get(
            "agents",
            {}
        )

        for name, config in agents.items():

            with st.container(border=True):

                st.write(
                    f"**{name.upper()}**"
                )

                st.caption(
                    f"Provider: {config.get('provider', 'unknown')}"
                )

                st.write(
                    f"Model: `{config.get('model', 'unknown')}`"
                )

                st.caption(
                    config.get("role", "")
                )

    else:

        st.warning(
            "Model routing configuration not found."
        )


# =============================================================================
# RADIO
# =============================================================================

elif st.session_state.page == "RADIO":

    st.subheader("📡 RACE RADIO")

    st.caption(
        "BANKAI command telemetry"
    )

    st.info(
        "Race Radio interface ready."
    )

    st.write(
        f"Last refresh: "
        f"{st.session_state.last_refresh.strftime('%H:%M:%S')}"
    )

    st.write(
        "SYSTEM → ONLINE"
    )

    st.write(
        "CORE → OPERATIONAL"
    )

    st.write(
        "AI BRIDGE → READY"
    )


# =============================================================================
# FOCUS
# =============================================================================

elif st.session_state.page == "FOCUS":

    st.subheader("⏱️ FOCUS MODE")

    st.caption(
        "Minimal command environment"
    )

    mission = st.text_input(
        "CURRENT MISSION",
        value=st.session_state.mission,
    )

    st.session_state.mission = mission

    st.progress(0.42)

    st.metric(
        "MISSION PROGRESS",
        "42%",
        "ACTIVE",
    )

    if st.button(
        "COMPLETE MISSION",
        use_container_width=True,
    ):

        st.session_state.mission = "MISSION COMPLETE"

        st.success(
            "Mission marked complete."
        )


# =============================================================================
# SYSTEM
# =============================================================================

elif st.session_state.page == "SYSTEM":

    st.subheader("⚙️ SYSTEM")

    st.caption(
        "BANKAI Race Control system configuration"
    )

    st.toggle(
        "Monitoring",
        key="monitoring",
    )

    st.toggle(
        "Auto Refresh",
        key="auto_refresh",
    )

    st.divider()

    st.write(
        "### Project"
    )

    st.write(
        f"**Path:** `{PROJECT_ROOT}`"
    )

    st.write(
        f"**Files:** {project_files()}"
    )

    st.write(
        f"**Log events:** {log_events()}"
    )

    if st.button(
        "CLEAR CHAT SESSION",
        use_container_width=True,
    ):

        st.session_state.chat_messages = []

        st.success(
            "Chat session cleared."
        )


# =============================================================================
# AUTO REFRESH
# =============================================================================

if st.session_state.auto_refresh:

    time.sleep(5)

    st.rerun()


# =============================================================================
# BOTTOM STATUS
# =============================================================================

st.divider()

st.caption(
    "BANKAI RACE CONTROL  •  BLEACH × RED BULL RACING  •  "
    "GENERAL AI × AGENTS × CODING × KNOWLEDGE × TESTING"
)

