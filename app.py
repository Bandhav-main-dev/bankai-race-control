
from pathlib import Path
from datetime import datetime
import json
import time

import streamlit as st


# ============================================================
# BANKAI RACE CONTROL
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

PROJECTS_FILE = DATA / "projects.json"
STATUS_FILE = DATA / "status.json"


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="BANKAI RACE CONTROL",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# NATIVE STREAMLIT THEME
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
    }

    [data-testid="stSidebar"] {
        background-color: #070b14;
        border-right: 1px solid #D4AF37;
    }

    .stButton > button {
        border: 1px solid #D4AF37;
        border-radius: 7px;
        background-color: #080d18;
        color: white;
        min-height: 42px;
    }

    .stButton > button:hover {
        border-color: #E10600;
        color: #D4AF37;
    }

    [data-testid="stMetric"] {
        background-color: #080d18;
        border: 1px solid #1d3557;
        border-radius: 8px;
        padding: 12px;
    }

    .stProgress > div > div > div > div {
        background-color: #E10600;
    }

    h1 {
        color: #FFFFFF;
    }

    h2, h3 {
        color: #D4AF37;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

DEFAULT_PROJECTS = [
    {
        "name": "Einstein AI V2",
        "repository": "Einstain-ai-brain-v2",
        "progress": 82,
        "status": "ACTIVE",
        "phase": "Reasoning Engine",
        "technology": "Python • AI • Machine Learning",
        "priority": "CRITICAL",
        "description": "Einstein-inspired AI reasoning system.",
        "health": "OPTIMAL",
        "mission": "Develop and validate the reasoning engine.",
    }
]


def load_json(path, default):
    try:
        if not path.exists():
            return default

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def get_projects():
    data = load_json(
        PROJECTS_FILE,
        {"projects": DEFAULT_PROJECTS},
    )

    if isinstance(data, dict):
        projects = data.get("projects", [])
    elif isinstance(data, list):
        projects = data
    else:
        projects = []

    if not projects:
        projects = DEFAULT_PROJECTS

    return [
        project
        for project in projects
        if isinstance(project, dict)
        and project.get("name")
    ]


projects = get_projects()

project_names = [
    project["name"]
    for project in projects
]


# ============================================================
# STATUS
# ============================================================

status = load_json(
    STATUS_FILE,
    {},
)

if not isinstance(status, dict):
    status = {}

if status.get("selected_project") not in project_names:
    status["selected_project"] = project_names[0]

modes = [
    "🟢 GREEN FLAG",
    "🔵 QUALIFYING",
    "🔴 ATTACK MODE",
    "🟡 CAUTION",
    "⚫ PIT MODE",
    "🔵 RESEARCH MODE",
    "⚔️ BANKAI MODE",
]

if status.get("mode") not in modes:
    status["mode"] = modes[0]

status.setdefault("current_lap", 1)
status.setdefault("target_lap", 10)
status.setdefault("session_seconds", 0)
status.setdefault("session_running", False)
status.setdefault(
    "driver_message",
    "Telemetry online.",
)
status.setdefault(
    "team_message",
    "Race Control ready.",
)
status.setdefault(
    "last_radio",
    "TEAM → DRIVER: Telemetry online.",
)
status.setdefault("radio_history", [])


# ============================================================
# PROJECT HELPERS
# ============================================================

def get_selected_project():
    for project in projects:
        if project["name"] == status["selected_project"]:
            return project

    return projects[0]


def change_project(name):
    status["selected_project"] = name
    status["last_updated"] = datetime.now().isoformat()

    selected = get_selected_project()

    status["last_radio"] = (
        f"RACE CONTROL → SYSTEM: "
        f"{selected['name']} selected for monitoring."
    )

    history = status.get("radio_history", [])

    history.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": status["last_radio"],
        },
    )

    status["radio_history"] = history[:20]

    save_json(
        STATUS_FILE,
        status,
    )


selected = get_selected_project()


# ============================================================
# HEADER
# ============================================================

st.title("⚔️ BANKAI RACE CONTROL")

st.caption(
    "AI MONITORING SYSTEM  •  BLEACH × F1 COMMAND CENTER"
)

st.divider()


# ============================================================
# TOP CONTROL
# ============================================================

left, middle, right = st.columns(
    [2, 2, 1]
)

with left:
    st.subheader("🏎️ RACE CONTROL")

    st.write(
        f"**SYSTEM:** {selected['name']}"
    )

with middle:

    current_mode = st.selectbox(
        "⚙️ SYSTEM MODE",
        modes,
        index=modes.index(status["mode"]),
    )

    if current_mode != status["mode"]:

        status["mode"] = current_mode
        status["last_updated"] = datetime.now().isoformat()

        if current_mode == "⚔️ BANKAI MODE":
            status["last_radio"] = (
                "RACE CONTROL → SYSTEM: "
                "BANKAI SEQUENCE ACTIVATED."
            )

        save_json(
            STATUS_FILE,
            status,
        )

with right:

    st.metric(
        "REIATSU",
        f"{selected.get('progress', 0)}%",
    )


# ============================================================
# SIDEBAR PROJECT SELECTOR
# ============================================================

with st.sidebar:

    st.title("⚔️ AI GRID")

    st.caption(
        "SELECT AN AI SYSTEM TO MONITOR"
    )

    st.divider()

    for project in projects:

        selected_project = (
            project["name"]
            == selected["name"]
        )

        if selected_project:
            label = (
                f"🔴 {project['name']}"
            )
        else:
            label = (
                f"⚪ {project['name']}"
            )

        if st.button(
            label,
            key=f"select_{project['name']}",
            use_container_width=True,
        ):
            change_project(project["name"])
            st.rerun()

        st.caption(
            f"{project.get('status', 'UNKNOWN')} "
            f"• {project.get('progress', 0)}%"
        )

    st.divider()

    st.caption("SYSTEM STATUS")

    st.write("🟢 RACE CONTROL — ONLINE")
    st.write("🔵 TELEMETRY — ONLINE")
    st.write("⚔️ BANKAI CORE — STANDBY")


# ============================================================
# SELECTED PROJECT
# ============================================================

st.subheader(
    f"🏁 {selected['name']}"
)

st.write(
    selected.get(
        "description",
        "AI project under monitoring.",
    )
)


# ============================================================
# PROJECT STATUS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "STATUS",
        selected.get("status", "UNKNOWN"),
    )

with c2:
    st.metric(
        "PHASE",
        selected.get("phase", "UNKNOWN"),
    )

with c3:
    st.metric(
        "HEALTH",
        selected.get("health", "UNKNOWN"),
    )

with c4:
    st.metric(
        "PRIORITY",
        selected.get("priority", "MEDIUM"),
    )


# ============================================================
# REIATSU
# ============================================================

st.divider()

st.subheader("⚡ REIATSU / PROJECT POWER")

progress = int(
    selected.get("progress", 0)
)

st.progress(
    progress / 100
)

st.write(
    f"**{progress}%** — project development power"
)


# ============================================================
# LIVE MONITORING
# ============================================================

st.divider()

st.subheader("📡 LIVE MONITORING")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "KNOWLEDGE CORE",
        "ONLINE",
    )

with m2:
    st.metric(
        "COGNITIVE CORE",
        "ONLINE",
    )

with m3:
    st.metric(
        "REASONING CORE",
        selected.get(
            "phase",
            "READY",
        ),
    )

with m4:
    st.metric(
        "TELEMETRY",
        "LIVE",
    )


# ============================================================
# PROJECT INFORMATION
# ============================================================

st.divider()

st.subheader(
    "📋 SYSTEM INTELLIGENCE"
)

tab1, tab2, tab3 = st.tabs(
    [
        "PROJECT STATUS",
        "CURRENT MISSION",
        "SYSTEM TELEMETRY",
    ]
)

with tab1:

    st.write(
        f"**Project:** {selected['name']}"
    )

    st.write(
        f"**Repository:** "
        f"{selected.get('repository', 'N/A')}"
    )

    st.write(
        f"**Technology:** "
        f"{selected.get('technology', 'AI')}"
    )

    st.write(
        f"**Status:** "
        f"{selected.get('status', 'UNKNOWN')}"
    )

    st.write(
        f"**Current Phase:** "
        f"{selected.get('phase', 'UNKNOWN')}"
    )

    st.write(
        f"**Priority:** "
        f"{selected.get('priority', 'MEDIUM')}"
    )

    st.write(
        f"**Progress:** {progress}%"
    )

with tab2:

    st.success(
        selected.get(
            "mission",
            "Continue AI development.",
        )
    )

    st.write(
        "**NEXT OPERATION**"
    )

    st.write(
        "Continue the current AI subsystem, "
        "validate the next milestone and "
        "maintain system telemetry."
    )

with tab3:

    telemetry = {
        "Subsystem": [
            "Knowledge",
            "Cognition",
            "Reasoning",
            "Monitoring",
            "Evaluation",
            "Race Control",
        ],
        "State": [
            "ONLINE",
            "ONLINE",
            "ACTIVE",
            "ONLINE",
            "READY",
            "ONLINE",
        ],
    }

    st.dataframe(
        telemetry,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RACE SESSION
# ============================================================

st.divider()

st.subheader("🏎️ AI DEVELOPMENT SESSION")

lap1, lap2, lap3 = st.columns(3)

with lap1:

    lap = st.number_input(
        "CURRENT LAP",
        min_value=1,
        max_value=999,
        value=int(status["current_lap"]),
    )

    if lap != status["current_lap"]:
        status["current_lap"] = lap
        save_json(
            STATUS_FILE,
            status,
        )

with lap2:

    seconds = int(
        status.get(
            "session_seconds",
            0,
        )
    )

    minutes = seconds // 60
    remaining = seconds % 60

    st.metric(
        "SESSION TIME",
        f"{minutes:02d}:{remaining:02d}",
    )

with lap3:

    if st.button(
        "▶️ START SESSION",
        use_container_width=True,
    ):

        status["session_running"] = True

        status["last_radio"] = (
            f"RACE CONTROL → {selected['name']}: "
            "Development session started."
        )

        save_json(
            STATUS_FILE,
            status,
        )

        st.rerun()


# ============================================================
# RADIO
# ============================================================

st.divider()

st.subheader("📻 TEAM RADIO")

radio1, radio2 = st.columns(2)

with radio1:

    driver = st.text_input(
        "DRIVER → TEAM",
        value=status["driver_message"],
    )

    if st.button(
        "📡 SEND DRIVER RADIO",
        use_container_width=True,
    ):

        message = (
            f"DRIVER → TEAM: {driver}"
        )

        status["driver_message"] = driver
        status["last_radio"] = message

        history = status.get(
            "radio_history",
            [],
        )

        history.insert(
            0,
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "message": message,
            },
        )

        status["radio_history"] = history[:20]

        save_json(
            STATUS_FILE,
            status,
        )

        st.success(
            "Driver transmission sent."
        )

with radio2:

    team = st.text_input(
        "TEAM → DRIVER",
        value=status["team_message"],
    )

    if st.button(
        "📡 SEND TEAM RADIO",
        use_container_width=True,
    ):

        message = (
            f"TEAM → DRIVER: {team}"
        )

        status["team_message"] = team
        status["last_radio"] = message

        history = status.get(
            "radio_history",
            [],
        )

        history.insert(
            0,
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "message": message,
            },
        )

        status["radio_history"] = history[:20]

        save_json(
            STATUS_FILE,
            status,
        )

        st.success(
            "Team transmission sent."
        )


st.info(
    f"📻 {status['last_radio']}"
)


# ============================================================
# MOTIVATION
# ============================================================

st.divider()

st.subheader("🏆 DRIVER MINDSET")

messages = [
    "No excuses. Find the limit.",
    "Stay focused. Keep pushing.",
    "One lap at a time.",
    "Find the performance that is still available.",
    "Pressure creates performance.",
    "Keep the system clean. Keep the mind clear.",
]

message_index = (
    progress + int(status["current_lap"])
) % len(messages)

st.info(
    messages[message_index]
)

st.caption(
    "Original Max-inspired motivational messages; "
    "not presented as verified Max Verstappen quotations."
)


# ============================================================
# BANKAI STATE
# ============================================================

st.divider()

st.subheader("⚔️ BANKAI CORE")

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.metric(
        "SHIKAI",
        "ACTIVE",
    )

with b2:
    st.metric(
        "REIATSU",
        f"{progress}%",
    )

with b3:
    st.metric(
        "BANKAI",
        "READY",
    )

with b4:
    st.metric(
        "RACE CONTROL",
        "ONLINE",
    )


# ============================================================
# AUDIO
# ============================================================

st.divider()

st.subheader("🔊 SYSTEM AUDIO")

audio_dir = DATA / "audio"

audio_items = [
    (
        "🏁 RACE START",
        audio_dir / "race_start.wav",
    ),
    (
        "⚔️ BANKAI",
        audio_dir / "bankai.wav",
    ),
    (
        "🔴 ATTACK MODE",
        audio_dir / "attack_mode.wav",
    ),
    (
        "🟡 WARNING",
        audio_dir / "warning.wav",
    ),
    (
        "📻 DRIVER RADIO",
        audio_dir / "driver_radio.wav",
    ),
    (
        "📻 TEAM RADIO",
        audio_dir / "team_radio.wav",
    ),
]

available = [
    item
    for item in audio_items
    if item[1].exists()
]

if available:

    audio_columns = st.columns(3)

    for index, (name, path) in enumerate(
        available
    ):

        with audio_columns[index % 3]:

            st.caption(name)

            with path.open("rb") as audio:
                st.audio(
                    audio.read(),
                    format="audio/wav",
                )

else:

    st.caption(
        "Audio modules will appear here when WAV "
        "files are added to data/audio/."
    )


# ============================================================
# RADIO HISTORY
# ============================================================

st.divider()

with st.expander(
    "📻 RACE CONTROL EVENT LOG"
):

    history = status.get(
        "radio_history",
        [],
    )

    if history:

        for event in history[:15]:

            st.write(
                f"**[{event['time']}]** "
                f"{event['message']}"
            )

    else:

        st.caption(
            "No events recorded."
        )


# ============================================================
# SESSION UPDATE
# ============================================================

if status.get("session_running"):

    status["session_seconds"] = (
        int(status.get("session_seconds", 0))
        + 1
    )

    status["last_updated"] = (
        datetime.now().isoformat()
    )

    save_json(
        STATUS_FILE,
        status,
    )

    time.sleep(1)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚔️ BANKAI RACE CONTROL  •  "
    "AI MONITORING SYSTEM  •  "
    "TELEMETRY ONLINE"
)
