from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_QA_BRANCH = "qa"


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class GitHubDeliveryError(RuntimeError):
    pass


def run_command(
    command: list[str],
    cwd: Path,
    check: bool = True,
) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )

    output = CommandResult(
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )

    if check and output.returncode != 0:
        message = output.stderr or output.stdout or "Command failed."
        raise GitHubDeliveryError(
            f"Command failed: {' '.join(command)}\n{message}"
        )

    return output


def git(cwd: Path, *args: str, check: bool = True) -> CommandResult:
    return run_command(
        ["git", *args],
        cwd=cwd,
        check=check,
    )


def current_branch(repo: Path) -> str:
    result = git(repo, "branch", "--show-current")
    return result.stdout.strip()


def remote_url(repo: Path) -> str:
    result = git(repo, "remote", "get-url", "origin")
    return result.stdout.strip()


def is_safe_branch_name(branch: str) -> bool:
    if not branch:
        return False

    if branch in {"main", "master", "qa", "develop", "dev"}:
        return False

    if branch.startswith("main/"):
        return False

    if branch.startswith("qa/"):
        return False

    if ".." in branch:
        return False

    return bool(
        re.fullmatch(
            r"feature/soul-forge-[a-z0-9][a-z0-9._/-]*",
            branch,
        )
    )


def make_feature_branch_name(functionality: str) -> str:
    slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        functionality.strip().lower(),
    )

    slug = re.sub(r"-+", "-", slug).strip("-")

    if not slug:
        slug = "generated-functionality"

    return f"feature/soul-forge-{slug}"


def changed_files(repo: Path) -> list[str]:
    result = git(repo, "status", "--short")

    files: list[str] = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        # Git status format:
        # XY filename
        filename = line[3:].strip()

        # Handle quoted paths conservatively.
        if filename.startswith('"') and filename.endswith('"'):
            filename = filename[1:-1]

        if filename:
            files.append(filename)

    return files


def validate_python_file(path: Path) -> tuple[bool, str]:
    try:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
        return True, "Python syntax PASS"
    except Exception as exc:
        return False, f"Python syntax FAIL: {exc}"


def validate_selected_files(
    repo: Path,
    files: list[str],
) -> dict[str, Any]:
    results: list[dict[str, str | bool]] = []
    passed = True

    for relative in files:
        path = repo / relative

        if not path.exists():
            results.append(
                {
                    "file": relative,
                    "passed": False,
                    "message": "File does not exist.",
                }
            )
            passed = False
            continue

        if path.suffix == ".py":
            ok, message = validate_python_file(path)

            results.append(
                {
                    "file": relative,
                    "passed": ok,
                    "message": message,
                }
            )

            if not ok:
                passed = False
        else:
            results.append(
                {
                    "file": relative,
                    "passed": True,
                    "message": "File exists.",
                }
            )

    return {
        "passed": passed,
        "files": results,
    }


def create_feature_branch(
    repo: Path,
    branch: str,
) -> None:
    if not is_safe_branch_name(branch):
        raise GitHubDeliveryError(
            f"Unsafe feature branch name: {branch}"
        )

    git(repo, "fetch", "origin")

    existing = git(
        repo,
        "branch",
        "--list",
        branch,
        check=False,
    )

    if existing.stdout.strip():
        git(repo, "switch", branch)
        return

    git(repo, "switch", "-c", branch)


def stage_files(
    repo: Path,
    files: list[str],
) -> None:
    if not files:
        raise GitHubDeliveryError(
            "No files selected for delivery."
        )

    # Never stage .git internals.
    safe_files = [
        f for f in files
        if not f.startswith(".git/")
    ]

    if not safe_files:
        raise GitHubDeliveryError(
            "No safe files selected."
        )

    git(repo, "add", "--", *safe_files)


def staged_files(repo: Path) -> list[str]:
    result = git(
        repo,
        "diff",
        "--cached",
        "--name-only",
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def commit(
    repo: Path,
    message: str,
) -> str:
    if not message.strip():
        raise GitHubDeliveryError(
            "Commit message cannot be empty."
        )

    # Conventional-commit style.
    if not re.match(
        r"^(feat|fix|refactor|test|docs|chore|perf|build|ci)\(",
        message.strip(),
    ):
        raise GitHubDeliveryError(
            "Use a conventional commit message, e.g. "
            "'feat(soul-forge): add generated feature'"
        )

    git(repo, "commit", "-m", message.strip())

    return git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()


def push_feature_branch(
    repo: Path,
    branch: str,
) -> None:
    if not is_safe_branch_name(branch):
        raise GitHubDeliveryError(
            "Only SOUL FORGE feature branches may be pushed."
        )

    if branch in {"main", "master", "qa"}:
        raise GitHubDeliveryError(
            "Direct protected-branch push blocked."
        )

    git(
        repo,
        "push",
        "-u",
        "origin",
        branch,
    )


def github_api(
    token: str,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    if not token:
        raise GitHubDeliveryError(
            "GitHub token is required for GitHub API operations."
        )

    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        method=method.upper(),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "SOUL-FORGE",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")

            if not raw:
                return {}

            return json.loads(raw)

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")

        raise GitHubDeliveryError(
            f"GitHub API {exc.code}: {detail}"
        ) from exc


def github_user(
    token: str,
) -> dict[str, Any]:
    return github_api(
        token,
        "GET",
        "https://api.github.com/user",
    )


def list_repositories(
    token: str,
) -> list[dict[str, Any]]:
    page = 1
    output: list[dict[str, Any]] = []

    while True:
        data = github_api(
            token,
            "GET",
            (
                "https://api.github.com/user/repos"
                f"?per_page=100&page={page}&sort=updated"
            ),
        )

        if not isinstance(data, list):
            break

        if not data:
            break

        output.extend(data)

        if len(data) < 100:
            break

        page += 1

    return output


def create_repository(
    token: str,
    name: str,
    description: str = "",
    private: bool = True,
) -> dict[str, Any]:
    if not re.fullmatch(
        r"[A-Za-z0-9._-]+",
        name.strip(),
    ):
        raise GitHubDeliveryError(
            "Repository name contains invalid characters."
        )

    return github_api(
        token,
        "POST",
        "https://api.github.com/user/repos",
        {
            "name": name.strip(),
            "description": description.strip(),
            "private": bool(private),
            "auto_init": True,
        },
    )


def parse_owner_repo(
    remote: str,
) -> tuple[str, str]:
    remote = remote.strip()

    patterns = [
        r"git@github\.com:([^/]+)/(.+?)(?:\.git)?$",
        r"https?://github\.com/([^/]+)/(.+?)(?:\.git)?$",
    ]

    for pattern in patterns:
        match = re.match(pattern, remote)

        if match:
            return match.group(1), match.group(2)

    raise GitHubDeliveryError(
        f"Could not parse GitHub repository from remote: {remote}"
    )


def create_pull_request(
    token: str,
    owner: str,
    repo: str,
    head: str,
    base: str = DEFAULT_QA_BRANCH,
    title: str = "",
    body: str = "",
) -> dict[str, Any]:
    if base in {"main", "master"}:
        raise GitHubDeliveryError(
            "SOUL FORGE PR target cannot be main/master."
        )

    if not is_safe_branch_name(head):
        raise GitHubDeliveryError(
            f"Unsafe PR source branch: {head}"
        )

    if base != "qa":
        raise GitHubDeliveryError(
            "SOUL FORGE delivery currently requires target branch 'qa'."
        )

    return github_api(
        token,
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        {
            "title": title.strip(),
            "head": head,
            "base": base,
            "body": body,
        },
    )


def delivery_manifest(
    functionality: str,
    branch: str,
    files: list[str],
    commit_message: str,
    validation: dict[str, Any],
    pr_url: str | None = None,
) -> dict[str, Any]:
    return {
        "system": "SOUL FORGE",
        "delivery_type": "generated_code",
        "functionality": functionality,
        "branch": branch,
        "target_branch": "qa",
        "files": files,
        "commit_message": commit_message,
        "validation": validation,
        "pull_request": pr_url,
        "main_merge": "MANUAL_ONLY",
    }
