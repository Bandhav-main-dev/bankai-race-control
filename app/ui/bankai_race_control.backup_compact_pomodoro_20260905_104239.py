
# ============================================================================
# ⚔️ SOUL FORGE MEMORY HELPERS V1
# ============================================================================


# =============================================================================
# SOUL FORGE — DEVELOPER MINDSET
# =============================================================================

SF_MAX_DEVELOPER_QUOTE = (
    "You are the best developer because you think you are the best."
)

SF_MAX_DEVELOPER_QUOTE_LABEL = (
    "SOUL FORGE × Max-inspired mindset"
)

def _sf_memory_get_project_name():

    try:

        for key in (
            "current_project",
            "selected_project",
            "active_project",
            "project_name",
        ):

            value = st.session_state.get(key)

            if value:
                return str(value)

    except Exception:
        pass

    return "SOUL_FORGE"


def _sf_memory_init():

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return

    if "sf_active_conversation_id" not in st.session_state:

        conversation = create_conversation(
            title="New Chat",
            project=_sf_memory_get_project_name(),
        )

        st.session_state[
            "sf_active_conversation_id"
        ] = conversation["conversation_id"]

        st.session_state[
            "sf_loaded_conversation"
        ] = conversation


def _sf_memory_load_active():

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return None

    _sf_memory_init()

    conversation_id = st.session_state.get(
        "sf_active_conversation_id"
    )

    if not conversation_id:
        return None

    conversation = load_conversation(
        conversation_id
    )

    if conversation:

        st.session_state[
            "sf_loaded_conversation"
        ] = conversation

    return conversation


def _sf_memory_save_user_message(message):

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return

    _sf_memory_init()

    conversation_id = st.session_state.get(
        "sf_active_conversation_id"
    )

    if conversation_id:

        save_message(
            conversation_id,
            "user",
            message,
        )

        remember_from_message(
            message,
            project=_sf_memory_get_project_name(),
        )


def _sf_memory_save_assistant_message(message):

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return

    conversation_id = st.session_state.get(
        "sf_active_conversation_id"
    )

    if conversation_id:

        save_message(
            conversation_id,
            "assistant",
            message,
        )


def _sf_memory_context(message):

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return ""

    return build_ai_memory_context(
        message,
        project=_sf_memory_get_project_name(),
    )


def _sf_memory_render():

    if not SOUL_FORGE_MEMORY_AVAILABLE:
        return

    try:

        render_soul_forge_memory_sidebar(
            project=_sf_memory_get_project_name()
        )

    except Exception:
        pass




# ============================================================================
# SOUL_FORGE_MEMORY_SYSTEM_IMPORT_V1
# ============================================================================

try:
    from app.core.soul_forge_memory import (
        add_memory,
        build_ai_memory_context,
        create_conversation,
        delete_conversation,
        detect_conflicts,
        list_conversations,
        load_conversation,
        memory_context,
        remember_from_message,
        rename_conversation,
        save_message,
        search_memory,
    )

    from app.core.soul_forge_memory_ui import (
        render_soul_forge_memory_panel,
        render_soul_forge_memory_sidebar,
    )

    SOUL_FORGE_MEMORY_AVAILABLE = True

except Exception as _sf_memory_import_error:

    SOUL_FORGE_MEMORY_AVAILABLE = False
    _sf_memory_import_error = str(_sf_memory_import_error)


import json

from pathlib import Path
from datetime import date, datetime, timedelta
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
    SOUL FORGE AI BRIDGE
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
                    "SOUL FORGE AI BRIDGE ERROR\n\n"
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
    ("📋", "Task Manager"),
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

# =============================================================================
# TASK MANAGER
# =============================================================================

SOUL_FORGE_TASK_FILE = Path(
    "/content/BANKAI-RACE-CONTROL/data/tasks.json"
)


def _sf_default_tasks():
    return [
        {
            "id": "SF-001",
            "title": "Build Knowledge Engine",
            "description": "Improve source-grounded knowledge workflow.",
            "project": "SOUL FORGE",
            "priority": "HIGH",
            "status": "IN PROGRESS",
            "progress": 70,
            "next_action": "Implement source retrieval",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
        {
            "id": "SF-002",
            "title": "Improve Agentic Pipeline",
            "description": "Refine the multi-stage agent workflow.",
            "project": "SOUL FORGE",
            "priority": "MEDIUM",
            "status": "IN PROGRESS",
            "progress": 40,
            "next_action": "Review validation stage",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
        {
            "id": "SF-003",
            "title": "Configure OpenRouter",
            "description": "Maintain multi-model routing and fallback.",
            "project": "SOUL FORGE",
            "priority": "HIGH",
            "status": "COMPLETED",
            "progress": 100,
            "next_action": "Monitor routing",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    ]


def _sf_load_tasks():
    try:
        if not SOUL_FORGE_TASK_FILE.exists():
            tasks = _sf_default_tasks()
            SOUL_FORGE_TASK_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            SOUL_FORGE_TASK_FILE.write_text(
                json.dumps(tasks, indent=2),
                encoding="utf-8",
            )
            return tasks

        data = json.loads(
            SOUL_FORGE_TASK_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return _sf_default_tasks()


def _sf_save_tasks(tasks):
    """
    Permission-safe SOUL FORGE task persistence.

    Streamlit Cloud may mount the application source tree as read-only.
    Therefore task writes must never assume that SOUL_FORGE_TASK_FILE is
    writable.

    Priority:
        1. Configured task file when writable.
        2. /tmp/soul_forge/data/tasks.json
        3. TMPDIR/soul_forge/data/tasks.json

    The current task list is also retained in Streamlit session state so
    Task Manager operations do not crash when persistent storage is unavailable.
    """
    import json
    import os
    from pathlib import Path

    # Always keep current task state for this Streamlit session.
    try:
        st.session_state["sf_tasks"] = tasks
    except Exception:
        pass

    configured_path = Path(SOUL_FORGE_TASK_FILE)

    candidates = [
        configured_path,
        Path("/tmp/soul_forge/data/tasks.json"),
        Path(os.environ.get("TMPDIR", "/tmp"))
        / "soul_forge"
        / "data"
        / "tasks.json",
    ]

    unique_candidates = []
    seen = set()

    for candidate in candidates:
        candidate = Path(candidate)
        key = str(candidate)

        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)

    payload = json.dumps(
        tasks,
        indent=2,
        ensure_ascii=False,
    )

    last_error = None

    for task_path in unique_candidates:
        try:
            task_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Test directory write permission.
            test_file = task_path.parent / ".soul_forge_write_test"

            try:
                test_file.write_text(
                    "ok",
                    encoding="utf-8",
                )
                test_file.unlink(missing_ok=True)

            except Exception as exc:
                last_error = exc
                continue

            # Write through a temporary file.
            temp_path = task_path.with_suffix(
                task_path.suffix + ".tmp"
            )

            temp_path.write_text(
                payload,
                encoding="utf-8",
            )

            temp_path.replace(task_path)

            try:
                st.session_state["sf_task_storage_path"] = str(
                    task_path
                )
                st.session_state["sf_task_storage_ok"] = True
                st.session_state.pop(
                    "sf_task_storage_error",
                    None,
                )
            except Exception:
                pass

            return True

        except (PermissionError, OSError, IOError) as exc:
            last_error = exc
            continue

        except Exception as exc:
            last_error = exc
            continue

    # Never crash Task Manager because persistence is unavailable.
    try:
        st.session_state["sf_task_storage_ok"] = False
        st.session_state["sf_task_storage_error"] = str(last_error)
    except Exception:
        pass

    return False
def _sf_task_id(tasks):
    numbers = []

    for task in tasks:
        match = re.search(
            r"SF-(\d+)",
            str(task.get("id", "")),
        )

        if match:
            numbers.append(
                int(match.group(1))
            )

    next_number = max(numbers, default=0) + 1

    return f"SF-{next_number:03d}"


def _sf_task_badge(priority):
    return {
        "HIGH": "🔴 HIGH",
        "MEDIUM": "🟡 MEDIUM",
        "LOW": "🟢 LOW",
    }.get(priority, priority)


def _sf_task_progress(value):
    try:
        value = int(value)
    except Exception:
        value = 0

    return max(0, min(100, value))


def _sf_task_end_of_week():
    today = datetime.now().date()

    # Sunday is the end of the week.
    days_until_sunday = (
        6 - today.weekday()
    ) % 7

    return today + timedelta(
        days=days_until_sunday
    )


def _sf_task_end_of_month():
    today = datetime.now().date()

    if today.month == 12:
        next_month = date(
            today.year + 1,
            1,
            1,
        )
    else:
        next_month = date(
            today.year,
            today.month + 1,
            1,
        )

    return next_month - timedelta(
        days=1
    )


def _sf_task_deadline_status(deadline, status):
    if status == "COMPLETED":
        return "completed"

    if not deadline:
        return "none"

    try:
        deadline_date = datetime.fromisoformat(
            str(deadline)
        ).date()

        today = datetime.now().date()

        if deadline_date < today:
            return "overdue"

        if deadline_date == today:
            return "today"

        if deadline_date <= today + timedelta(days=2):
            return "soon"

        return "normal"

    except Exception:
        return "none"


def _sf_task_deadline_label(deadline, status):
    state = _sf_task_deadline_status(
        deadline,
        status,
    )

    if not deadline:
        return "📅 No deadline"

    try:
        formatted = datetime.fromisoformat(
            str(deadline)
        ).strftime("%d %b %Y")
    except Exception:
        formatted = str(deadline)

    labels = {
        "overdue": f"🚨 OVERDUE · {formatted}",
        "today": f"🔴 DUE TODAY · {formatted}",
        "soon": f"🟡 DUE SOON · {formatted}",
        "completed": f"✅ {formatted}",
        "normal": f"📅 {formatted}",
        "none": "📅 No deadline",
    }

    return labels.get(
        state,
        f"📅 {formatted}",
    )


def _sf_ai_task_plan(plan_type):
    """
    Ask the existing SOUL FORGE AI bridge to create a structured task plan.

    The function intentionally calls bankai_chat(prompt) without introducing
    any new backend API or force_intent argument.
    """

    if plan_type == "WEEKLY":

        deadline = _sf_task_end_of_week()

        prompt = f"""
You are the SOUL FORGE task planning assistant.

Create a practical development task plan for the current week.

Today:
{datetime.now().date().isoformat()}

Weekly deadline:
{deadline.isoformat()}

Project:
SOUL FORGE

Return ONLY valid JSON.
Do not use markdown.
Do not use ``` fences.

JSON format:

[
  {{
    "title": "short task title",
    "description": "what must be accomplished",
    "priority": "HIGH",
    "next_action": "the immediate next action"
  }}
]

Rules:
- Generate 3 to 6 useful tasks.
- Focus on realistic software/AI development work.
- Avoid duplicate generic tasks.
- Priority must be HIGH, MEDIUM, or LOW.
- Do not include deadline, status, progress, id, or timestamps.
"""

    else:

        deadline = _sf_task_end_of_month()

        prompt = f"""
You are the SOUL FORGE task planning assistant.

Create a practical end-of-month development task plan.

Today:
{datetime.now().date().isoformat()}

Monthly deadline:
{deadline.isoformat()}

Project:
SOUL FORGE

Return ONLY valid JSON.
Do not use markdown.
Do not use ``` fences.

JSON format:

[
  {{
    "title": "short task title",
    "description": "what must be accomplished",
    "priority": "HIGH",
    "next_action": "the immediate next action"
  }}
]

Rules:
- Generate 4 to 8 useful tasks.
- Focus on meaningful monthly milestones.
- Include development, testing, documentation, reliability, and cleanup where appropriate.
- Avoid duplicate generic tasks.
- Priority must be HIGH, MEDIUM, or LOW.
- Do not include deadline, status, progress, id, or timestamps.
"""

    try:

        result = bankai_chat(
            prompt
        )

        if isinstance(result, dict):

            text = (
                result.get("response")
                or result.get("content")
                or result.get("message")
                or result.get("text")
                or ""
            )

        else:

            text = str(result)

        text = text.strip()

        # Remove accidental markdown fences.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        # Extract JSON array if the model included extra prose.
        first = text.find("[")
        last = text.rfind("]")

        if first >= 0 and last > first:

            text = text[
                first:last + 1
            ]

        data = json.loads(text)

        if not isinstance(data, list):
            return []

        valid = []

        for item in data:

            if not isinstance(item, dict):
                continue

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            if not title:
                continue

            priority = str(
                item.get(
                    "priority",
                    "MEDIUM",
                )
            ).upper()

            if priority not in {
                "HIGH",
                "MEDIUM",
                "LOW",
            }:
                priority = "MEDIUM"

            valid.append(
                {
                    "title": title,
                    "description": str(
                        item.get(
                            "description",
                            "",
                        )
                    ).strip(),
                    "priority": priority,
                    "next_action": str(
                        item.get(
                            "next_action",
                            "",
                        )
                    ).strip(),
                }
            )

        return valid

    except Exception as exc:

        st.warning(
            f"AI planning could not complete: {exc}"
        )

        return []




# =============================================================================
# SOUL_FORGE_GLOBAL_FOCUS_TIMER_V1
# =============================================================================

SF_FOCUS_VERSION = "1.0.0"

SF_FOCUS_QUOTES = [
    "One task. One target. No distraction.",
    "Discipline creates momentum.",
    "Build first. Perfect later.",
    "The next lap starts now.",
    "Small progress is still progress.",
    "Focus is a superpower when you protect it.",
    "You don't need more time. You need better focus.",
    "One completed session moves the project forward.",
    "Stay in the lane. Finish the task.",
    "Bankai is control — control your focus.",
    "Your future system is being built right now.",
    "Don't watch the clock. Use it.",
]


def _sf_focus_init():
    """Initialize the global SOUL FORGE focus session."""

    defaults = {
        "sf_focus_active": False,
        "sf_focus_paused": False,
        "sf_focus_task_id": None,
        "sf_focus_task_title": "",
        "sf_focus_project": "",
        "sf_focus_priority": "",
        "sf_focus_duration_seconds": 25 * 60,
        "sf_focus_remaining_seconds": 25 * 60,
        "sf_focus_started_at": None,
        "sf_focus_pause_started_at": None,
        "sf_focus_total_paused_seconds": 0,
        "sf_focus_quote_index": 0,
        "sf_focus_completed_sessions": 0,
        "sf_focus_total_seconds_today": 0,
        "sf_focus_session_start": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _sf_focus_now():
    return datetime.now()


def _sf_focus_recalculate():
    """
    Calculate remaining time from timestamps.

    This is intentionally timestamp based instead of relying on a loop.
    Streamlit reruns the application frequently, so this keeps the timer
    consistent when the user changes pages.
    """

    if not st.session_state.sf_focus_active:
        return

    if st.session_state.sf_focus_paused:
        return

    started_at = st.session_state.sf_focus_started_at

    if not started_at:
        return

    if isinstance(started_at, str):
        try:
            started_at = datetime.fromisoformat(started_at)
        except Exception:
            return

    total = int(st.session_state.sf_focus_duration_seconds)

    paused = int(st.session_state.sf_focus_total_paused_seconds)

    elapsed = (
        _sf_focus_now() - started_at
    ).total_seconds()

    remaining = max(
        0,
        int(total - elapsed + paused)
    )

    st.session_state.sf_focus_remaining_seconds = remaining

    if remaining <= 0:
        _sf_focus_complete()


def _sf_focus_format(seconds):
    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


def _sf_focus_start(
    task_id,
    task_title,
    duration_seconds,
    project="",
    priority="",
):
    """Start a new focus session."""

    _sf_focus_init()

    now = _sf_focus_now()

    st.session_state.sf_focus_active = True
    st.session_state.sf_focus_paused = False

    st.session_state.sf_focus_task_id = str(task_id)
    st.session_state.sf_focus_task_title = str(task_title)
    st.session_state.sf_focus_project = str(project or "")
    st.session_state.sf_focus_priority = str(priority or "")

    st.session_state.sf_focus_duration_seconds = int(
        duration_seconds
    )

    st.session_state.sf_focus_remaining_seconds = int(
        duration_seconds
    )

    st.session_state.sf_focus_started_at = now.isoformat()
    st.session_state.sf_focus_pause_started_at = None
    st.session_state.sf_focus_total_paused_seconds = 0
    st.session_state.sf_focus_session_start = now.isoformat()

    st.session_state.sf_focus_quote_index = (
        st.session_state.sf_focus_quote_index + 1
    ) % len(SF_FOCUS_QUOTES)


def _sf_focus_pause():
    """Pause the active focus session."""

    _sf_focus_init()

    if not st.session_state.sf_focus_active:
        return

    if st.session_state.sf_focus_paused:
        return

    _sf_focus_recalculate()

    st.session_state.sf_focus_paused = True
    st.session_state.sf_focus_pause_started_at = (
        _sf_focus_now().isoformat()
    )


def _sf_focus_resume():
    """Resume a paused focus session."""

    _sf_focus_init()

    if not st.session_state.sf_focus_active:
        return

    if not st.session_state.sf_focus_paused:
        return

    pause_started = st.session_state.sf_focus_pause_started_at

    if pause_started:
        try:
            pause_started_dt = datetime.fromisoformat(
                pause_started
            )

            paused_seconds = (
                _sf_focus_now() - pause_started_dt
            ).total_seconds()

            st.session_state.sf_focus_total_paused_seconds += int(
                paused_seconds
            )

        except Exception:
            pass

    st.session_state.sf_focus_paused = False
    st.session_state.sf_focus_pause_started_at = None


def _sf_focus_restart():
    """Restart the current task's focus session."""

    _sf_focus_init()

    if not st.session_state.sf_focus_task_id:
        return

    _sf_focus_start(
        task_id=st.session_state.sf_focus_task_id,
        task_title=st.session_state.sf_focus_task_title,
        duration_seconds=st.session_state.sf_focus_duration_seconds,
        project=st.session_state.sf_focus_project,
        priority=st.session_state.sf_focus_priority,
    )


def _sf_focus_stop():
    """Stop the current focus session."""

    _sf_focus_init()

    st.session_state.sf_focus_active = False
    st.session_state.sf_focus_paused = False

    st.session_state.sf_focus_task_id = None
    st.session_state.sf_focus_task_title = ""
    st.session_state.sf_focus_project = ""
    st.session_state.sf_focus_priority = ""

    st.session_state.sf_focus_remaining_seconds = 0

    st.session_state.sf_focus_started_at = None
    st.session_state.sf_focus_pause_started_at = None
    st.session_state.sf_focus_total_paused_seconds = 0
    st.session_state.sf_focus_session_start = None


def _sf_focus_complete():
    """Finish a focus session."""

    if not st.session_state.sf_focus_active:
        return

    duration = int(
        st.session_state.sf_focus_duration_seconds
    )

    st.session_state.sf_focus_completed_sessions += 1

    st.session_state.sf_focus_total_seconds_today += duration

    st.session_state.sf_focus_remaining_seconds = 0
    st.session_state.sf_focus_active = False
    st.session_state.sf_focus_paused = False





# Initialize global focus state as soon as the application loads.
_sf_focus_init()

# =============================================================================
# END SOUL_FORGE_GLOBAL_FOCUS_TIMER_V1
# =============================================================================



def render_task_manager():

    st.title("📋 TASK MANAGER")

    st.caption(
        "Your SOUL FORGE execution board — plan, build, review and finish."
    )

    tasks = _sf_load_tasks()

    # =========================================================================
    # SESSION STATE
    # =========================================================================

    if "sf_task_editing" not in st.session_state:
        st.session_state.sf_task_editing = None

    if "sf_task_search" not in st.session_state:
        st.session_state.sf_task_search = ""

    if "sf_task_reset_confirm" not in st.session_state:
        st.session_state.sf_task_reset_confirm = False

    # =========================================================================
    # TOP COMMAND BAR
    # =========================================================================

    top1, top2, top3, top4 = st.columns(
        [1.5, 1.5, 1.5, 1]
    )

    with top1:

        if st.button(
            "➕ NEW TASK",
            use_container_width=True,
        ):

            st.session_state.sf_task_new_open = True

    with top2:

        if st.button(
            "🤖 WEEKLY AI PLAN",
            use_container_width=True,
        ):

            with st.spinner(
                "SOUL FORGE is creating this week's tasks..."
            ):

                generated = _sf_ai_task_plan(
                    "WEEKLY"
                )

            if generated:

                deadline = _sf_task_end_of_week()
                now = datetime.now().isoformat(
                    timespec="seconds"
                )

                existing_titles = {
                    str(
                        task.get(
                            "title",
                            ""
                        )
                    ).strip().lower()
                    for task in tasks
                }

                added = 0

                for item in generated:

                    title = item["title"]

                    if title.lower() in existing_titles:
                        continue

                    tasks.append(
                        {
                            "id": _sf_task_id(tasks),
                            "title": title,
                            "description": item.get(
                                "description",
                                "",
                            ),
                            "project": "SOUL FORGE",
                            "priority": item.get(
                                "priority",
                                "MEDIUM",
                            ),
                            "status": "NOT STARTED",
                            "progress": 0,
                            "next_action": item.get(
                                "next_action",
                                "",
                            ),
                            "task_type": "WEEKLY",
                            "deadline": deadline.isoformat(),
                            "created_at": now,
                            "updated_at": now,
                        }
                    )

                    existing_titles.add(
                        title.lower()
                    )

                    added += 1

                _sf_save_tasks(tasks)

                st.success(
                    f"🤖 Weekly AI plan created — {added} new tasks."
                )

                st.rerun()

    with top3:

        if st.button(
            "🤖 MONTHLY AI PLAN",
            use_container_width=True,
        ):

            with st.spinner(
                "SOUL FORGE is creating this month's tasks..."
            ):

                generated = _sf_ai_task_plan(
                    "MONTHLY"
                )

            if generated:

                deadline = _sf_task_end_of_month()
                now = datetime.now().isoformat(
                    timespec="seconds"
                )

                existing_titles = {
                    str(
                        task.get(
                            "title",
                            ""
                        )
                    ).strip().lower()
                    for task in tasks
                }

                added = 0

                for item in generated:

                    title = item["title"]

                    if title.lower() in existing_titles:
                        continue

                    tasks.append(
                        {
                            "id": _sf_task_id(tasks),
                            "title": title,
                            "description": item.get(
                                "description",
                                "",
                            ),
                            "project": "SOUL FORGE",
                            "priority": item.get(
                                "priority",
                                "MEDIUM",
                            ),
                            "status": "NOT STARTED",
                            "progress": 0,
                            "next_action": item.get(
                                "next_action",
                                "",
                            ),
                            "task_type": "MONTHLY",
                            "deadline": deadline.isoformat(),
                            "created_at": now,
                            "updated_at": now,
                        }
                    )

                    existing_titles.add(
                        title.lower()
                    )

                    added += 1

                _sf_save_tasks(tasks)

                st.success(
                    f"🤖 Monthly AI plan created — {added} new tasks."
                )

                st.rerun()

    with top4:

        if st.button(
            "🗑️ RESET TASKS",
            use_container_width=True,
        ):

            st.session_state.sf_task_reset_confirm = True

    # =========================================================================
    # RESET CONFIRMATION
    # =========================================================================

    if st.session_state.sf_task_reset_confirm:

        st.warning(
            "⚠️ This will permanently delete all current tasks."
        )

        r1, r2 = st.columns(2)

        with r1:

            if st.button(
                "🗑️ YES, DELETE ALL TASKS",
                use_container_width=True,
            ):

                _sf_save_tasks([])

                st.session_state.sf_task_reset_confirm = False
                st.session_state.sf_task_editing = None

                st.success(
                    "All tasks have been reset."
                )

                st.rerun()

        with r2:

            if st.button(
                "❌ CANCEL RESET",
                use_container_width=True,
            ):

                st.session_state.sf_task_reset_confirm = False

                st.rerun()

    st.divider()

    # =========================================================================
    # SUMMARY
    # =========================================================================

    total = len(tasks)

    completed = sum(
        1
        for task in tasks
        if task.get("status") == "COMPLETED"
    )

    active = total - completed

    overdue = sum(
        1
        for task in tasks
        if _sf_task_deadline_status(
            task.get("deadline"),
            task.get("status"),
        ) == "overdue"
    )

    average_progress = (
        round(
            sum(
                _sf_task_progress(
                    task.get(
                        "progress",
                        0,
                    )
                )
                for task in tasks
            )
            / total
        )
        if total
        else 0
    )

    s1, s2, s3, s4, s5 = st.columns(5)

    with s1:
        st.metric(
            "TOTAL",
            total,
        )

    with s2:
        st.metric(
            "ACTIVE",
            active,
        )

    with s3:
        st.metric(
            "COMPLETED",
            completed,
        )

    with s4:
        st.metric(
            "OVERDUE",
            overdue,
        )

    with s5:
        st.metric(
            "AVG PROGRESS",
            f"{average_progress}%",
        )

    st.divider()

    # =========================================================================
    # CREATE NEW TASK
    # =========================================================================

    new_open = st.session_state.get(
        "sf_task_new_open",
        False,
    )

    with st.expander(
        "➕ CREATE NEW TASK",
        expanded=new_open,
    ):

        with st.form(
            "sf_create_task_form_v2"
        ):

            title = st.text_input(
                "Task title",
                placeholder="Example: Implement source ranking",
            )

            description = st.text_area(
                "Description",
                placeholder="What needs to be accomplished?",
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                project = st.text_input(
                    "Project",
                    value="SOUL FORGE",
                )

            with c2:

                priority = st.selectbox(
                    "Priority",
                    [
                        "HIGH",
                        "MEDIUM",
                        "LOW",
                    ],
                )

            with c3:

                status = st.selectbox(
                    "Status",
                    [
                        "NOT STARTED",
                        "IN PROGRESS",
                        "BLOCKED",
                        "COMPLETED",
                    ],
                )

            c4, c5, c6 = st.columns(3)

            with c4:

                task_type = st.selectbox(
                    "Task type",
                    [
                        "ONE-TIME",
                        "WEEKLY",
                        "MONTHLY",
                    ],
                )

            with c5:

                default_deadline = datetime.now().date()

                if task_type == "WEEKLY":
                    default_deadline = _sf_task_end_of_week()

                elif task_type == "MONTHLY":
                    default_deadline = _sf_task_end_of_month()

                deadline = st.date_input(
                    "Deadline",
                    value=default_deadline,
                )

            with c6:

                progress = st.slider(
                    "Progress",
                    0,
                    100,
                    0,
                    5,
                )

            next_action = st.text_input(
                "Next action",
                placeholder="What should happen next?",
            )

            submitted = st.form_submit_button(
                "➕ CREATE TASK",
                use_container_width=True,
            )

            if submitted:

                if not title.strip():

                    st.error(
                        "Task title is required."
                    )

                else:

                    now = datetime.now().isoformat(
                        timespec="seconds"
                    )

                    new_task = {
                        "id": _sf_task_id(tasks),
                        "title": title.strip(),
                        "description": description.strip(),
                        "project": (
                            project.strip()
                            or "SOUL FORGE"
                        ),
                        "priority": priority,
                        "status": status,
                        "progress": (
                            100
                            if status == "COMPLETED"
                            else progress
                        ),
                        "next_action": next_action.strip(),
                        "task_type": task_type,
                        "deadline": deadline.isoformat(),
                        "created_at": now,
                        "updated_at": now,
                    }

                    tasks.append(
                        new_task
                    )

                    _sf_save_tasks(
                        tasks
                    )

                    st.session_state.sf_task_new_open = False

                    st.success(
                        f"Created task: {title.strip()}"
                    )

                    st.rerun()

    # =========================================================================
    # FILTERS
    # =========================================================================

    st.subheader(
        "🔎 TASK BOARD"
    )

    f1, f2, f3, f4, f5 = st.columns(
        [1.5, 1, 1, 1, 1]
    )

    with f1:

        search = st.text_input(
            "Search",
            key="sf_task_search_v2",
            placeholder="Search tasks...",
        )

    with f2:

        status_filter = st.selectbox(
            "Status",
            [
                "ALL",
                "NOT STARTED",
                "IN PROGRESS",
                "BLOCKED",
                "COMPLETED",
            ],
        )

    with f3:

        priority_filter = st.selectbox(
            "Priority",
            [
                "ALL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
        )

    with f4:

        type_filter = st.selectbox(
            "Type",
            [
                "ALL",
                "ONE-TIME",
                "WEEKLY",
                "MONTHLY",
            ],
        )

    with f5:

        view_filter = st.selectbox(
            "View",
            [
                "ALL TASKS",
                "ACTIVE",
                "COMPLETED",
                "OVERDUE",
            ],
        )

    # =========================================================================
    # FILTER TASKS
    # =========================================================================

    filtered = []

    for task in tasks:

        combined = " ".join(
            [
                str(
                    task.get(
                        "title",
                        "",
                    )
                ),
                str(
                    task.get(
                        "description",
                        "",
                    )
                ),
                str(
                    task.get(
                        "project",
                        "",
                    )
                ),
                str(
                    task.get(
                        "next_action",
                        "",
                    )
                ),
            ]
        ).lower()

        if search.strip():

            if search.lower().strip() not in combined:
                continue

        if (
            status_filter != "ALL"
            and task.get("status") != status_filter
        ):
            continue

        if (
            priority_filter != "ALL"
            and task.get("priority") != priority_filter
        ):
            continue

        if (
            type_filter != "ALL"
            and task.get(
                "task_type",
                "ONE-TIME",
            ) != type_filter
        ):
            continue

        if (
            view_filter == "ACTIVE"
            and task.get("status") == "COMPLETED"
        ):
            continue

        if (
            view_filter == "COMPLETED"
            and task.get("status") != "COMPLETED"
        ):
            continue

        if view_filter == "OVERDUE":

            if _sf_task_deadline_status(
                task.get("deadline"),
                task.get("status"),
            ) != "overdue":

                continue

        filtered.append(
            task
        )

    # =========================================================================
    # SORT
    # =========================================================================

    def _sf_sort_key(task):

        deadline = task.get(
            "deadline"
        )

        if not deadline:
            return "9999-12-31"

        return str(deadline)

    filtered.sort(
        key=_sf_sort_key
    )

    # =========================================================================
    # TASK LIST
    # =========================================================================

    if not filtered:

        st.info(
            "No tasks match the current filters."
        )

    for task in filtered:

        task_id = task.get(
            "id",
            "UNKNOWN",
        )

        task_title = task.get(
            "title",
            "Untitled Task",
        )

        task_status = task.get(
            "status",
            "NOT STARTED",
        )

        task_priority = task.get(
            "priority",
            "MEDIUM",
        )

        task_progress = _sf_task_progress(
            task.get(
                "progress",
                0,
            )
        )

        task_type = task.get(
            "task_type",
            "ONE-TIME",
        )

        deadline = task.get(
            "deadline"
        )

        deadline_state = _sf_task_deadline_status(
            deadline,
            task_status,
        )

        with st.container(
            border=True
        ):

            top_left, top_mid, top_right = st.columns(
                [4, 2, 1.3]
            )

            with top_left:

                if task_status == "COMPLETED":

                    st.markdown(
                        f"### ✅ {task_title}"
                    )

                elif deadline_state == "overdue":

                    st.markdown(
                        f"### 🚨 {task_title}"
                    )

                else:

                    st.markdown(
                        f"### ☐ {task_title}"
                    )

                st.caption(
                    f"{task_id}  •  "
                    f"{task.get('project', 'SOUL FORGE')}"
                )

            with top_mid:

                priority_labels = {
                    "HIGH": "🔴 HIGH",
                    "MEDIUM": "🟡 MEDIUM",
                    "LOW": "🟢 LOW",
                }

                st.write(
                    priority_labels.get(
                        task_priority,
                        task_priority,
                    )
                )

                type_labels = {
                    "ONE-TIME": "⚡ ONE-TIME",
                    "WEEKLY": "🔁 WEEKLY",
                    "MONTHLY": "📆 MONTHLY",
                }

                st.caption(
                    type_labels.get(
                        task_type,
                        task_type,
                    )
                )

            with top_right:

                st.write(
                    f"**{task_progress}%**"
                )

                st.caption(
                    task_status
                )

            st.progress(
                task_progress / 100
            )

            d1, d2 = st.columns(2)

            with d1:

                st.write(
                    _sf_task_deadline_label(
                        deadline,
                        task_status,
                    )
                )

            with d2:

                next_action_value = task.get(
                    "next_action",
                    "",
                )

                if next_action_value:

                    st.caption(
                        f"➡️ Next: {next_action_value}"
                    )

            info1, info2 = st.columns(2)

            with info1:

                st.write(
                    "**Description**"
                )

                st.caption(
                    task.get(
                        "description",
                        "No description.",
                    )
                    or "No description."
                )

            with info2:

                st.write(
                    "**Project**"
                )

                st.caption(
                    task.get(
                        "project",
                        "SOUL FORGE",
                    )
                )

            action1, action2, action3 = st.columns(3)

            with action1:

                if task_status == "COMPLETED":

                    if st.button(
                        "↩️ REOPEN",
                        key=f"sf_reopen_v2_{task_id}",
                        use_container_width=True,
                    ):

                        task["status"] = "IN PROGRESS"

                        if task_progress >= 100:
                            task["progress"] = 90

                        task["updated_at"] = (
                            datetime.now().isoformat(
                                timespec="seconds"
                            )
                        )

                        _sf_save_tasks(
                            tasks
                        )

                        st.rerun()

                else:

                    if st.button(
                        "✅ COMPLETE",
                        key=f"sf_complete_v2_{task_id}",
                        use_container_width=True,
                    ):

                        task["status"] = "COMPLETED"
                        task["progress"] = 100

                        task["updated_at"] = (
                            datetime.now().isoformat(
                                timespec="seconds"
                            )
                        )

                        _sf_save_tasks(
                            tasks
                        )

                        st.rerun()

            with action2:

                if st.button(
                    "✏️ EDIT",
                    key=f"sf_edit_v2_{task_id}",
                    use_container_width=True,
                ):

                    st.session_state.sf_task_editing = task_id

                    st.rerun()

            with action3:

                if st.button(
                    "🗑️ DELETE",
                    key=f"sf_delete_v2_{task_id}",
                    use_container_width=True,
                ):

                    tasks = [
                        item
                        for item in tasks
                        if item.get("id") != task_id
                    ]

                    _sf_save_tasks(
                        tasks
                    )

                    st.session_state.sf_task_editing = None

                    st.rerun()

            # =================================================================
            # EDIT
            # =================================================================

            if (
                st.session_state.sf_task_editing
                == task_id
            ):

                st.divider()

                st.markdown(
                    "#### ✏️ EDIT TASK"
                )

                with st.form(
                    f"sf_edit_form_v2_{task_id}"
                ):

                    edit_title = st.text_input(
                        "Title",
                        value=task_title,
                    )

                    edit_description = st.text_area(
                        "Description",
                        value=task.get(
                            "description",
                            "",
                        ),
                    )

                    e1, e2, e3 = st.columns(3)

                    with e1:

                        edit_project = st.text_input(
                            "Project",
                            value=task.get(
                                "project",
                                "SOUL FORGE",
                            ),
                        )

                    with e2:

                        priorities = [
                            "HIGH",
                            "MEDIUM",
                            "LOW",
                        ]

                        current_priority = task.get(
                            "priority",
                            "MEDIUM",
                        )

                        edit_priority = st.selectbox(
                            "Priority",
                            priorities,
                            index=(
                                priorities.index(
                                    current_priority
                                )
                                if current_priority in priorities
                                else 1
                            ),
                        )

                    with e3:

                        statuses = [
                            "NOT STARTED",
                            "IN PROGRESS",
                            "BLOCKED",
                            "COMPLETED",
                        ]

                        current_status = task.get(
                            "status",
                            "NOT STARTED",
                        )

                        edit_status = st.selectbox(
                            "Status",
                            statuses,
                            index=(
                                statuses.index(
                                    current_status
                                )
                                if current_status in statuses
                                else 0
                            ),
                        )

                    e4, e5, e6 = st.columns(3)

                    with e4:

                        types = [
                            "ONE-TIME",
                            "WEEKLY",
                            "MONTHLY",
                        ]

                        current_type = task.get(
                            "task_type",
                            "ONE-TIME",
                        )

                        edit_type = st.selectbox(
                            "Task type",
                            types,
                            index=(
                                types.index(
                                    current_type
                                )
                                if current_type in types
                                else 0
                            ),
                        )

                    with e5:

                        try:

                            current_deadline = (
                                datetime.fromisoformat(
                                    str(deadline)
                                ).date()
                                if deadline
                                else datetime.now().date()
                            )

                        except Exception:

                            current_deadline = (
                                datetime.now().date()
                            )

                        edit_deadline = st.date_input(
                            "Deadline",
                            value=current_deadline,
                        )

                    with e6:

                        edit_progress = st.slider(
                            "Progress",
                            0,
                            100,
                            task_progress,
                            5,
                        )

                    edit_next_action = st.text_input(
                        "Next action",
                        value=task.get(
                            "next_action",
                            "",
                        ),
                    )

                    ec1, ec2 = st.columns(2)

                    with ec1:

                        save_edit = st.form_submit_button(
                            "💾 SAVE CHANGES",
                            use_container_width=True,
                        )

                    with ec2:

                        cancel_edit = st.form_submit_button(
                            "❌ CANCEL",
                            use_container_width=True,
                        )

                    if save_edit:

                        task["title"] = (
                            edit_title.strip()
                            or task["title"]
                        )

                        task["description"] = (
                            edit_description.strip()
                        )

                        task["project"] = (
                            edit_project.strip()
                            or "SOUL FORGE"
                        )

                        task["priority"] = (
                            edit_priority
                        )

                        task["status"] = (
                            edit_status
                        )

                        task["task_type"] = (
                            edit_type
                        )

                        task["deadline"] = (
                            edit_deadline.isoformat()
                        )

                        task["progress"] = (
                            100
                            if edit_status == "COMPLETED"
                            else edit_progress
                        )

                        task["next_action"] = (
                            edit_next_action.strip()
                        )

                        task["updated_at"] = (
                            datetime.now().isoformat(
                                timespec="seconds"
                            )
                        )

                        _sf_save_tasks(
                            tasks
                        )

                        st.session_state.sf_task_editing = None

                        st.rerun()

                    if cancel_edit:

                        st.session_state.sf_task_editing = None

                        st.rerun()

    # =========================================================================
    # AI PLANNER INFORMATION
    # =========================================================================

    st.divider()

    with st.expander(
        "🤖 AI TASK PLANNER"
    ):

        st.write(
            "SOUL FORGE can generate recurring development work automatically."
        )

        p1, p2 = st.columns(2)

        with p1:

            st.markdown(
                "### 🔁 Weekly"
            )

            st.caption(
                "AI creates 3–6 tasks targeted for the end of this week."
            )

            st.write(
                f"Deadline: **{_sf_task_end_of_week().strftime('%d %b %Y')}**"
            )

        with p2:

            st.markdown(
                "### 📆 Monthly"
            )

            st.caption(
                "AI creates 4–8 milestone tasks targeted for the end of this month."
            )

            st.write(
                f"Deadline: **{_sf_task_end_of_month().strftime('%d %b %Y')}**"
            )

    # =========================================================================
    # TASK STORAGE
    # =========================================================================

    with st.expander(
        "⚙️ TASK STORAGE"
    ):

        st.caption(
            "Tasks are persisted locally and survive Streamlit reruns."
        )

        st.code(
            str(
                SOUL_FORGE_TASK_FILE
            ),
            language="text",
        )

        st.caption(
            f"{len(tasks)} task records currently stored."
        )


# -------------------------------------------------------------------------
# GLOBAL SOUL FORGE FOCUS SESSION
# -------------------------------------------------------------------------

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
            "SOUL FORGE AI BRIDGE"
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



def render_sf_max_developer_quote():

    # ========================================================================
    # SOUL FORGE — CHATBOT HERO TITLE
    # ========================================================================

    st.markdown(
        "# ⚔️ SOUL FORGE"
    )

    st.markdown(
        "### **THE FORGE OF GREAT DEVELOPERS**"
    )

    st.caption(
        "SOUL FORGE × Max-inspired mindset"
    )

    st.markdown(
        "> **“You are the best developer because you think you are the best.”**"
    )

    st.caption(
        "THINK  •  BUILD  •  ATTACK  •  IMPROVE"
    )

def render_chat():

    # ========================================================================
    # 🧠 SOUL FORGE MEMORY PANEL
    # ========================================================================

    render_sf_max_developer_quote()
    try:
        render_soul_forge_memory_panel(
            project=_sf_memory_get_project_name()
        )
    except Exception:
        pass



    # ========================================================================
    # 🧠 SOUL FORGE PERSISTENT MEMORY
    # ========================================================================

    _sf_memory_init()
    _sf_memory_load_active()
    _sf_memory_render()



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

    # ⚔️ SOUL FORGE MEMORY CONTEXT

    # Memory retrieval is available through _sf_memory_context().

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
                "SOUL FORGE THINKING..."
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


# === SOUL FORGE GLOBAL HEADER BEGIN ===

@st.fragment(run_every="1s")
@st.fragment(run_every="1s")
def _sf_focus_render_global():
    """
    SOUL FORGE GLOBAL POMODORO COMMAND CENTER.

    Global controls are rendered before the page router.
    The timer is native Streamlit and uses session state.
    """

    import time
    from pathlib import Path
    import streamlit as st

    # =========================================================================
    # SESSION STATE
    # =========================================================================

    if "sf_active_task" not in st.session_state:
        st.session_state.sf_active_task = "No active task"

    if "sf_pomo_phase" not in st.session_state:
        st.session_state.sf_pomo_phase = "WORK"

    if "sf_pomo_cycle" not in st.session_state:
        st.session_state.sf_pomo_cycle = 1

    if "sf_pomo_work_minutes" not in st.session_state:
        st.session_state.sf_pomo_work_minutes = 25

    if "sf_pomo_break_minutes" not in st.session_state:
        st.session_state.sf_pomo_break_minutes = 5

    if "sf_pomo_seconds" not in st.session_state:
        st.session_state.sf_pomo_seconds = 25 * 60

    if "sf_pomo_running" not in st.session_state:
        st.session_state.sf_pomo_running = False

    if "sf_pomo_end_time" not in st.session_state:
        st.session_state.sf_pomo_end_time = None

    if "sf_pomo_paused_remaining" not in st.session_state:
        st.session_state.sf_pomo_paused_remaining = 25 * 60

    if "sf_pomo_completed" not in st.session_state:
        st.session_state.sf_pomo_completed = False

    if "sf_pomo_sessions_completed" not in st.session_state:
        st.session_state.sf_pomo_sessions_completed = 0

    if "sf_pomo_last_transition" not in st.session_state:
        st.session_state.sf_pomo_last_transition = None

    # =========================================================================
    # TASK DISCOVERY
    # =========================================================================

    task_options = [
        "No active task",
    ]

    project_root = Path("/content/BANKAI-RACE-CONTROL")
    tasks_file = project_root / "tasks.json"

    if tasks_file.exists():
        try:
            import json

            task_data = json.loads(
                tasks_file.read_text(encoding="utf-8")
            )

            discovered = []

            if isinstance(task_data, list):
                discovered = task_data

            elif isinstance(task_data, dict):
                for key in (
                    "tasks",
                    "items",
                    "active_tasks",
                    "roadmap",
                ):
                    value = task_data.get(key)

                    if isinstance(value, list):
                        discovered = value
                        break

            for item in discovered:
                if isinstance(item, str):
                    name = item.strip()

                    if name:
                        task_options.append(name)

                elif isinstance(item, dict):
                    task_id = str(
                        item.get("id", "")
                    ).strip()

                    name = str(
                        item.get(
                            "name",
                            item.get(
                                "title",
                                item.get(
                                    "task",
                                    ""
                                )
                            ),
                        )
                    ).strip()

                    if task_id and name:
                        display_name = f"{task_id} — {name}"

                    elif name:
                        display_name = name

                    elif task_id:
                        display_name = task_id

                    else:
                        display_name = ""

                    if display_name:
                        task_options.append(display_name)

        except Exception:
            pass

    # Remove duplicates while preserving order.
    task_options = list(
        dict.fromkeys(task_options)
    )

    if st.session_state.sf_active_task not in task_options:
        st.session_state.sf_active_task = "No active task"

    # =========================================================================
    # TIMER CALCULATION
    # =========================================================================

    if st.session_state.sf_pomo_running:

        end_time = st.session_state.sf_pomo_end_time

        if end_time is None:
            duration = max(
                1,
                st.session_state.sf_pomo_seconds,
            )

            st.session_state.sf_pomo_end_time = (
                time.time() + duration
            )

            end_time = st.session_state.sf_pomo_end_time

        remaining = max(
            0,
            int(end_time - time.time()),
        )

        st.session_state.sf_pomo_seconds = remaining

        # ---------------------------------------------------------------------
        # PHASE COMPLETE
        # ---------------------------------------------------------------------

        if remaining <= 0:

            completed_phase = (
                st.session_state.sf_pomo_phase
            )

            st.session_state.sf_pomo_running = False
            st.session_state.sf_pomo_end_time = None
            st.session_state.sf_pomo_last_transition = time.time()

            if completed_phase == "WORK":

                st.session_state.sf_pomo_sessions_completed += 1

                st.session_state.sf_pomo_phase = "BREAK"

                st.session_state.sf_pomo_seconds = (
                    st.session_state.sf_pomo_break_minutes * 60
                )

                st.session_state.sf_pomo_paused_remaining = (
                    st.session_state.sf_pomo_seconds
                )

                st.session_state.sf_pomo_completed = True

                st.toast(
                    "Work session complete — break time.",
                    icon="☕",
                )

            else:

                st.session_state.sf_pomo_cycle += 1

                st.session_state.sf_pomo_phase = "WORK"

                st.session_state.sf_pomo_seconds = (
                    st.session_state.sf_pomo_work_minutes * 60
                )

                st.session_state.sf_pomo_paused_remaining = (
                    st.session_state.sf_pomo_seconds
                )

                st.session_state.sf_pomo_completed = True

                st.toast(
                    "Break complete — forge again.",
                    icon="🔥",
                )

    # =========================================================================
    # HEADER
    # =========================================================================

    st.divider()

    header_left, header_right = st.columns(
        [3, 1],
        vertical_alignment="center",
    )

    with header_left:
        st.subheader("⚔️ SOUL FORGE")
        st.caption(
            "POMODORO COMMAND • ACTIVE TASK • DEEP WORK"
        )

    with header_right:

        if st.session_state.sf_pomo_running:

            if st.session_state.sf_pomo_phase == "WORK":
                st.success(
                    "FOCUS ACTIVE",
                    icon="🔥",
                )
            else:
                st.info(
                    "BREAK ACTIVE",
                    icon="☕",
                )

        elif st.session_state.sf_pomo_completed:

            st.warning(
                "PHASE COMPLETE",
                icon="⏰",
            )

        else:

            st.info(
                "READY",
                icon="🟢",
            )

    # =========================================================================
    # ACTIVE TASK
    # =========================================================================

    task_col, timer_col = st.columns(
        [1.2, 1],
        vertical_alignment="top",
    )

    with task_col:

        st.markdown("### 🎯 Active Task")

        selected_task = st.selectbox(
            "Select active task",
            task_options,
            index=task_options.index(
                st.session_state.sf_active_task
            ),
            key="sf_global_active_task_select",
            label_visibility="collapsed",
        )

        if selected_task != st.session_state.sf_active_task:

            st.session_state.sf_active_task = selected_task

            st.toast(
                f"Active task: {selected_task}",
                icon="🎯",
            )

        if selected_task == "No active task":

            st.info(
                "No active task",
                icon="⚪",
            )

        else:

            st.success(
                f"Active: {selected_task}",
                icon="🎯",
            )

        st.caption(
            "This task is attached to the current Pomodoro session."
        )

    # =========================================================================
    # TIMER
    # =========================================================================

    with timer_col:

        st.markdown("### 🍅 Pomodoro")

        display_seconds = max(
            0,
            int(st.session_state.sf_pomo_seconds),
        )

        minutes = display_seconds // 60
        seconds = display_seconds % 60

        timer_text = (
            f"{minutes:02d}:{seconds:02d}"
        )

        if st.session_state.sf_pomo_phase == "WORK":

            st.metric(
                "🔥 WORK",
                timer_text,
            )

        else:

            st.metric(
                "☕ BREAK",
                timer_text,
            )

        st.caption(
            f"Cycle {st.session_state.sf_pomo_cycle} "
            f"• Completed sessions: "
            f"{st.session_state.sf_pomo_sessions_completed}"
        )

    # =========================================================================
    # PHASE STATUS
    # =========================================================================

    phase_col, cycle_col = st.columns(2)

    with phase_col:

        if st.session_state.sf_pomo_phase == "WORK":

            st.success(
                "🔥 WORK PHASE",
                icon="🔥",
            )

        else:

            st.info(
                "☕ BREAK PHASE",
                icon="☕",
            )

    with cycle_col:

        st.metric(
            "POMODORO CYCLES",
            st.session_state.sf_pomo_cycle,
        )

    # =========================================================================
    # PROGRESS
    # =========================================================================

    if st.session_state.sf_pomo_phase == "WORK":

        total_seconds = max(
            1,
            st.session_state.sf_pomo_work_minutes * 60,
        )

    else:

        total_seconds = max(
            1,
            st.session_state.sf_pomo_break_minutes * 60,
        )

    progress = min(
        1.0,
        max(
            0.0,
            1.0
            - (
                st.session_state.sf_pomo_seconds
                / total_seconds
            ),
        ),
    )

    st.progress(progress)

    # =========================================================================
    # CONTROLS
    # =========================================================================

    start_col, pause_col, reset_col, skip_col = st.columns(4)

    with start_col:

        if st.button(
            "▶️ Start",
            key="sf_global_timer_start_button",
            use_container_width=True,
            disabled=st.session_state.sf_pomo_running,
        ):

            remaining = max(
                1,
                st.session_state.sf_pomo_seconds,
            )

            st.session_state.sf_pomo_running = True

            st.session_state.sf_pomo_end_time = (
                time.time() + remaining
            )

            st.session_state.sf_pomo_completed = False

            st.toast(
                "Pomodoro started",
                icon="🔥",
            )

    with pause_col:

        if st.button(
            "⏸️ Pause",
            key="sf_global_timer_pause_button",
            use_container_width=True,
            disabled=not st.session_state.sf_pomo_running,
        ):

            if st.session_state.sf_pomo_end_time is not None:

                remaining = max(
                    0,
                    int(
                        st.session_state.sf_pomo_end_time
                        - time.time()
                    ),
                )

                st.session_state.sf_pomo_seconds = remaining

            st.session_state.sf_pomo_running = False
            st.session_state.sf_pomo_end_time = None
            st.session_state.sf_pomo_paused_remaining = (
                st.session_state.sf_pomo_seconds
            )

            st.toast(
                "Pomodoro paused",
                icon="⏸️",
            )

    with reset_col:

        if st.button(
            "🔄 Reset",
            key="sf_global_timer_reset_button",
            use_container_width=True,
        ):

            if st.session_state.sf_pomo_phase == "WORK":

                reset_seconds = (
                    st.session_state.sf_pomo_work_minutes
                    * 60
                )

            else:

                reset_seconds = (
                    st.session_state.sf_pomo_break_minutes
                    * 60
                )

            st.session_state.sf_pomo_seconds = reset_seconds
            st.session_state.sf_pomo_paused_remaining = reset_seconds
            st.session_state.sf_pomo_running = False
            st.session_state.sf_pomo_end_time = None
            st.session_state.sf_pomo_completed = False

            st.toast(
                "Pomodoro reset",
                icon="🔄",
            )

    with skip_col:

        if st.button(
            "⏭️ Skip",
            key="sf_global_timer_skip_button",
            use_container_width=True,
        ):

            if st.session_state.sf_pomo_phase == "WORK":

                st.session_state.sf_pomo_sessions_completed += 1
                st.session_state.sf_pomo_phase = "BREAK"

                st.session_state.sf_pomo_seconds = (
                    st.session_state.sf_pomo_break_minutes
                    * 60
                )

            else:

                st.session_state.sf_pomo_cycle += 1
                st.session_state.sf_pomo_phase = "WORK"

                st.session_state.sf_pomo_seconds = (
                    st.session_state.sf_pomo_work_minutes
                    * 60
                )

            st.session_state.sf_pomo_running = False
            st.session_state.sf_pomo_end_time = None
            st.session_state.sf_pomo_completed = False

            st.toast(
                "Pomodoro phase skipped",
                icon="⏭️",
            )

    # =========================================================================
    # SETTINGS
    # =========================================================================

    with st.expander(
        "⚙️ Pomodoro Settings",
        expanded=False,
    ):

        settings_left, settings_right = st.columns(2)

        with settings_left:

            work_minutes = st.number_input(
                "Work duration",
                min_value=1,
                max_value=120,
                value=int(
                    st.session_state.sf_pomo_work_minutes
                ),
                step=1,
                key="sf_pomo_work_duration_input",
            )

        with settings_right:

            break_minutes = st.number_input(
                "Break duration",
                min_value=1,
                max_value=60,
                value=int(
                    st.session_state.sf_pomo_break_minutes
                ),
                step=1,
                key="sf_pomo_break_duration_input",
            )

        if (
            work_minutes
            != st.session_state.sf_pomo_work_minutes
            or break_minutes
            != st.session_state.sf_pomo_break_minutes
        ):

            st.session_state.sf_pomo_work_minutes = int(
                work_minutes
            )

            st.session_state.sf_pomo_break_minutes = int(
                break_minutes
            )

            if not st.session_state.sf_pomo_running:

                if st.session_state.sf_pomo_phase == "WORK":

                    st.session_state.sf_pomo_seconds = (
                        int(work_minutes) * 60
                    )

                else:

                    st.session_state.sf_pomo_seconds = (
                        int(break_minutes) * 60
                    )

        st.caption(
            "Recommended: 25 minutes work + 5 minutes break."
        )

    # =========================================================================
    # COMPLETION MESSAGE
    # =========================================================================

    if st.session_state.sf_pomo_completed:

        if st.session_state.sf_pomo_phase == "BREAK":

            st.warning(
                "⏰ Work session complete. "
                "Take your break.",
                icon="☕",
            )

        else:

            st.success(
                "⏰ Break complete. "
                "Return to the forge.",
                icon="🔥",
            )

        if st.button(
            "Dismiss notification",
            key="sf_dismiss_timer_complete",
            use_container_width=True,
        ):

            st.session_state.sf_pomo_completed = False

    # =========================================================================
    # FOOTER
    # =========================================================================

    if st.session_state.sf_pomo_running:

        if st.session_state.sf_pomo_phase == "WORK":

            st.caption(
                "🔥 Deep work active • "
                "Stay locked on the selected task."
            )

        else:

            st.caption(
                "☕ Recovery phase • "
                "Prepare for the next forge cycle."
            )

    else:

        st.caption(
            "Select a task and start the Pomodoro."
        )

    st.divider()

def _sf_focus_render_task_selector():
    """
    Backwards-compatible Soul Forge focus selector.
    """
    return _sf_focus_render_global()


# === SOUL FORGE GLOBAL HEADER END ===
# === SOUL FORGE GLOBAL HEADER CALL BEGIN ===
# === SOUL FORGE GLOBAL HEADER CALL END ===

# ============================================================================
# SOUL FORGE — GLOBAL POMODORO / ACTIVE TASK
# Rendered BEFORE the page router so it stays visible on every page.
# ============================================================================
_sf_focus_render_global()

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
elif (
    st.session_state.page
    == "Task Manager"
):
    render_task_manager()


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
