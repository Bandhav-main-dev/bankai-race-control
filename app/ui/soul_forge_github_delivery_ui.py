from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st

from app.services.soul_forge_github_delivery import GitHubDelivery
from app.services.soul_forge_github_delivery import extract_json


PROJECT = Path('/content/BANKAI-RACE-CONTROL')


def _files():
    result = {}
    ignored = {
        '.git',
        '.venv',
        'venv',
        '__pycache__',
        '.pytest_cache',
        'repair_backups',
        'node_modules',
    }

    for path in PROJECT.rglob('*'):
        if not path.is_file():
            continue

        relative = path.relative_to(PROJECT)

        if any(part in ignored for part in relative.parts):
            continue

        if path.stat().st_size > 500000:
            continue

        try:
            result[relative.as_posix()] = path.read_text(
                encoding='utf-8',
                errors='replace',
            )
        except Exception:
            pass

    return result


def _ai(prompt):
    try:
        from app.providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider()

        try:
            result = provider.ask(prompt)
        except TypeError:
            result = provider.ask(prompt=prompt)

        if isinstance(result, dict):
            for key in ['content', 'text', 'response', 'answer']:
                if result.get(key):
                    return str(result[key])

        return str(result)

    except Exception:
        import requests

        key = os.getenv('OPENROUTER_API_KEY')

        if not key:
            raise RuntimeError(
                'OPENROUTER_API_KEY is not configured.'
            )

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': st.session_state.get(
                    'sf_delivery_model',
                    'openai/gpt-5-mini',
                ),
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ],
                'temperature': 0.1,
            },
            timeout=180,
        )

        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


def _safe_write(files):
    written = []

    for relative, content in files.items():
        relative = str(relative).replace('\\', '/')

        if relative.startswith('/'):
            raise ValueError(f'Absolute path rejected: {relative}')

        if relative == '.env' or relative.endswith('/.env'):
            raise ValueError('.env generation is prohibited.')

        target = (PROJECT / relative).resolve()

        if PROJECT not in target.parents:
            raise ValueError(f'Path traversal rejected: {relative}')

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding='utf-8')
        written.append(relative)

    return written


def _generation_prompt(task, remote, local):
    remote_text = json.dumps(remote, indent=2)[:50000]
    local_text = json.dumps(
        {k: v[:10000] for k, v in list(local.items())[:100]},
        indent=2,
    )[:70000]

    return (
        'You are the senior autonomous software engineering agent for SOUL FORGE.\n\n'
        'USER TASK:\n' + task + '\n\n'
        'REMOTE REPOSITORY:\n' + remote_text + '\n\n'
        'LOCAL PROJECT:\n' + local_text + '\n\n'
        'Return ONLY valid JSON with this structure:\n'
        '{\n'
        '  "summary": "implementation summary",\n'
        '  "files": {"relative/path.py": "complete file content"},\n'
        '  "dependencies": [],\n'
        '  "tests": [],\n'
        '  "browser_tests": []\n'
        '}\n\n'
        'Rules:\n'
        '- Support multiple files.\n'
        '- Include every required new or modified file.\n'
        '- Preserve existing architecture.\n'
        '- Reuse existing modules where possible.\n'
        '- Never create .env.\n'
        '- Never hard-code secrets.\n'
        '- Use relative paths only.\n'
        '- Include tests when appropriate.\n'
        '- If UI changes, include browser testing information.\n'
        '- Do not claim tests passed unless they actually ran.'
    )


def _repair_prompt(task, failures, files):
    failures_text = json.dumps(failures, indent=2)
    files_text = json.dumps(
        {k: v[:10000] for k, v in list(files.items())[:100]},
        indent=2,
    )[:70000]

    return (
        'You are the autonomous debugging agent for SOUL FORGE.\n\n'
        'ORIGINAL TASK:\n' + task + '\n\n'
        'FAILURES:\n' + failures_text + '\n\n'
        'CURRENT PROJECT FILES:\n' + files_text + '\n\n'
        'Diagnose the root cause and repair it.\n'
        'Return ONLY JSON.\n'
        '{\n'
        '  "summary": "repair summary",\n'
        '  "files": {"relative/path.py": "complete corrected content"}\n'
        '}\n'
        'Do not create .env.\n'
        'Do not hard-code secrets.'
    )


def _browser_test():
    try:
        import requests
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {
            'passed': False,
            'output': f'Playwright unavailable: {exc}',
        }

    process = None
    screenshots = PROJECT / 'repair_backups' / 'browser_screenshots'
    screenshots.mkdir(parents=True, exist_ok=True)

    try:
        process = subprocess.Popen(
            [
                sys.executable,
                '-m',
                'streamlit',
                'run',
                'app/ui/bankai_race_control.py',
                '--server.port',
                '8501',
                '--server.address',
                '127.0.0.1',
                '--server.headless',
                'true',
            ],
            cwd=PROJECT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        ready = False

        for _ in range(45):
            try:
                response = requests.get(
                    'http://127.0.0.1:8501',
                    timeout=3,
                )
                if response.status_code < 500:
                    ready = True
                    break
            except Exception:
                pass
            time.sleep(1)

        if not ready:
            return {
                'passed': False,
                'output': 'Streamlit did not become ready.',
            }

        errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={'width': 1440, 'height': 1000}
            )

            page.on(
                'console',
                lambda msg: errors.append(msg.text)
                if msg.type == 'error' else None,
            )

            page.on(
                'pageerror',
                lambda error: errors.append(str(error)),
            )

            page.goto(
                'http://127.0.0.1:8501',
                wait_until='domcontentloaded',
                timeout=30000,
            )

            page.wait_for_timeout(4000)

            body = page.locator('body').inner_text()

            if not body.strip():
                raise RuntimeError('Browser loaded a blank page.')

            page.screenshot(
                path=str(screenshots / '01_home.png'),
                full_page=True,
            )

            browser.close()

        if errors:
            return {
                'passed': False,
                'output': '\n'.join(errors),
            }

        return {
            'passed': True,
            'output': 'Browser smoke test passed.',
        }

    except Exception as exc:
        return {
            'passed': False,
            'output': str(exc),
        }

    finally:
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass


def render_github_delivery():
    st.subheader('GitHub Delivery')
    st.caption(
        'Autonomous multi-file generation, validation, repair and PR delivery.'
    )

    if 'sf_gh_verified' not in st.session_state:
        st.session_state.sf_gh_verified = False
    if 'sf_gh_token' not in st.session_state:
        st.session_state.sf_gh_token = None
    if 'sf_gh_repos' not in st.session_state:
        st.session_state.sf_gh_repos = []
    if 'sf_gh_target' not in st.session_state:
        st.session_state.sf_gh_target = None
    if 'sf_manifest' not in st.session_state:
        st.session_state.sf_manifest = None
    if 'sf_engineering' not in st.session_state:
        st.session_state.sf_engineering = None
    if 'sf_validation' not in st.session_state:
        st.session_state.sf_validation = None
    if 'sf_browser' not in st.session_state:
        st.session_state.sf_browser = None

    st.markdown('### 1. GitHub Access')

    token = st.text_input(
        'Fine-grained GitHub PAT',
        type='password',
    )

    if st.button('Verify GitHub Access', type='primary'):
        try:
            client = GitHubDelivery(token, PROJECT)
            user = client.verify_access()
            repos = client.list_repositories()

            st.session_state.sf_gh_token = token
            st.session_state.sf_gh_repos = repos
            st.session_state.sf_gh_verified = True

            st.success(
                f'GitHub access verified for @{user.get("login", "user")}'
            )
        except Exception as exc:
            st.error(str(exc))

    if not st.session_state.sf_gh_verified:
        st.info('Verify GitHub access before continuing.')
        return

    st.markdown('### 2. Repository')

    mode = st.radio(
        'Repository mode',
        ['Existing repository', 'Create new repository'],
        horizontal=True,
    )

    client = GitHubDelivery(
        st.session_state.sf_gh_token,
        PROJECT,
    )

    if mode == 'Existing repository':
        repos = st.session_state.sf_gh_repos

        if not repos:
            st.warning('No repositories available.')
            return

        options = {r['full_name']: r for r in repos}
        selected = st.selectbox(
            'Select repository',
            list(options.keys()),
        )

        repo = options[selected]

        st.session_state.sf_gh_target = {
            'owner': repo['owner']['login'],
            'repo': repo['name'],
        }

    else:
        name = st.text_input('New repository name')
        description = st.text_input(
            'Repository description',
            value='Soul Forge autonomous engineering',
        )
        private = st.checkbox('Private repository', value=True)

        if st.button('Create Repository'):
            try:
                repo = client.create_repository(
                    name,
                    description,
                    private,
                )

                st.session_state.sf_gh_target = {
                    'owner': repo['owner']['login'],
                    'repo': repo['name'],
                }

                st.success('Repository created.')
            except Exception as exc:
                st.error(str(exc))

    target = st.session_state.sf_gh_target

    if not target:
        return

    owner = target['owner']
    repo_name = target['repo']

    st.success(f'Target: {owner}/{repo_name}')

    st.markdown('### 3. Engineering Task')

    task = st.text_area(
        'What should the AI build?',
        height=150,
    )

    max_iterations = st.slider(
        'Maximum autonomous repair iterations',
        1,
        10,
        5,
    )

    run_tests = st.checkbox('Run pytest', value=True)
    browser_enabled = st.checkbox(
        'Run Playwright browser testing',
        value=True,
    )

    st.session_state.sf_delivery_model = st.text_input(
        'AI model',
        value=st.session_state.get(
            'sf_delivery_model',
            'openai/gpt-5-mini',
        ),
    )

    if st.button(
        'Start Autonomous Engineering',
        type='primary',
        disabled=not bool(task.strip()),
    ):
        try:
            remote = client.inspect_repository(
                owner,
                repo_name,
                'qa',
            )

            local = _files()
            prompt = _generation_prompt(
                task,
                remote,
                local,
            )

            with st.spinner('AI generating multi-file implementation...'):
                manifest = extract_json(_ai(prompt))

            _safe_write(manifest.get('files', {}))
            st.session_state.sf_manifest = manifest

            st.success('Multi-file implementation generated.')

            def repair(iteration, failures):
                st.warning(
                    f'Autonomous repair iteration {iteration}'
                )

                current = _files()
                repair_data = extract_json(
                    _ai(
                        _repair_prompt(
                            task,
                            failures,
                            current,
                        )
                    )
                )

                _safe_write(
                    repair_data.get('files', {})
                )

            engineering = client.autonomous_loop(
                repair,
                max_iterations,
                run_tests,
            )

            st.session_state.sf_engineering = engineering

            if not engineering.passed:
                st.error('Autonomous repair stopped with unresolved failures.')

                for failure in engineering.failures:
                    st.code(failure, language='text')

                return

            st.success('CODE ENGINEERING GATE PASSED.')

            if browser_enabled:
                st.info('Running Playwright browser validation...')
                browser = _browser_test()
                st.session_state.sf_browser = browser

                if not browser['passed']:
                    st.error('BROWSER GATE FAILED.')
                    st.code(browser['output'], language='text')
                    return

                st.success('BROWSER/UI GATE PASSED.')

            final = client.validate_all(run_tests)
            st.session_state.sf_validation = final

            if not final.passed:
                st.error('FINAL VALIDATION FAILED.')
                for failure in final.failures:
                    st.code(failure, language='text')
                return

            st.success('ALL CONFIGURED GATES PASSED.')

        except Exception as exc:
            st.error(f'Engineering pipeline failed: {exc}')

    st.markdown('### 4. Delivery')

    manifest = st.session_state.sf_manifest
    final = st.session_state.sf_validation
    browser = st.session_state.sf_browser

    ready = (
        manifest is not None
        and final is not None
        and final.passed
        and (
            not browser_enabled
            or (browser is not None and browser['passed'])
        )
    )

    if manifest:
        with st.expander('Generated files'):
            st.json({
                'summary': manifest.get('summary', ''),
                'files': list(manifest.get('files', {}).keys()),
                'dependencies': manifest.get('dependencies', []),
                'tests': manifest.get('tests', []),
                'browser_tests': manifest.get('browser_tests', []),
            })

    feature = st.text_input(
        'Feature name',
        value='autonomous-delivery',
    )

    commit = st.text_input(
        'Commit message',
        value='feat: autonomous Soul Forge delivery',
    )

    pr_title = st.text_input(
        'Pull request title',
        value='feat: autonomous Soul Forge delivery',
    )

    pr_body = st.text_area(
        'Pull request description',
        value=(
            '## Soul Forge Autonomous Delivery\n\n'
            '- Multi-file generation\n'
            '- AST and compile validation\n'
            '- Ruff\n'
            '- Pytest\n'
            '- Secret scan\n'
            '- Autonomous repair\n'
            '- Optional Playwright testing\n\n'
            'Target branch: qa\n\n'
            'Manual review required before main.'
        ),
    )

    if st.button(
        'Create Feature Branch + PR',
        type='primary',
        disabled=not ready,
    ):
        try:
            result = client.deliver(
                owner,
                repo_name,
                manifest.get('files', {}),
                feature,
                commit,
                pr_title,
                pr_body,
            )

            st.success('DELIVERY COMPLETED.')
            st.write('Feature branch:', result['branch'])

            st.link_button(
                'Open Pull Request',
                result['pr']['html_url'],
            )

            st.warning(
                'PR targets qa. No direct push to main was performed.'
            )

        except Exception as exc:
            st.error(f'GitHub delivery failed: {exc}')
