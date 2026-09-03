
import json
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "projects.json"
CSS_FILE = ROOT / "styles" / "dashboard.css"


st.set_page_config(
    page_title="Bankai Race Control",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

if CSS_FILE.exists():
    st.markdown(
        f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD DATA
# ============================================================

with open(DATA_FILE, "r", encoding="utf-8") as file:
    projects = json.load(file)


# ============================================================
# HELPERS
# ============================================================

def status_class(status: str) -> str:
    status = status.upper()

    if status == "ACTIVE":
        return "status-active"

    if status == "RESEARCH":
        return "status-research"

    if status == "COMPLETED":
        return "status-completed"

    return "status-paused"


def calculate_reiatsu(progress: int) -> int:
    return min(100, max(0, progress + 8))


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚔️ BANKAI")

    st.caption("RACE CONTROL")

    st.divider()

    page = st.radio(
        "COMMAND",
        [
            "Command Center",
            "Projects",
            "AI Lab",
            "Race Control",
            "Tasks",
            "Analytics",
        ],
    )

    st.divider()

    st.caption("SYSTEM")

    st.write("🟢 CORE ONLINE")
    st.write("🟢 DATA ONLINE")
    st.write("🟢 UI ONLINE")

    st.divider()

    st.caption("BANKAI // V1.0")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="command-header">

        <div class="command-title">
            BANKAI RACE CONTROL
        </div>

        <div class="command-subtitle">
            PERSONAL AI / SOFTWARE PROJECT COMMAND CENTER
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    st.markdown(
        '<div class="section-title">SYSTEM TELEMETRY</div>',
        unsafe_allow_html=True,
    )

    total_projects = len(projects)

    active_projects = len(
        [p for p in projects if p["status"] == "ACTIVE"]
    )

    completed_projects = len(
        [p for p in projects if p["status"] == "COMPLETED"]
    )

    overall_progress = round(
        sum(p["progress"] for p in projects) / total_projects
    )

    reiatsu = calculate_reiatsu(overall_progress)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "PROJECTS",
            total_projects,
        )

    with col2:
        st.metric(
            "ACTIVE",
            active_projects,
        )

    with col3:
        st.metric(
            "OVERALL PROGRESS",
            f"{overall_progress}%",
        )

    with col4:
        st.metric(
            "REIATSU",
            f"{reiatsu}%",
        )


    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">PROJECT GRID</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)

    for index, project in enumerate(projects):

        with cols[index % 3]:

            progress = project["progress"]

            st.markdown(
                f"""
                <div class="project-card">

                    <div class="project-name">
                        {project["name"]}
                    </div>

                    <div class="project-type">
                        {project["type"]}
                    </div>

                    <div class="project-description">
                        {project["description"]}
                    </div>

                    <div>
                        <strong>{progress}%</strong>
                    </div>

                    <div class="progress-track">
                        <div
                            class="progress-fill"
                            style="width:{progress}%"
                        ></div>
                    </div>

                    <div class="project-meta">
                        <span>
                            {project["phase"]}
                        </span>

                        <span class="{status_class(project["status"])}">
                            {project["status"]}
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


    # --------------------------------------------------------
    # RACE CONTROL + REIATSU
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">RACE CONTROL</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:

        st.markdown(
            f"""
            <div class="race-card">

                <div class="race-label">
                    🏎️ DEVELOPMENT TELEMETRY
                </div>

                <h2>
                    LAP {min(24, overall_progress // 4)}/24
                </h2>

                <p>
                    Overall development progression
                </p>

                <div class="progress-track">
                    <div
                        class="progress-fill"
                        style="width:{overall_progress}%"
                    ></div>
                </div>

                <p>
                    Sector 1 — Foundation
                </p>

                <p>
                    Sector 2 — Implementation
                </p>

                <p>
                    Sector 3 — Testing
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            f"""
            <div class="reiatsu-card">

                <div class="reiatsu-title">
                    ⚔️ SOUL SOCIETY SYSTEM
                </div>

                <div class="reiatsu-value">
                    {reiatsu}%
                </div>

                <p>
                    CURRENT REIATSU
                </p>

                <div class="progress-track">
                    <div
                        class="progress-fill"
                        style="width:{reiatsu}%"
                    ></div>
                </div>

                <br>

                <p>
                    ZANPAKUTO — {overall_progress}%
                </p>

                <p>
                    BANKAI — {min(100, overall_progress + 5)}%
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # NEXT ACTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">NEXT ACTION</div>',
        unsafe_allow_html=True,
    )

    active = [
        p for p in projects
        if p["status"] in ["ACTIVE", "RESEARCH"]
    ]

    if active:

        target = min(
            active,
            key=lambda x: x["progress"]
        )

        st.info(
            f'⚡ {target["name"]} → {target["next"]}'
        )


    # --------------------------------------------------------
    # TIMELINE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">MISSION TIMELINE</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="timeline">

            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-title">
                    PROJECT FOUNDATION
                </div>
                <div class="timeline-description">
                    Architecture and repository setup
                </div>
            </div>

            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-title">
                    DATA PHASE
                </div>
                <div class="timeline-description">
                    Dataset and knowledge acquisition
                </div>
            </div>

            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-title">
                    MODEL ENGINEERING
                </div>
                <div class="timeline-description">
                    AI and software implementation
                </div>
            </div>

            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-title">
                    TESTING
                </div>
                <div class="timeline-description">
                    Validation and quality control
                </div>
            </div>

            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-title">
                    DEPLOYMENT
                </div>
                <div class="timeline-description">
                    Final integration and release
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECTS PAGE
# ============================================================

elif page == "Projects":

    st.header("⚔️ PROJECT ARCHIVE")

    for project in projects:

        with st.expander(
            f'{project["name"]} — {project["progress"]}%'
        ):

            st.write(project["description"])

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "PROGRESS",
                    f'{project["progress"]}%'
                )

            with col2:
                st.metric(
                    "LAP",
                    project["lap"]
                )

            with col3:
                st.metric(
                    "TESTS",
                    project["tests"]
                )

            st.write(
                f'**Current Phase:** {project["phase"]}'
            )

            st.write(
                f'**Next:** {project["next"]}'
            )


# ============================================================
# AI LAB
# ============================================================

elif page == "AI Lab":

    st.header("🧠 AI LAB")

    ai_projects = [
        p for p in projects
        if "AI" in p["type"]
        or "NEURAL" in p["type"]
        or "MACHINE" in p["type"]
    ]

    if not ai_projects:

        st.info("No AI projects registered.")

    else:

        for project in ai_projects:

            st.subheader(project["name"])

            st.progress(
                project["progress"] / 100
            )

            st.caption(
                f'{project["phase"]} → {project["next"]}'
            )


# ============================================================
# RACE CONTROL
# ============================================================

elif page == "Race Control":

    st.header("🏎️ RACE CONTROL")

    st.subheader("Development Grid")

    for project in projects:

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write(project["name"])

        with col2:
            st.write(
                f'LAP {project["lap"]}'
            )

        with col3:
            st.progress(
                project["progress"] / 100
            )

        with col4:
            st.write(project["status"])


# ============================================================
# TASKS
# ============================================================

elif page == "Tasks":

    st.header("📋 TASK CONTROL")

    tasks = {
        "TODO": [
            "Design Patrick Jane dataset",
            "Build feature extraction pipeline",
            "Add GitHub project synchronization",
        ],
        "IN PROGRESS": [
            "Einstein reasoning engine",
            "Project command center",
        ],
        "DONE": [
            "Streamlit foundation",
            "Dashboard theme",
            "Project telemetry",
        ],
    }

    columns = st.columns(3)

    for column, (state, items) in zip(
        columns,
        tasks.items()
    ):

        with column:

            st.subheader(state)

            for item in items:

                st.checkbox(
                    item,
                    value=(state == "DONE"),
                    key=f"{state}-{item}",
                )


# ============================================================
# ANALYTICS
# ============================================================

elif page == "Analytics":

    st.header("📊 PROJECT ANALYTICS")

    names = [
        p["name"]
        for p in projects
    ]

    progress = [
        p["progress"]
        for p in projects
    ]

    st.bar_chart(
        {
            "Project Progress": dict(
                zip(names, progress)
            )
        }
    )

    st.subheader("Project Statistics")

    for project in projects:

        st.write(
            f'**{project["name"]}** — '
            f'{project["progress"]}%'
        )

        st.progress(
            project["progress"] / 100
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BANKAI RACE CONTROL // "
    "BLEACH × F1 × AI // "
    "PERSONAL PROJECT COMMAND CENTER"
)
