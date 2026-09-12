# =============================================================================
# SOUL FORGE — POMODORO TIMER ENGINE
# Extracted from app/ui/bankai_race_control.py
# =============================================================================

from __future__ import annotations

from datetime import datetime

import streamlit as st


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

