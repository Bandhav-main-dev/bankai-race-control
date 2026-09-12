from __future__ import annotations

import ast
import base64
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


GITHUB_API = "https://api.github.com"

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "repair_backups",
}

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"OPENROUTER_API_KEY\s*=\s*['\"][^'\"]+"),
    re.compile(r"OPENAI_API_KEY\s*=\s*['\"][^'\"]+"),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*['\"][^'\"]+"),
]


@dataclass
class ValidationResult:
    passed: bool
    stage: str
    output: str = ''
    errors: list[str] = field(default_factory=list)


@dataclass
class EngineeringResult:
    passed: bool
    iterations: int
    failures: list[str]
    history: list[dict[str, Any]] = field(default_factory=list)


class GitHubDeliveryError(RuntimeError):
    pass


class GitHubDelivery:

    def __init__(self, token: str, project_root: str | Path):
        if not token or len(token.strip()) < 20:
            raise GitHubDeliveryError(
                'GitHub fine-grained PAT is missing or invalid.'
            )

        self.token = token.strip()
        self.project_root = Path(project_root).resolve()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Soul-Forge-GitHub-Delivery",
        })

    def request(self, method, path, **kwargs):
        url = path if path.startswith('http') else GITHUB_API + path
        response = self.session.request(
            method,
            url,
            timeout=30,
            **kwargs,
        )

        if not response.ok:
            try:
                payload = response.json()
                message = payload.get('message', response.text)
            except Exception:
                message = response.text

            raise GitHubDeliveryError(
                f'GitHub API {response.status_code}: {message}'
            )

        if not response.content:
            return {}

        return response.json()

    def verify_access(self):
        return self.request('GET', '/user')

    def list_repositories(self, limit=100):
        data = self.request(
            'GET',
            '/user/repos',
            params={
                'visibility': 'all',
                'affiliation': 'owner,collaborator,organization_member',
                'per_page': min(limit, 100),
                'sort': 'updated',
            },
        )
        return data[:limit]

    def create_repository(self, name, description='', private=True):
        if not name:
            raise GitHubDeliveryError('Repository name is required.')

        return self.request(
            'POST',
            '/user/repos',
            json={
                'name': name,
                'description': description,
                'private': private,
                'auto_init': True,
            },
        )

    def get_branch(self, owner, repo, branch):
        return self.request(
            'GET',
            f'/repos/{owner}/{repo}/branches/{branch}',
        )

    def branch_sha(self, owner, repo, branch):
        return self.get_branch(owner, repo, branch)['commit']['sha']

    def inspect_repository(self, owner, repo, branch='qa'):
        branch_data = self.get_branch(owner, repo, branch)
        tree_sha = branch_data['commit']['commit']['tree']['sha']

        tree = self.request(
            'GET',
            f'/repos/{owner}/{repo}/git/trees/{tree_sha}',
            params={'recursive': '1'},
        )

        files = []
        for item in tree.get('tree', []):
            if item.get('type') != 'blob':
                continue

            path = item.get('path', '')
            if any(part in IGNORED_DIRS for part in Path(path).parts):
                continue

            files.append(path)

        return {
            'branch': branch,
            'commit': branch_data['commit']['sha'],
            'tree': tree_sha,
            'files': files,
        }

    def get_file(self, owner, repo, path, branch='qa'):
        data = self.request(
            'GET',
            f'/repos/{owner}/{repo}/contents/{path}',
            params={'ref': branch},
        )

        if data.get('encoding') != 'base64':
            return ''

        return base64.b64decode(data['content']).decode(
            'utf-8',
            errors='replace',
        )

    def local_files(self):
        result = {}

        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue

            relative = path.relative_to(self.project_root)

            if any(part in IGNORED_DIRS for part in relative.parts):
                continue

            if path.stat().st_size > 750000:
                continue

            try:
                result[relative.as_posix()] = path.read_text(
                    encoding='utf-8',
                    errors='replace',
                )
            except Exception:
                pass

        return result

    def validate_python(self):
        errors = []
        count = 0

        for path in self.project_root.rglob('*.py'):
            relative = path.relative_to(self.project_root)

            if any(part in IGNORED_DIRS for part in relative.parts):
                continue

            count += 1

            try:
                source = path.read_text(
                    encoding='utf-8',
                    errors='replace',
                )

                ast.parse(source, filename=str(path))
                compile(source, str(path), 'exec')

            except Exception as exc:
                errors.append(f'{relative}: {exc}')

        return ValidationResult(
            passed=not errors,
            stage='AST + COMPILE',
            output=f'Checked {count} Python files.',
            errors=errors,
        )

    def compile_all(self):
        result = subprocess.run(
            [sys.executable, '-m', 'compileall', '-q', '.'],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=180,
        )

        output = (result.stdout + '\n' + result.stderr).strip()

        return ValidationResult(
            passed=result.returncode == 0,
            stage='COMPILEALL',
            output=output or 'compileall passed.',
        )

    def ruff(self):
        if shutil.which('ruff') is None:
            return ValidationResult(
                passed=True,
                stage='RUFF',
                output='Ruff unavailable; skipped.',
            )

        result = subprocess.run(
            ['ruff', 'check', '.'],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=300,
        )

        output = (result.stdout + '\n' + result.stderr).strip()

        return ValidationResult(
            passed=result.returncode == 0,
            stage='RUFF',
            output=output,
        )

    def pytest(self):
        tests = self.project_root / 'tests'

        if not tests.exists():
            return ValidationResult(
                passed=True,
                stage='PYTEST',
                output='No tests directory; skipped.',
            )

        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '-q'],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=600,
        )

        output = (result.stdout + '\n' + result.stderr).strip()

        return ValidationResult(
            passed=result.returncode == 0,
            stage='PYTEST',
            output=output,
        )

    def secret_scan(self):
        errors = []

        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue

            relative = path.relative_to(self.project_root)

            if any(part in IGNORED_DIRS for part in relative.parts):
                continue

            if path.name == '.env':
                errors.append(f'.env detected: {relative}')
                continue

            if path.stat().st_size > 2000000:
                continue

            try:
                content = path.read_text(
                    encoding='utf-8',
                    errors='ignore',
                )
            except Exception:
                continue

            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    errors.append(f'Possible secret: {relative}')
                    break

        return ValidationResult(
            passed=not errors,
            stage='SECRET SCAN',
            output='No obvious secrets found.' if not errors else '\n'.join(errors),
            errors=errors,
        )

    def validate_all(self, run_tests=True):
        results = [
            self.validate_python(),
            self.compile_all(),
            self.ruff(),
        ]

        if run_tests:
            results.append(self.pytest())

        results.append(self.secret_scan())

        failures = []
        for result in results:
            if not result.passed:
                failures.append(
                    f'{result.stage}: {result.output} {result.errors}'
                )

        return EngineeringResult(
            passed=not failures,
            iterations=1,
            failures=failures,
            history=[
                {
                    'stage': r.stage,
                    'passed': r.passed,
                    'output': r.output,
                    'errors': r.errors,
                }
                for r in results
            ],
        )

    def autonomous_loop(
        self,
        repair_callback,
        max_iterations=5,
        run_tests=True,
    ):
        history = []
        last_failures = []

        for iteration in range(1, max_iterations + 1):
            result = self.validate_all(run_tests=run_tests)

            history.append({
                'iteration': iteration,
                'passed': result.passed,
                'results': result.history,
            })

            if result.passed:
                return EngineeringResult(
                    passed=True,
                    iterations=iteration,
                    failures=[],
                    history=history,
                )

            last_failures = result.failures

            if iteration >= max_iterations:
                break

            repair_callback(iteration, last_failures)

        return EngineeringResult(
            passed=False,
            iterations=max_iterations,
            failures=last_failures,
            history=history,
        )

    def create_branch(self, owner, repo, new_branch, source_branch='qa'):
        if new_branch in {'main', 'master', 'qa'}:
            raise GitHubDeliveryError(
                'Protected branch cannot be delivery branch.'
            )

        sha = self.branch_sha(owner, repo, source_branch)

        return self.request(
            'POST',
            f'/repos/{owner}/{repo}/git/refs',
            json={
                'ref': f'refs/heads/{new_branch}',
                'sha': sha,
            },
        )

    def create_blob(self, owner, repo, content):
        return self.request(
            'POST',
            f'/repos/{owner}/{repo}/git/blobs',
            json={
                'content': content,
                'encoding': 'utf-8',
            },
        )['sha']

    def atomic_commit(self, owner, repo, branch, files, message):
        branch_data = self.get_branch(owner, repo, branch)
        parent = branch_data['commit']['sha']
        base_tree = branch_data['commit']['commit']['tree']['sha']
        entries = []

        for path, content in files.items():
            normalized = str(path).replace('\\', '/').lstrip('/')

            if not normalized:
                continue

            blob = self.create_blob(owner, repo, content)

            entries.append({
                'path': normalized,
                'mode': '100644',
                'type': 'blob',
                'sha': blob,
            })

        tree = self.request(
            'POST',
            f'/repos/{owner}/{repo}/git/trees',
            json={
                'base_tree': base_tree,
                'tree': entries,
            },
        )

        commit = self.request(
            'POST',
            f'/repos/{owner}/{repo}/git/commits',
            json={
                'message': message,
                'tree': tree['sha'],
                'parents': [parent],
            },
        )

        self.request(
            'PATCH',
            f'/repos/{owner}/{repo}/git/refs/heads/{branch}',
            json={
                'sha': commit['sha'],
                'force': False,
            },
        )

        return commit

    def create_pr(self, owner, repo, head, title, body, base='qa'):
        if base == 'main':
            raise GitHubDeliveryError(
                'PR to main is prohibited.'
            )

        return self.request(
            'POST',
            f'/repos/{owner}/{repo}/pulls',
            json={
                'title': title,
                'body': body,
                'head': head,
                'base': base,
            },
        )

    def deliver(
        self,
        owner,
        repo,
        files,
        feature_name,
        commit_message,
        pr_title,
        pr_body,
    ):
        safe = re.sub(
            r'[^a-zA-Z0-9-]+',
            '-',
            feature_name.lower(),
        ).strip('-')

        branch = f'feature/soul-forge-{safe}-{int(time.time())}'

        self.create_branch(
            owner,
            repo,
            branch,
            'qa',
        )

        commit = self.atomic_commit(
            owner,
            repo,
            branch,
            files,
            commit_message,
        )

        pr = self.create_pr(
            owner,
            repo,
            branch,
            pr_title,
            pr_body,
            'qa',
        )

        return {
            'branch': branch,
            'commit': commit,
            'pr': pr,
        }


def extract_json(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = text.replace('```json', '', 1)
        text = text.replace('```', '')
        text = text.strip()

    start = text.find('{')
    end = text.rfind('}')

    if start == -1 or end == -1:
        raise ValueError('AI response did not contain JSON.')

    return json.loads(text[start:end + 1])
