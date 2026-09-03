from pathlib import Path
import json

import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent
PROJECTS_FILE = ROOT / 'data' / 'projects.json'


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title='Bankai Race Control',
    page_icon='🏁',
    layout='wide',
    initial_sidebar_state='expanded',
)


# ============================================================
# DATA
# ============================================================

def load_projects():
    if not PROJECTS_FILE.exists():
        return []

    try:
        data = json.loads(
            PROJECTS_FILE.read_text(encoding='utf-8')
        )

        if isinstance(data, dict):
            return data.get('projects', [])

        if isinstance(data, list):
            return data

    except Exception:
        return []

    return []


projects = load_projects()


# ============================================================
# TELEMETRY
# ============================================================

total_projects = len(projects)

if total_projects:
    overall_progress = round(
        sum(
            int(project.get('progress', 0))
            for project in projects
        ) / total_projects
    )
else:
    overall_progress = 0


active_projects = sum(
    1
    for project in projects
    if str(project.get('status', '')).upper() == 'ACTIVE'
)

research_projects = sum(
    1
    for project in projects
    if str(project.get('status', '')).upper() == 'RESEARCH'
)

paused_projects = sum(
    1
    for project in projects
    if str(project.get('status', '')).upper() == 'PAUSED'
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title('🏁 RACE CONTROL')

    st.caption('BANKAI RACE CONTROL V3')

    st.divider()

    page = st.radio(
        'COMMAND CENTER',
        [
            '🏁 Command Center',
            '⚔️ Project Armory',
            '🏎️ Race Telemetry',
            '🧠 AI Lab',
            '📋 Race Tasks',
            '📊 Analytics',
        ],
    )

    st.divider()

    st.subheader('🏎️ DRIVER')

    st.metric(
        'MAX',
        'VERSTAPPEN',
    )

    st.caption('FOCUS • PRECISION • ATTACK')

    st.divider()

    st.subheader('⚔️ REIATSU')

    st.metric(
        'PROJECT POWER',
        f'{overall_progress}%',
    )

    st.progress(
        overall_progress / 100
    )

    st.caption('Overall development power')


# ============================================================
# COMMAND CENTER
# ============================================================

if page == '🏁 Command Center':

    st.title('🏁 BANKAI RACE CONTROL')

    st.subheader(
        'PERSONAL AI / SOFTWARE PROJECT COMMAND CENTER'
    )

    st.caption(
        'BLEACH × RED BULL RACING × MAX VERSTAPPEN'
    )

    st.divider()

    st.info(
        '🏎️ MAX MODE — Stay focused. Reduce mistakes. Push the next lap.'
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('🏁 PROJECTS', total_projects)

    with col2:
        st.metric('🔥 ACTIVE', active_projects)

    with col3:
        st.metric('🧠 RESEARCH', research_projects)

    with col4:
        st.metric('⚠️ PAUSED', paused_projects)

    st.divider()

    st.subheader('⚔️ REIATSU — OVERALL PROJECT POWER')

    st.progress(overall_progress / 100)

    st.metric(
        'CURRENT POWER',
        f'{overall_progress}%',
    )

    st.divider()

    st.subheader('🏎️ CURRENT GRID')

    grid_columns = st.columns(3)

    for index, project in enumerate(projects):

        with grid_columns[index % 3]:

            with st.container(border=True):

                name = project.get('name', 'Unknown Project')
                progress = int(project.get('progress', 0))
                status = project.get('status', 'UNKNOWN')
                phase = project.get('phase', 'Unknown')
                technology = project.get('technology', 'Unknown')
                health = project.get('health', 'UNKNOWN')

                st.subheader(f'⚔️ {name}')

                st.caption(technology)

                st.progress(progress / 100)

                c1, c2 = st.columns(2)

                with c1:
                    st.metric('LAP', f'{progress}%')

                with c2:
                    st.metric('STATUS', status)

                st.write(f'**Phase:** {phase}')
                st.write(f'**Health:** {health}')

    st.divider()

    st.subheader('🔥 BANKAI MINDSET')

    st.warning(
        'Start strong. Stay precise. Finish the lap. Then unlock Bankai.'
    )


# ============================================================
# PROJECT ARMORY
# ============================================================

elif page == '⚔️ Project Armory':

    st.title('⚔️ PROJECT ARMORY')

    st.caption(
        'Every project is a Zanpakuto. Every milestone unlocks power.'
    )

    st.divider()

    search = st.text_input(
        '🔎 SEARCH PROJECTS',
        placeholder='Enter project name...',
    )

    filtered = projects

    if search:
        filtered = [
            project
            for project in projects
            if search.lower() in project.get('name', '').lower()
        ]

    for project in filtered:

        with st.container(border=True):

            left, middle, right = st.columns([3, 4, 2])

            progress = int(project.get('progress', 0))

            with left:
                st.subheader(
                    f"⚔️ {project.get('name', 'Unknown')}"
                )
                st.caption(
                    project.get('technology', 'Unknown')
                )

            with middle:
                st.write(
                    f"**Phase:** {project.get('phase', 'Unknown')}"
                )
                st.progress(progress / 100)
                st.caption(f'Progress: {progress}%')

            with right:
                st.metric(
                    'STATUS',
                    project.get('status', 'UNKNOWN'),
                )
                st.caption(
                    f"Health: {project.get('health', 'UNKNOWN')}"
                )


# ============================================================
# RACE TELEMETRY
# ============================================================

elif page == '🏎️ Race Telemetry':

    st.title('🏎️ RACE TELEMETRY')

    st.caption('Project performance and development telemetry.')

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric('GRID SIZE', total_projects)

    with c2:
        st.metric('ACTIVE CARS', active_projects)

    with c3:
        st.metric('AVERAGE LAP', f'{overall_progress}%')

    st.divider()

    st.subheader('🏁 DEVELOPMENT LAPS')

    for project in projects:

        name = project.get('name', 'Unknown')
        progress = int(project.get('progress', 0))

        st.write(f'**{name}**')
        st.progress(progress / 100)


# ============================================================
# AI LAB
# ============================================================

elif page == '🧠 AI Lab':

    st.title('🧠 AI LAB')

    st.caption('Artificial intelligence and machine learning command center.')

    st.divider()

    ai_projects = [
        project
        for project in projects
        if any(
            keyword in str(project.get('technology', '')).lower()
            for keyword in ['ai', 'ml', 'machine', 'python', 'ann']
        )
    ]

    if not ai_projects:
        st.info('No AI projects detected.')

    for project in ai_projects:

        with st.container(border=True):

            st.subheader(
                f"🧠 {project.get('name', 'AI Project')}"
            )

            st.caption(
                project.get('technology', 'Unknown')
            )

            st.progress(
                int(project.get('progress', 0)) / 100
            )


# ============================================================
# TASKS
# ============================================================

elif page == '📋 Race Tasks':

    st.title('📋 RACE TASKS')

    st.caption('Next actions required to complete the current development lap.')

    st.divider()

    tasks = [
        'Complete current milestone',
        'Run automated tests',
        'Review GitHub changes',
        'Update documentation',
        'Commit stable changes',
        'Push changes to GitHub',
        'Prepare next development lap',
    ]

    for index, task in enumerate(tasks):
        st.checkbox(task, key=f'race_task_{index}')

    st.divider()

    st.success(
        '🏁 Complete the current lap before starting the next one.'
    )


# ============================================================
# ANALYTICS
# ============================================================

elif page == '📊 Analytics':

    st.title('📊 PROJECT ANALYTICS')

    st.caption('Development performance across your project grid.')

    st.divider()

    progress_data = {
        project.get('name', 'Unknown'): int(
            project.get('progress', 0)
        )
        for project in projects
    }

    if progress_data:
        st.subheader('🏎️ PROJECT PROGRESS')
        st.bar_chart(progress_data)

    st.divider()

    status_data = {}

    for project in projects:
        status = str(
            project.get('status', 'UNKNOWN')
        )
        status_data[status] = status_data.get(status, 0) + 1

    if status_data:
        st.subheader('⚔️ PROJECT STATUS')
        st.bar_chart(status_data)


# ============================================================
# FOOTER
# ============================================================

st.divider()

f1, f2, f3 = st.columns(3)

with f1:
    st.caption('⚔️ BANKAI RACE CONTROL')

with f2:
    st.caption('🏎️ MAX MODE')

with f3:
    st.caption('🏁 RACE CONTROL ONLINE')
