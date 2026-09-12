"""
SOUL FORGE — INDEPENDENT TIMER BAR

This component only displays and controls the timer.

It has no knowledge of:
    - Task Manager
    - Command Center
    - Knowledge
    - Chat
    - Agentic AI
    - Ruflo
    - Settings
    - page routing
"""

from __future__ import annotations

import streamlit as st

from app.core.timer.timer_state import (
    ensure_timer_state,
    format_timer_seconds,
    get_active_task_title,
    get_timer_display_seconds,
    get_timer_status,
    is_timer_complete,
    is_timer_paused,
    is_timer_running,
)

from app.core.timer.pomodoro_engine import (
    _sf_focus_pause,
    _sf_focus_restart,
    _sf_focus_start,
)


def _timer_start() -> None:
    """Start the timer engine."""

    _sf_focus_start()


def _timer_pause() -> None:
    """Pause the timer engine."""

    _sf_focus_pause()


def _timer_reset() -> None:
    """Restart the current timer session."""

    _sf_focus_restart()


def render_timer_bar() -> None:
    """Render the independent timer component."""

    ensure_timer_state()

    task = get_active_task_title()
    seconds = get_timer_display_seconds()

    timer_text = format_timer_seconds(seconds)
    status = get_timer_status()

    st.markdown(
        "### SOUL FORGE  ·  SYSTEM ONLINE"
    )

    if task == "No active task":
        st.caption(
            "ACTIVE TASK  ·  No active task"
        )
    else:
        st.caption(
            f"ACTIVE TASK  ·  {task}"
        )

    (
        task_col,
        mode_col,
        time_col,
        action_col,
        reset_col,
    ) = st.columns(
        [2.4, 1.0, 1.2, 0.9, 0.9]
    )

    with task_col:
        st.write("ONE-TASK")

    with mode_col:
        st.write(status)

    with time_col:
        st.write(f"**{timer_text}**")

    with action_col:

        if is_timer_running() and not is_timer_paused():

            if st.button(
                "PAUSE",
                key="sf_independent_timer_pause",
                use_container_width=True,
            ):
                _timer_pause()
                st.rerun()

        else:

            if st.button(
                "START",
                key="sf_independent_timer_start",
                use_container_width=True,
            ):
                _timer_start()
                st.rerun()

    with reset_col:

        if st.button(
            "RESET",
            key="sf_independent_timer_reset",
            use_container_width=True,
        ):
            _timer_reset()
            st.rerun()

    if is_timer_complete():
        st.success("Timer Complete")

    st.divider()
