import json
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st


# ================================================================
# BANKAI RACE CONTROL
# ================================================================

st.set_page_config(
    page_title="BANKAI RACE CONTROL",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
AUDIO = DATA / "audio"
PROJECTS_FILE = DATA / "projects.json"
STATUS_FILE = DATA / "status.json"


# ================================================================
# JSON
# ================================================================

def load_json(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def save_json(path, data):
    path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )


projects = load_json(PROJECTS_FILE, [])

status = load_json(
    STATUS_FILE,
    {
        "selected_project": "Einstein AI V2",
        "mode": "🟢 GREEN FLAG",
        "current_lap": 1,
        "target_lap": 10,
        "session_seconds": 0,
        "session_running": False,
        "radio_history": [],
        "ai_messages": []
    }
)


# ================================================================
# PROJECT
# ================================================================

def get_project(name):
    for project in projects:
        if project.get("name") == name:
            return project

    if projects:
        return projects[0]

    return {
        "name": "Unknown AI",
        "status": "UNKNOWN",
        "phase": "UNKNOWN",
        "health": "UNKNOWN",
        "priority": "UNKNOWN",
        "progress": 0,
        "technology": "Unknown",
        "repository": "Unknown",
        "mission": "No mission.",
        "next_operation": "No operation."
    }


selected_project = get_project(
    status.get("selected_project", "Einstein AI V2")
)


# ================================================================
# EVENTS
# ================================================================

def log_event(message):
    history = status.setdefault("radio_history", [])

    history.insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message
        }
    )

    status["radio_history"] = history[:30]
    status["last_radio"] = message
    status["last_updated"] = datetime.now().isoformat()

    save_json(STATUS_FILE, status)


# ================================================================
# AUDIO
# ================================================================

def play_audio(filename, message=None):
    path = AUDIO / filename

    if path.exists():
        st.audio(str(path), format="audio/wav")

    status["last_audio"] = filename

    if message:
        log_event(message)

    save_json(STATUS_FILE, status)


# ================================================================
# OMNIROUTE
# ================================================================

def check_omniroute():
    url = st.session_state.get(
        "omniroute_url",
        "http://localhost:20128/v1"
    )

    try:
        response = requests.get(
            url.rstrip("/") + "/models",
            timeout=2
        )
        return response.ok
    except Exception:
        return False


def ask_bankai_ai(question):
    from openai import OpenAI

    base_url = st.session_state.get(
        "omniroute_url",
        "http://localhost:20128/v1"
    )

    model = st.session_state.get(
        "omniroute_model",
        "auto"
    )

    api_key = st.session_state.get(
        "omniroute_key",
        ""
    ) or "omniroute"

    system_prompt = (
        "You are BANKAI AI, the AI race engineer inside "
        "BANKAI RACE CONTROL.\n\n"
        "Current project: " + str(selected_project.get("name")) + "\n"
        "Status: " + str(selected_project.get("status")) + "\n"
        "Phase: " + str(selected_project.get("phase")) + "\n"
        "Health: " + str(selected_project.get("health")) + "\n"
        "Priority: " + str(selected_project.get("priority")) + "\n"
        "Progress: " + str(selected_project.get("progress")) + "%\n"
        "Technology: " + str(selected_project.get("technology")) + "\n"
        "Mission: " + str(selected_project.get("mission")) + "\n"
        "Next operation: " + str(selected_project.get("next_operation")) + "\n\n"
        "Current mode: " + str(status.get("mode")) + "\n"
        "Current lap: " + str(status.get("current_lap")) + "/" + str(status.get("target_lap")) + "\n\n"
        "Give practical technical recommendations. "
        "Never invent telemetry. "
        "Separate known facts from recommendations."
    )

    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# ================================================================
# SESSION STATE
# ================================================================

if "omniroute_url" not in st.session_state:
    st.session_state.omniroute_url = "http://localhost:20128/v1"

if "omniroute_model" not in st.session_state:
    st.session_state.omniroute_model = "auto"

if "omniroute_key" not in st.session_state:
    st.session_state.omniroute_key = ""

if "last_ai_question" not in st.session_state:
    st.session_state.last_ai_question = ""

if "last_ai_response" not in st.session_state:
    st.session_state.last_ai_response = ""

if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()


# ================================================================
# HEADER
# ================================================================

st.title("⚔️ BANKAI RACE CONTROL")

st.caption(
    "AI MONITORING SYSTEM • BLEACH × F1 • "
    "RACE ENGINEERING COMMAND CENTER"
)

st.divider()


# ================================================================
# TOP TELEMETRY
# ================================================================

a, b, c = st.columns(3)

with a:
    st.metric(
        "🏎️ MONITORING",
        selected_project.get("name", "Unknown")
    )

with b:
    st.metric(
        "⚔️ REIATSU",
        f"{selected_project.get("progress", 0)}%"
    )

with c:
    st.metric(
        "🏁 MODE",
        status.get("mode", "🟢 GREEN FLAG")
    )


# ================================================================
# SIDEBAR
# ================================================================

with st.sidebar:

    st.header("🏎️ AI GRID")

    for project in projects:

        name = project.get("name", "Unknown")

        selected = name == status.get("selected_project")

        label = f"🔴 {name}" if selected else f"⚪ {name}"

        if st.button(
            label,
            key=f"project_{name}",
            use_container_width=True
        ):

            status["selected_project"] = name

            log_event(
                f"RACE CONTROL → PROJECT SELECTED: {name}"
            )

            play_audio("button.wav")
            st.rerun()

    st.divider()

    st.header("📡 OMNIROUTE")

    st.session_state.omniroute_url = st.text_input(
        "Endpoint",
        value=st.session_state.omniroute_url
    )

    st.session_state.omniroute_model = st.text_input(
        "Model",
        value=st.session_state.omniroute_model
    )

    st.session_state.omniroute_key = st.text_input(
        "API Key",
        value=st.session_state.omniroute_key,
        type="password"
    )

    if st.button(
        "📡 TEST OMNIROUTE",
        use_container_width=True
    ):

        if check_omniroute():
            st.success("🟢 OMNIROUTE ONLINE")
            play_audio(
                "ai.wav",
                "RACE CONTROL → OMNIROUTE ONLINE"
            )
        else:
            st.error("🔴 OMNIROUTE OFFLINE")
            play_audio(
                "warning.wav",
                "RACE CONTROL → OMNIROUTE OFFLINE"
            )

    st.divider()

    st.write("🧠 AI CORE — ONLINE")
    st.write("📡 TELEMETRY — ONLINE")
    st.write("🏎️ RACE CONTROL — READY")


# ================================================================
# PROJECT STATUS
# ================================================================

st.subheader(f"🏁 {selected_project.get("name")}")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("STATUS", selected_project.get("status", "UNKNOWN"))

with c2:
    st.metric("PHASE", selected_project.get("phase", "UNKNOWN"))

with c3:
    st.metric("HEALTH", selected_project.get("health", "UNKNOWN"))

with c4:
    st.metric("PRIORITY", selected_project.get("priority", "UNKNOWN"))


# ================================================================
# REIATSU
# ================================================================

st.subheader("⚡ REIATSU / DEVELOPMENT POWER")

progress = int(selected_project.get("progress", 0))

st.progress(max(0, min(100, progress)))

st.caption(f"DEVELOPMENT POWER • {progress}%")


# ================================================================
# AI CORE
# ================================================================

st.subheader("🧠 AI CORE MONITORING")

core1, core2, core3 = st.columns(3)

with core1:
    with st.container(border=True):
        st.markdown("### 🔵 KNOWLEDGE CORE")
        st.write("Scientific knowledge acquisition")
        st.success("OPERATIONAL")

with core2:
    with st.container(border=True):
        st.markdown("### 🔴 COGNITIVE CORE")
        st.write("Cognitive architecture")
        st.info("MONITORING")

with core3:
    with st.container(border=True):
        st.markdown("### 🟡 REASONING CORE")
        st.write("Reasoning and decision engine")
        st.warning("ACTIVE")


# ================================================================
# PROJECT INTELLIGENCE
# ================================================================

with st.expander("📊 PROJECT INTELLIGENCE", expanded=True):

    left, right = st.columns(2)

    with left:
        st.write(
            f"**Technology:** {selected_project.get("technology")}"
        )
        st.write(
            f"**Repository:** {selected_project.get("repository")}"
        )

    with right:
        st.write(
            f"**Mission:** {selected_project.get("mission")}"
        )
        st.write(
            f"**Next Operation:** {selected_project.get("next_operation")}"
        )


# ================================================================
# BANKAI AI COMMAND
# ================================================================

st.divider()

st.subheader("🤖 BANKAI AI COMMAND")

st.caption("Ollama-compatible AI routed through OmniRoute.")

ai_main, ai_info = st.columns([2, 1])

with ai_main:

    if st.session_state.last_ai_question:
        st.write(
            f"👤 **YOU:** {st.session_state.last_ai_question}"
        )

    if st.session_state.last_ai_response:
        with st.container(border=True):
            st.markdown("### ⚔️ BANKAI AI")
            st.write(st.session_state.last_ai_response)

    question = st.text_area(
        "AI Command",
        placeholder="Ask BANKAI AI about the selected AI project...",
        height=130
    )

    send, clear = st.columns(2)

    with send:

        if st.button(
            "⚡ SEND TO BANKAI AI",
            use_container_width=True
        ):

            if question.strip():

                st.session_state.last_ai_question = question.strip()

                try:
                    with st.spinner(
                        "BANKAI AI analysing telemetry..."
                    ):
                        answer = ask_bankai_ai(question.strip())

                    st.session_state.last_ai_response = answer

                    messages = status.setdefault("ai_messages", [])

                    messages.insert(
                        0,
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "project": selected_project.get("name"),
                            "question": question.strip(),
                            "answer": answer
                        }
                    )

                    status["ai_messages"] = messages[:20]

                    save_json(STATUS_FILE, status)

                    play_audio(
                        "ai.wav",
                        "BANKAI AI → ANALYSIS READY"
                    )

                    st.rerun()

                except Exception as exc:
                    st.error(
                        f"AI connection error: {type(exc).__name__}: {exc}"
                    )

    with clear:

        if st.button(
            "🧹 CLEAR AI",
            use_container_width=True
        ):

            st.session_state.last_ai_question = ""
            st.session_state.last_ai_response = ""
            play_audio("button.wav")
            st.rerun()


with ai_info:

    with st.container(border=True):

        st.markdown("### 📡 AI TELEMETRY")

        st.write(f"**Project:** {selected_project.get("name")}")
        st.write("**Route:** OmniRoute")
        st.write("**Backend:** Ollama compatible")
        st.write(f"**Model:** {st.session_state.omniroute_model}")

        if check_omniroute():
            st.success("🟢 OMNI ONLINE")
        else:
            st.warning("🟡 OMNI NOT DETECTED")


# ================================================================
# DEVELOPMENT SESSION
# ================================================================

st.divider()

st.subheader("🏎️ DEVELOPMENT SESSION")

lap_col, timer_col, state_col = st.columns(3)

with lap_col:
    st.metric(
        "CURRENT LAP",
        f"{status.get("current_lap", 1)} / {status.get("target_lap", 10)}"
    )

with timer_col:
    seconds = int(status.get("session_seconds", 0))
    minutes = seconds // 60
    secs = seconds % 60
    st.metric("SESSION TIME", f"{minutes:02d}:{secs:02d}")

with state_col:
    if status.get("session_running", False):
        st.metric("SESSION", "🟢 RUNNING")
    else:
        st.metric("SESSION", "🔴 STOPPED")


# ================================================================
# TIMER
# ================================================================

if status.get("session_running", False):

    now = time.time()
    elapsed = int(now - st.session_state.last_tick)

    if elapsed > 0:
        status["session_seconds"] = (
            int(status.get("session_seconds", 0))
            + elapsed
        )
        save_json(STATUS_FILE, status)

    st.session_state.last_tick = now
    time.sleep(1)
    st.rerun()

else:
    st.session_state.last_tick = time.time()


# ================================================================
# SESSION CONTROLS
# ================================================================

start, stop, lap, reset = st.columns(4)

with start:
    if st.button("▶️ START SESSION", use_container_width=True):
        status["session_running"] = True
        log_event("RACE CONTROL → SESSION STARTED")
        play_audio("race_start.wav")
        st.rerun()

with stop:
    if st.button("🛑 STOP SESSION", use_container_width=True):
        status["session_running"] = False
        log_event("RACE CONTROL → SESSION STOPPED")
        play_audio("stop.wav")
        st.rerun()

with lap:
    if st.button("🏁 NEXT LAP", use_container_width=True):
        current = int(status.get("current_lap", 1))
        target = int(status.get("target_lap", 10))
        status["current_lap"] = min(current + 1, target)
        log_event(f"RACE CONTROL → LAP {status["current_lap"]}")
        play_audio("lap.wav")
        st.rerun()

with reset:
    if st.button("🔄 RESET", use_container_width=True):
        status["session_running"] = False
        status["session_seconds"] = 0
        status["current_lap"] = 1
        log_event("RACE CONTROL → SESSION RESET")
        play_audio("button.wav")
        st.rerun()


# ================================================================
# MODES
# ================================================================

st.divider()
st.subheader("⚔️ RACE MODE")

modes = [
    "🟢 GREEN FLAG",
    "🔵 QUALIFYING",
    "🔴 ATTACK MODE",
    "🟡 CAUTION",
    "⚪ PIT MODE",
    "🧠 RESEARCH MODE",
    "⚔️ BANKAI MODE"
]

current_mode = status.get("mode", modes[0])

if current_mode not in modes:
    current_mode = modes[0]

new_mode = st.selectbox(
    "Operating mode",
    modes,
    index=modes.index(current_mode)
)

if new_mode != status.get("mode"):

    status["mode"] = new_mode

    if "BANKAI" in new_mode:
        audio = "bankai.wav"
    elif "ATTACK" in new_mode:
        audio = "attack_mode.wav"
    elif "CAUTION" in new_mode:
        audio = "warning.wav"
    elif "QUALIFYING" in new_mode:
        audio = "qualifying.wav"
    else:
        audio = "button.wav"

    log_event(f"RACE CONTROL → MODE: {new_mode}")
    play_audio(audio)
    st.rerun()


# ================================================================
# MOTIVATIONAL COMMAND
# ================================================================

st.divider()
st.subheader("🏆 MOTIVATIONAL COMMAND")

motivational = [
    ("FOCUS", "Keep your eyes on the target. The next lap is the only lap that matters."),
    ("DISCIPLINE", "Build the system one verified step at a time."),
    ("PRESSURE", "When pressure rises, precision matters more."),
    ("LIMIT", "Find the performance that is still available."),
    ("BANKAI", "Release the next level only when the foundation is ready.")
]

focus, message = motivational[
    (int(status.get("current_lap", 1)) - 1) % len(motivational)
]

with st.container(border=True):
    st.markdown(f"### ⚔️ {focus}")
    st.write(f"**{message}**")
    st.caption("MAX-INSPIRED ORIGINAL MOTIVATIONAL MESSAGE")
    st.write("MENTAL STATE: 🔒 LOCKED IN")
    st.write("MISSION: 🏎️ PUSH")


# ================================================================
# EVENT LOG
# ================================================================

st.divider()
st.subheader("📡 LAST SYSTEM TRANSMISSION")
st.info(status.get("last_radio", "RACE CONTROL → SYSTEM ONLINE"))

with st.expander("📻 RACE CONTROL EVENT LOG"):
    history = status.get("radio_history", [])

    if history:
        for event in history[:20]:
            st.write(
                f"`{event.get("time", "--:--:--")}` {event.get("message", "")}"
            )
    else:
        st.caption("No events recorded.")


# ================================================================
# AI HISTORY
# ================================================================

with st.expander("🧠 AI COMMAND HISTORY"):

    ai_history = status.get("ai_messages", [])

    if ai_history:

        for item in ai_history[:10]:
            st.write(
                f"`{item.get("time", "--:--:--")}` {item.get("project", "AI")}"
            )
            st.write(f"👤 {item.get("question", "")}")
            st.write(f"🤖 {item.get("answer", "")}")
            st.divider()

    else:
        st.caption("No AI commands recorded.")


# ================================================================
# FOOTER
# ================================================================

st.divider()
st.caption(
    "⚔️ BANKAI RACE CONTROL • AI MONITORING • "
    "BLEACH × F1 • OLLAMA / OMNIROUTE"
)
