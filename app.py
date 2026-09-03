from pathlib import Path
from datetime import datetime
import json
import time
import streamlit as st

# =============================================================================
# PROJECT ROOT
# Works in both Streamlit Cloud and Google Colab
# =============================================================================

if "__file__" in globals():
    ROOT = Path(__file__).resolve().parent
else:
    ROOT = Path("/content/bankai_race_control")

DATA = ROOT / "data"

PROJECTS_FILE = DATA / "projects.json"
STATUS_FILE = DATA / "status.json"




st.set_page_config(
    page_title='BANKAI RACE CONTROL',
    page_icon='🏁',
    layout='wide',
    initial_sidebar_state='expanded'
)

def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

projects = load_json(PROJECTS_FILE, [])
status = load_json(STATUS_FILE, {})

if not projects:
    st.error('No projects found in data/projects.json')
    st.stop()

project_names = [project['name'] for project in projects]

if status.get('selected_project') not in project_names:
    status['selected_project'] = project_names[0]

modes = [
    '🟢 GREEN FLAG',
    '🔴 ATTACK MODE',
    '🟡 CAUTION',
    '🔵 QUALIFYING',
    '⚫ PIT MODE',
    '⚔️ BANKAI MODE'
]

mode_descriptions = {
    '🟢 GREEN FLAG': 'Normal development pace.',
    '🔴 ATTACK MODE': 'Maximum priority. Push the next milestone.',
    '🟡 CAUTION': 'Investigate failures before pushing forward.',
    '🔵 QUALIFYING': 'Focus on performance, tests and optimization.',
    '⚫ PIT MODE': 'Maintenance, refactoring and infrastructure.',
    '⚔️ BANKAI MODE': 'Final-boss development mode. Full concentration.'
}

selected_name = st.sidebar.selectbox(
    '🏎️ SELECT REPOSITORY',
    project_names,
    index=project_names.index(status['selected_project'])
)

selected_project = next(
    project for project in projects
    if project['name'] == selected_name
)

status['selected_project'] = selected_name

selected_mode = st.sidebar.selectbox(
    '⚙️ RACE MODE',
    modes,
    index=modes.index(status.get('mode', modes[0]))
)

if selected_mode != status.get('mode'):
    status['mode'] = selected_mode
    status['last_radio'] = f'TEAM → DRIVER: Mode changed to {selected_mode}. Push smart.'
    status['radio_history'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'channel': 'TEAM → DRIVER',
        'message': status['last_radio']
    })

status['mode'] = selected_mode

st.sidebar.divider()
st.sidebar.subheader('🏁 RACE CONTROL')
st.sidebar.caption(mode_descriptions[selected_mode])

st.sidebar.metric('DRIVER', 'MAX')
st.sidebar.metric('PROJECT', selected_project['name'])
st.sidebar.metric('PROGRESS', f"{selected_project['progress']}%")

st.sidebar.divider()
st.sidebar.caption('⚔️ BLEACH × F1 × AI')
st.sidebar.caption('🏎️ MAX MODE ACTIVE')

# -------------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------------

st.title('🏁 BANKAI RACE CONTROL')
st.subheader('PERSONAL AI / SOFTWARE PROJECT COMMAND CENTER')
st.caption('⚔️ BLEACH × F1 • DRIVER: MAX • TEAM RADIO ONLINE')

header_left, header_mid, header_right = st.columns(3)

with header_left:
    st.metric('🏎️ DRIVER', 'MAX')

with header_mid:
    st.metric('⚙️ MODE', selected_mode)

with header_right:
    st.metric('🏁 STATUS', selected_project['status'])

st.divider()

# -------------------------------------------------------------------------
# MAX MESSAGE
# -------------------------------------------------------------------------

quotes = {
    '🟢 GREEN FLAG': 'Stay focused. Build one lap at a time.',
    '🔴 ATTACK MODE': 'Push hard, but keep the car under control.',
    '🟡 CAUTION': 'No unnecessary risks. Find the problem first.',
    '🔵 QUALIFYING': 'Every millisecond matters. Optimize the details.',
    '⚫ PIT MODE': 'Reset, repair and come back stronger.',
    '⚔️ BANKAI MODE': 'Final lap mentality. Maximum concentration.'
}

st.info(f'🏎️ MAX MODE — {quotes[selected_mode]}')

# -------------------------------------------------------------------------
# PROJECT TELEMETRY
# -------------------------------------------------------------------------

st.header('📡 PROJECT TELEMETRY')

telemetry = st.columns(4)

with telemetry[0]:
    st.metric('REPOSITORY', selected_project['repository'])

with telemetry[1]:
    st.metric('PHASE', selected_project['phase'])

with telemetry[2]:
    st.metric('PRIORITY', selected_project['priority'])

with telemetry[3]:
    st.metric('TECH STACK', selected_project['technology'])

st.progress(
    min(max(selected_project['progress'], 0), 100) / 100,
    text=f"Project Progress — {selected_project['progress']}%"
)

st.divider()

# -------------------------------------------------------------------------
# F1 TIMER CONTROL
# -------------------------------------------------------------------------

st.header('⏱️ F1 RACE TIMER')

timer_col1, timer_col2, timer_col3, timer_col4 = st.columns(4)

session_seconds = int(status.get('session_seconds', 0))

if status.get('session_running') and status.get('session_started'):
    try:
        started = datetime.fromisoformat(status['session_started'])
        session_seconds += max(
            0,
            int((datetime.now() - started).total_seconds())
        )
    except Exception:
        pass

minutes = session_seconds // 60
seconds = session_seconds % 60

with timer_col1:
    st.metric('SESSION TIME', f'{minutes:02d}:{seconds:02d}')

with timer_col2:
    st.metric(
        'CURRENT LAP',
        f"{status.get('current_lap', 1)} / {status.get('target_lap', 10)}"
    )

with timer_col3:
    remaining_laps = max(
        0,
        int(status.get('target_lap', 10)) - int(status.get('current_lap', 1))
    )
    st.metric('LAPS REMAINING', remaining_laps)

with timer_col4:
    st.metric('TASK', status.get('current_task', selected_project['phase']))

timer_buttons = st.columns(4)

with timer_buttons[0]:
    if st.button('▶️ START SESSION', use_container_width=True):
        status['session_running'] = True
        status['session_started'] = datetime.now().isoformat(timespec='seconds')
        status['last_radio'] = 'TEAM → DRIVER: Green flag. Session started.'
        status['radio_history'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'channel': 'TEAM → DRIVER',
            'message': status['last_radio']
        })
        save_json(STATUS_FILE, status)
        st.rerun()

with timer_buttons[1]:
    if st.button('⏸️ PAUSE', use_container_width=True):
        if status.get('session_running') and status.get('session_started'):
            try:
                started = datetime.fromisoformat(status['session_started'])
                elapsed = max(0, int((datetime.now() - started).total_seconds()))
                status['session_seconds'] = session_seconds
            except Exception:
                pass
        status['session_running'] = False
        status['session_started'] = None
        save_json(STATUS_FILE, status)
        st.rerun()

with timer_buttons[2]:
    if st.button('🔄 RESET', use_container_width=True):
        status['session_running'] = False
        status['session_started'] = None
        status['session_seconds'] = 0
        status['current_lap'] = 1
        save_json(STATUS_FILE, status)
        st.rerun()

with timer_buttons[3]:
    if st.button('🏁 NEXT LAP', use_container_width=True):
        status['current_lap'] = min(
            int(status.get('current_lap', 1)) + 1,
            int(status.get('target_lap', 10))
        )
        status['last_radio'] = f'TEAM → DRIVER: Lap {status["current_lap"]} confirmed. Push the next sector.'
        status['radio_history'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'channel': 'TEAM → DRIVER',
            'message': status['last_radio']
        })
        save_json(STATUS_FILE, status)
        st.rerun()

if status.get('session_running'):
    time.sleep(1)
    st.rerun()

st.divider()

# -------------------------------------------------------------------------
# DRIVER / TEAM RADIO
# -------------------------------------------------------------------------

st.header('📻 DRIVER ↔ TEAM RADIO')

radio_left, radio_right = st.columns(2)

with radio_left:
    st.subheader('🏎️ DRIVER → TEAM')

    driver_messages = [
        'Car feels good. Continue pushing.',
        'Need more performance from the next phase.',
        'Something is wrong. Check telemetry.',
        'Ready for the next lap.',
        'I am pushing now.',
        'Development target completed.'
    ]

    driver_message = st.selectbox(
        'Driver communication',
        driver_messages,
        key='driver_message_select'
    )

    if st.button('📡 SEND DRIVER RADIO', use_container_width=True):
        message = f'DRIVER → TEAM: {driver_message}'
        status['driver_message'] = driver_message
        status['last_radio'] = message
        status['radio_history'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'channel': 'DRIVER → TEAM',
            'message': message
        })
        save_json(STATUS_FILE, status)
        st.success(message)

    driver_audio = DATA / 'audio' / 'driver_radio.wav'
    if driver_audio.exists():
        st.audio(driver_audio.read_bytes(), format='audio/wav')

with radio_right:
    st.subheader('🧑‍💻 TEAM → DRIVER')

    team_messages = [
        'Telemetry looks good. Continue.',
        'Push the next lap.',
        'Box, we need maintenance.',
        'Attack mode is confirmed.',
        'Caution. Investigate before continuing.',
        'Excellent work. Keep the rhythm.'
    ]

    team_message = st.selectbox(
        'Team communication',
        team_messages,
        key='team_message_select'
    )

    if st.button('📡 SEND TEAM RADIO', use_container_width=True):
        message = f'TEAM → DRIVER: {team_message}'
        status['team_message'] = team_message
        status['last_radio'] = message
        status['radio_history'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'channel': 'TEAM → DRIVER',
            'message': message
        })
        save_json(STATUS_FILE, status)
        st.success(message)

    team_audio = DATA / 'audio' / 'team_radio.wav'
    if team_audio.exists():
        st.audio(team_audio.read_bytes(), format='audio/wav')

st.divider()

st.subheader('📻 LAST RADIO CALL')
st.warning(status.get('last_radio', 'Radio offline.'))

# -------------------------------------------------------------------------
# RADIO HISTORY
# -------------------------------------------------------------------------

with st.expander('📜 RADIO HISTORY', expanded=False):
    history = status.get('radio_history', [])

    if not history:
        st.caption('No radio calls yet.')
    else:
        for entry in reversed(history[-20:]):
            st.write(
                f"**{entry.get('time', '--:--:--')}** — "
                f"{entry.get('channel', 'RADIO')} — "
                f"{entry.get('message', '')}"
            )

# -------------------------------------------------------------------------
# CURRENT DEVELOPMENT TASK
# -------------------------------------------------------------------------

st.divider()
st.header('🎯 CURRENT DEVELOPMENT TARGET')

task_col1, task_col2 = st.columns([3, 1])

with task_col1:
    task = st.text_input(
        'Current task',
        value=status.get('current_task', selected_project['phase'])
    )

with task_col2:
    if st.button('💾 SAVE TASK', use_container_width=True):
        status['current_task'] = task
        status['last_updated'] = datetime.now().isoformat(timespec='seconds')
        save_json(STATUS_FILE, status)
        st.success('Task saved to status.json')

st.info(
    f"🏁 Current target: **{status.get('current_task', selected_project['phase'])}**"
)

# -------------------------------------------------------------------------
# ALL PROJECTS
# -------------------------------------------------------------------------

st.divider()
st.header('🏆 PROJECT GRID')

grid = st.columns(3)

for index, project in enumerate(projects):
    with grid[index % 3]:
        with st.container(border=True):
            st.subheader(f"🏎️ {project['name']}")
            st.caption(project['repository'])
            st.progress(
                min(max(project['progress'], 0), 100) / 100,
                text=f"{project['progress']}%"
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric('STATUS', project['status'])

            with c2:
                st.metric('PHASE', project['phase'])

            st.caption(project['technology'])

# -------------------------------------------------------------------------
# JSON STATUS VIEW
# -------------------------------------------------------------------------

st.divider()

with st.expander('🗄️ LIVE STATUS.JSON', expanded=False):
    st.json(status)

# -------------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------------

st.divider()
footer1, footer2, footer3 = st.columns(3)

with footer1:
    st.caption('⚔️ BANKAI RACE CONTROL')

with footer2:
    st.caption('🏎️ MAX MODE')

with footer3:
    st.caption('🏁 RACE CONTROL ONLINE')

status['last_updated'] = datetime.now().isoformat(timespec='seconds')
save_json(STATUS_FILE, status)