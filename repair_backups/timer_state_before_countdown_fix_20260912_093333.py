"""
SOUL FORGE — CENTRAL TIMER STATE

This module provides page-independent access to timer state.

It does not:
    - render UI
    - choose pages
    - route pages
    - implement timer calculations
"""

from __future__ import annotations

from typing import Any

import streamlit as st


TIMER_STATE_KEYS = (
    "sf_focus_active",
    "sf_focus_paused",
    "sf_focus_completed_sessions",
    "sf_focus_duration_seconds",
    "sf_focus_pause_started_at",
    "sf_focus_priority",
    "sf_focus_project",
    "sf_focus_remaining_seconds",
    "sf_focus_seconds",
    "sf_focus_session_start",
    "sf_focus_started_at",
    "sf_focus_task_id",
    "sf_focus_task_title",
    "sf_focus_total_paused_seconds",
    "sf_focus_total_seconds_today",
    "sf_timer_complete",
    "sf_timer_last_tick",
    "sf_timer_running",
    "sf_active_task",
    "sf_work_minutes",
    "sf_break_minutes",
    "sf_long_break_minutes",
    "sf_cycle",
    "sf_cycles_before_long_break",
)


DEFAULT_TIMER_STATE: dict[str, Any] = {
    "sf_focus_active": False,
    "sf_focus_paused": False,
    "sf_focus_completed_sessions": 0,
    "sf_focus_duration_seconds": 0,
    "sf_focus_pause_started_at": None,
    "sf_focus_priority": "",
    "sf_focus_project": "",
    "sf_focus_remaining_seconds": 0,
    "sf_focus_seconds": 0,
    "sf_focus_session_start": None,
    "sf_focus_started_at": None,
    "sf_focus_task_id": None,
    "sf_focus_task_title": "",
    "sf_focus_total_paused_seconds": 0,
    "sf_focus_total_seconds_today": 0,
    "sf_timer_complete": False,
    "sf_timer_last_tick": None,
    "sf_timer_running": False,
    "sf_active_task": None,
    "sf_work_minutes": 25,
    "sf_break_minutes": 5,
    "sf_long_break_minutes": 15,
    "sf_cycle": 1,
    "sf_cycles_before_long_break": 4,
}


def ensure_timer_state() -> None:
    """Initialize missing timer state without overwriting existing state."""

    for key, value in DEFAULT_TIMER_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_timer_state() -> dict[str, Any]:
    """Return a copy of the timer state."""

    ensure_timer_state()

    return {
        key: st.session_state.get(key)
        for key in TIMER_STATE_KEYS
    }


def is_timer_running() -> bool:
    """Return True when the timer is running."""

    ensure_timer_state()

    return bool(
        st.session_state.get("sf_timer_running", False)
        or st.session_state.get("sf_focus_active", False)
    )


def is_timer_paused() -> bool:
    """Return True when the timer is paused."""

    ensure_timer_state()

    return bool(
        st.session_state.get("sf_focus_paused", False)
    )


def is_timer_complete() -> bool:
    """Return True when the timer has completed."""

    ensure_timer_state()

    return bool(
        st.session_state.get("sf_timer_complete", False)
    )


def get_active_task() -> Any:
    """Return the active task or None."""

    ensure_timer_state()

    active = st.session_state.get("sf_active_task")

    if active:
        return active

    task_id = st.session_state.get("sf_focus_task_id")
    task_title = st.session_state.get(
        "sf_focus_task_title",
        "",
    )

    if task_id or task_title:
        return {
            "id": task_id,
            "title": task_title,
        }

    return None


def get_active_task_title() -> str:
    """Return a safe display title."""

    task = get_active_task()

    if task is None:
        return "No active task"

    if isinstance(task, dict):
        title = (
            task.get("title")
            or task.get("name")
            or task.get("task")
            or ""
        )

        if title:
            return str(title)

    return str(task)


def get_timer_display_seconds() -> int:
    """Return remaining seconds."""

    ensure_timer_state()

    value = st.session_state.get(
        "sf_focus_remaining_seconds",
        0,
    )

    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def format_timer_seconds(seconds: int) -> str:
    """Format seconds for display."""

    try:
        seconds = max(0, int(seconds))
    except (TypeError, ValueError):
        seconds = 0

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def get_timer_status() -> str:
    """Return READY, WORK, PAUSED, or COMPLETE."""

    if is_timer_complete():
        return "COMPLETE"

    if is_timer_paused():
        return "PAUSED"

    if is_timer_running():
        return "WORK"

    return "READY"
