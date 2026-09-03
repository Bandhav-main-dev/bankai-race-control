from pathlib import Path
import subprocess

from app.tools.security import SecurityPolicy
from app.utils.logger import log


class TerminalTools:

    def __init__(
        self,
        project_root: Path
    ):

        self.project_root = Path(
            project_root
        ).resolve()

        self.security = SecurityPolicy(
            self.project_root
        )

    def run(
        self,
        command: str,
        timeout: int = 120
    ):

        self.security.validate_command(
            command
        )

        log(
            f"EXEC {command}"
        )

        result = subprocess.run(
            command,
            shell=True,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def python(
        self,
        code: str,
        timeout: int = 120
    ):

        log(
            "EXEC Python code"
        )

        result = subprocess.run(
            [
                "python",
                "-c",
                code
            ],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

    def pytest(
        self,
        timeout: int = 120
    ):

        return self.run(
            "python -m pytest -q",
            timeout
        )

    def ruff(
        self,
        timeout: int = 120
    ):

        return self.run(
            "ruff check .",
            timeout
        )

    def git_status(
        self
    ):

        return self.run(
            "git status --short",
            timeout=30
        )
