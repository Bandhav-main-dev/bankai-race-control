
from pathlib import Path
from datetime import datetime
import json
import time

import streamlit as st


# ============================================================
# ⚔️ BANKAI RACE CONTROL
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
AUDIO = DATA / "audio"

PROJECTS_FILE = DATA / "projects.json"
STATUS_FILE = DATA / "status.json"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="BANKAI RACE CONTROL",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_json(path, default):

    try:

        if not path.exists():
            return default

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return default


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


projects_data = load_json(
    PROJECTS_FILE,
    {"projects": []},
)

projects = projects_data.get(
    "projects",
    [],
)

if not projects:

    projects = [
        {
            "name": "Einstein AI V2",
            "progress": 0,
            "status": "UNKNOWN",
            "phase": "Unknown",
            "health": "UNKNOWN",
            "priority": "HIGH",
            "technology": "AI",
            "description": "AI monitoring target.",
            "mission": "Continue development.",
            "next_operation": "Continue development.",
        }
    ]


status = load_json(
    STATUS_FILE,
    {},
)

if not isinstance(status, dict):
    status = {}


# ============================================================
# MODES
# ============================================================

MODES = [
    "🟢 GREEN FLAG",
    "🔵 QUALIFYING",
    "🔴 ATTACK MODE",
    "🟡 CAUTION",
    "⚫ PIT MODE",
    "🔵 RESEARCH MODE",
    "⚔️ BANKAI MODE",
]


# ============================================================
# STATUS NORMALIZATION
# ============================================================

project_names = [
    project["name"]
    for project in projects
]

if status.get(
    "selected_project"
) not in project_names:

    status["selected_project"] = (
        project_names[0]
    )


if status.get("mode") not in MODES:
    status["mode"] = MODES[0]


status.setdefault(
    "current_lap",
    1,
)

status.setdefault(
    "target_lap",
    10,
)

status.setdefault(
    "session_seconds",
    0,
)

status.setdefault(
    "session_running",
    False,
)

status.setdefault(
    "last_radio",
    "RACE CONTROL → SYSTEM: Telemetry online.",
)

status.setdefault(
    "radio_history",
    [],
)

status.setdefault(
    "last_audio",
    "",
)


# ============================================================
# HELPERS
# ============================================================

def selected_project():

    for project in projects:

        if project["name"] == status[
            "selected_project"
        ]:

            return project

    return projects[0]


def update_status():

    status["last_updated"] = (
        datetime.now().isoformat()
    )

    save_json(
        STATUS_FILE,
        status,
    )


def play_audio(
    filename,
    message=None,
):

    audio_path = AUDIO / filename

    if audio_path.exists():

        with audio_path.open("rb") as audio:

            st.audio(
                audio.read(),
                format="audio/wav",
            )

    if message:

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

    status["last_audio"] = filename

    update_status()


def select_project(name):

    status["selected_project"] = name

    project = next(
        (
            item
            for item in projects
            if item["name"] == name
        ),
        None,
    )

    if project:

        status["last_radio"] = (
            "RACE CONTROL → SYSTEM: "
            f"{name} selected for monitoring."
        )

        status["radio_history"].insert(
            0,
            {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "message": status["last_radio"],
            },
        )

    update_status()


project = selected_project()


# ============================================================
# HEADER
# ============================================================

st.title("⚔️ BANKAI RACE CONTROL")

st.caption(
    "AI MONITORING SYSTEM  •  "
    "BLEACH × F1  •  "
    "TELEMETRY COMMAND"
)

st.divider()


# ============================================================
# SYSTEM HEADER
# ============================================================

header1, header2, header3 = st.columns(
    [2, 2, 1]
)

with header1:

    st.subheader(
        "🏎️ AI RACE CONTROL"
    )

    st.write(
        f"**MONITORING:** "
        f"{project['name']}"
    )

with header2:

    mode = st.selectbox(
        "⚙️ OPERATING MODE",
        MODES,
        index=MODES.index(
            status["mode"]
        ),
    )

    if mode != status["mode"]:

        status["mode"] = mode

        if mode == "⚔️ BANKAI MODE":

            play_audio(
                "bankai.wav",
                "⚔️ RACE CONTROL → SYSTEM: BANKAI ACTIVATED.",
            )

        elif mode == "🔴 ATTACK MODE":

            play_audio(
                "attack_mode.wav",
                "🔴 RACE CONTROL → SYSTEM: ATTACK MODE.",
            )

        elif mode == "🟡 CAUTION":

            play_audio(
                "warning.wav",
                "🟡 RACE CONTROL → SYSTEM: CAUTION.",
            )

        elif mode == "🔵 QUALIFYING":

            play_audio(
                "qualifying.wav",
                "🔵 RACE CONTROL → SYSTEM: QUALIFYING.",
            )

        else:

            play_audio(
                "button.wav",
                f"RACE CONTROL → SYSTEM: {mode}.",
            )

with header3:

    st.metric(
        "⚡ REIATSU",
        f"{project.get('progress', 0)}%",
    )


# ============================================================
# SIDEBAR AI GRID
# ============================================================

with st.sidebar:

    st.title("⚔️ AI GRID")

    st.caption(
        "SELECT SYSTEM TO MONITOR"
    )

    st.divider()

    for item in projects:

        is_selected = (
            item["name"]
            == project["name"]
        )

        if is_selected:

            label = (
                f"🔴 {item['name']}"
            )

        else:

            label = (
                f"⚪ {item['name']}"
            )

        if st.button(
            label,
            key=f"project_{item['name']}",
            use_container_width=True,
        ):

            select_project(
                item["name"]
            )

            play_audio(
                "button.wav"
            )

            st.rerun()

        st.caption(
            f"{item.get('status', 'UNKNOWN')} "
            f"• {item.get('progress', 0)}%"
        )

    st.divider()

    st.caption("RACE CONTROL")

    st.write("🟢 TELEMETRY ONLINE")
    st.write("🔵 AI CORE ONLINE")
    st.write("⚔️ BANKAI CORE READY")


# ============================================================
# HERO
# ============================================================

st.subheader(
    f"🏁 {project['name']}"
)

st.write(
    project.get(
        "description",
        "AI project under monitoring.",
    )
)

st.divider()


# ============================================================
# PROJECT STATUS
# ============================================================

st.subheader(
    "📡 PROJECT TELEMETRY"
)

status1, status2, status3, status4 = st.columns(
    4
)

with status1:

    st.metric(
        "STATUS",
        project.get(
            "status",
            "UNKNOWN",
        ),
    )

with status2:

    st.metric(
        "PHASE",
        project.get(
            "phase",
            "UNKNOWN",
        ),
    )

with status3:

    st.metric(
        "HEALTH",
        project.get(
            "health",
            "UNKNOWN",
        ),
    )

with status4:

    st.metric(
        "PRIORITY",
        project.get(
            "priority",
            "MEDIUM",
        ),
    )


# ============================================================
# REIATSU
# ============================================================

st.divider()

st.subheader(
    "⚡ REIATSU / DEVELOPMENT POWER"
)

progress = int(
    project.get(
        "progress",
        0,
    )
)

st.progress(
    progress / 100
)

st.caption(
    f"{progress}% SYSTEM DEVELOPMENT"
)


# ============================================================
# MONITORING CORES
# ============================================================

st.divider()

st.subheader(
    "🧠 AI CORE MONITORING"
)

core1, core2, core3 = st.columns(3)

with core1:

    with st.container(border=True):

        st.subheader(
            "📚 KNOWLEDGE CORE"
        )

        st.success(
            "ONLINE"
        )

        st.caption(
            "Scientific knowledge and data layer"
        )

with core2:

    with st.container(border=True):

        st.subheader(
            "🧠 COGNITIVE CORE"
        )

        st.success(
            "ONLINE"
        )

        st.caption(
            "Cognitive architecture monitoring"
        )

with core3:

    with st.container(border=True):

        st.subheader(
            "⚡ REASONING CORE"
        )

        st.info(
            project.get(
                "phase",
                "READY",
            )
        )

        st.caption(
            "Current AI reasoning subsystem"
        )


# ============================================================
# PROJECT INTELLIGENCE
# ============================================================

st.divider()

st.subheader(
    "🔎 SYSTEM INTELLIGENCE"
)

info1, info2 = st.columns(2)

with info1:

    st.write(
        f"**Repository:** "
        f"{project.get('repository', 'N/A')}"
    )

    st.write(
        f"**Technology:** "
        f"{project.get('technology', 'AI')}"
    )

    st.write(
        f"**Health:** "
        f"{project.get('health', 'UNKNOWN')}"
    )

with info2:

    st.write(
        "**CURRENT MISSION**"
    )

    st.info(
        project.get(
            "mission",
            "Continue development.",
        )
    )

    st.write(
        "**NEXT OPERATION**"
    )

    st.warning(
        project.get(
            "next_operation",
            "Continue development.",
        )
    )


# ============================================================
# SESSION CONTROL
# ============================================================

st.divider()

st.subheader(
    "🏎️ DEVELOPMENT SESSION"
)

session1, session2, session3, session4 = st.columns(
    4
)

with session1:

    st.metric(
        "LAP",
        f"{status['current_lap']} / "
        f"{status['target_lap']}",
    )

with session2:

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

with session3:

    if status["session_running"]:

        st.success(
            "🟢 SESSION RUNNING"
        )

    else:

        st.info(
            "⚫ SESSION STOPPED"
        )

with session4:

    st.metric(
        "MODE",
        status["mode"],
    )


# ============================================================
# SESSION BUTTONS
# ============================================================

start_col, stop_col, lap_col, reset_col = st.columns(
    4
)

with start_col:

    if st.button(
        "▶️ START SESSION",
        use_container_width=True,
    ):

        status["session_running"] = True

        play_audio(
            "race_start.wav",
            (
                "RACE CONTROL → SYSTEM: "
                f"{project['name']} development session started."
            ),
        )

        st.rerun()


with stop_col:

    if st.button(
        "🛑 STOP SESSION",
        use_container_width=True,
    ):

        status["session_running"] = False

        play_audio(
            "stop.wav",
            "RACE CONTROL → SYSTEM: DEVELOPMENT SESSION STOPPED.",
        )

        st.rerun()


with lap_col:

    if st.button(
        "🏁 NEXT LAP",
        use_container_width=True,
    ):

        status["current_lap"] += 1

        play_audio(
            "lap.wav",
            (
                "RACE CONTROL → SYSTEM: "
                f"LAP {status['current_lap']} COMPLETE."
            ),
        )

        st.rerun()


with reset_col:

    if st.button(
        "🔄 RESET",
        use_container_width=True,
    ):

        status["session_running"] = False
        status["session_seconds"] = 0
        status["current_lap"] = 1

        play_audio(
            "button.wav",
            "RACE CONTROL → SYSTEM: SESSION RESET.",
        )

        st.rerun()


# ============================================================
# MOTIVATIONAL COMMAND
# ============================================================

st.divider()

st.subheader(
    "🏆 MOTIVATIONAL COMMAND"
)

motivation_left, motivation_right = st.columns(
    [2, 1]
)

motivational_lines = [
    (
        "FOCUS",
        "Keep your eyes on the target. "
        "The next lap is the only lap that matters.",
    ),
    (
        "DISCIPLINE",
        "Build the system one verified step at a time.",
    ),
    (
        "PRESSURE",
        "When the pressure rises, precision matters more.",
    ),
    (
        "LIMIT",
        "Find the performance that is still available.",
    ),
    (
        "BANKAI",
        "Release the next level only when the foundation is ready.",
    ),
]

quote_index = (
    progress
    + int(status["current_lap"])
) % len(motivational_lines)

title, message = motivational_lines[
    quote_index
]

with motivation_left:

    with st.container(border=True):

        st.subheader(
            f"⚔️ {title}"
        )

        st.write(
            message
        )

        st.caption(
            "MAX-INSPIRED ORIGINAL MOTIVATIONAL MESSAGE"
        )

with motivation_right:

    st.metric(
        "MENTAL STATE",
        "LOCKED IN",
    )

    st.metric(
        "MISSION",
        "PUSH",
    )


# ============================================================
# CURRENT SYSTEM MODE
# ============================================================

st.divider()

st.subheader(
    "⚙️ CURRENT SYSTEM MODE"
)

if status["mode"] == "⚔️ BANKAI MODE":

    st.success(
        "⚔️ BANKAI MODE — SYSTEM OPERATING BEYOND NORMAL DEVELOPMENT STATE."
    )

elif status["mode"] == "🔴 ATTACK MODE":

    st.error(
        "🔴 ATTACK MODE — DEVELOPMENT PUSH ACTIVE."
    )

elif status["mode"] == "🟡 CAUTION":

    st.warning(
        "🟡 CAUTION — SYSTEM REQUIRES ATTENTION."
    )

elif status["mode"] == "🔵 QUALIFYING":

    st.info(
        "🔵 QUALIFYING — PERFORMANCE AND VALIDATION RUN."
    )

else:

    st.info(
        f"{status['mode']} — SYSTEM READY."
    )


# ============================================================
# SYSTEM AUDIO
# ============================================================

st.divider()

st.subheader(
    "🔊 RACE CONTROL AUDIO"
)

audio_col1, audio_col2, audio_col3 = st.columns(
    3
)

audio_buttons = [
    (
        audio_col1,
        "🏁 START AUDIO",
        "race_start.wav",
    ),
    (
        audio_col2,
        "⚔️ BANKAI AUDIO",
        "bankai.wav",
    ),
    (
        audio_col3,
        "🔴 ATTACK AUDIO",
        "attack_mode.wav",
    ),
]


for column, label, filename in audio_buttons:

    with column:

        if st.button(
            label,
            key=f"audio_{filename}",
            use_container_width=True,
        ):

            play_audio(
                filename
            )


# ============================================================
# LAST RADIO / EVENT
# ============================================================

st.divider()

st.subheader(
    "📻 LAST SYSTEM TRANSMISSION"
)

st.info(
    status["last_radio"]
)


# ============================================================
# EVENT LOG
# ============================================================

with st.expander(
    "📡 RACE CONTROL EVENT LOG"
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
# TIMER
# ============================================================

if status["session_running"]:

    status["session_seconds"] = (
        int(
            status.get(
                "session_seconds",
                0,
            )
        )
        + 1
    )

    update_status()

    time.sleep(1)

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "⚔️ BANKAI RACE CONTROL  •  "
    "AI MONITORING SYSTEM  •  "
    "EINSTEIN AI  •  "
    "TELEMETRY ONLINE"
)
