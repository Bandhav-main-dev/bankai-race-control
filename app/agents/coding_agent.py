import sys
import subprocess

"""
BANKAI RACE CONTROL — Coding Agent
V0.6.1

Compatibility-preserving multi-agent coding interface.

This version preserves the V0.3/V0.5 constructor contract:

    CodingAgent(PROJECT)

while adding the V0.6 multi-agent task interface.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CodingTask:
    """Task assigned to the coding agent."""

    title: str
    description: str
    files: list[str] = field(default_factory=list)


class CodingAgent:
    """
    BANKAI coding agent.

    The project argument is intentionally optional so both interfaces work:

        CodingAgent(PROJECT)   # existing V0.3/V0.5 interface
        CodingAgent()          # V0.6 agent interface

    Existing coding-tool functionality is preserved through the project's
    existing tool modules.
    """

    name = "coder"
    role = "implementation"

    def __init__(self, project: str | Path | None = None) -> None:
        if project is None:
            project = Path.cwd()

        self.project = Path(project).resolve()

    # -------------------------------------------------------------------------
    # V0.6 TASK INTERFACE
    # -------------------------------------------------------------------------

    def create_task(
        self,
        title: str,
        description: str,
        files: list[str] | None = None,
    ) -> CodingTask:
        """Create a coding task."""

        if not title or not title.strip():
            raise ValueError("Coding task title cannot be empty.")

        if not description or not description.strip():
            raise ValueError("Coding task description cannot be empty.")

        return CodingTask(
            title=title.strip(),
            description=description.strip(),
            files=files or [],
        )

    def prepare_implementation(
        self,
        task: CodingTask,
    ) -> dict[str, Any]:
        """Prepare an implementation request."""

        return {
            "agent": self.name,
            "role": self.role,
            "project": str(self.project),
            "task": {
                "title": task.title,
                "description": task.description,
                "files": task.files,
            },
            "status": "ready",
        }

    # -------------------------------------------------------------------------
    # EXISTING PROJECT INSPECTION COMPATIBILITY
    # -------------------------------------------------------------------------

    def inspect_project(self) -> dict[str, Any]:
        """
        Inspect the BANKAI project.

        This preserves the expected V0.3/V0.5 coding-agent behavior.
        """

        if not self.project.exists():
            raise FileNotFoundError(
                f"Project does not exist: {self.project}"
            )

        files = []
        directories = []

        for path in self.project.rglob("*"):
            if ".git" in path.parts:
                continue

            if path.is_file():
                files.append(str(path.relative_to(self.project)))

            elif path.is_dir():
                directories.append(str(path.relative_to(self.project)))

        return {
            "project": str(self.project),
            "exists": True,
            "files": sorted(files),
            "directories": sorted(directories),
        }

    def read(self, relative_path: str) -> str:
        """
        Read a project file safely.

        Delegates to the existing filesystem tool when available.
        Falls back to direct safe project-relative reading.
        """

        target = (self.project / relative_path).resolve()

        try:
            target.relative_to(self.project)
        except ValueError as exc:
            raise ValueError(
                f"Path escapes project sandbox: {relative_path}"
            ) from exc

        if not target.exists():
            raise FileNotFoundError(str(target))

        if not target.is_file():
            raise IsADirectoryError(str(target))

        return target.read_text(encoding="utf-8")

    def search_code(
        self,
        query: str,
        pattern: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search project source files.

        Compatible with the existing test interface while remaining
        dependency-light.
        """

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        query = query.strip()
        results = []

        extensions = {
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".md",
            ".txt",
        }

        for path in self.project.rglob("*"):
            if ".git" in path.parts:
                continue

            if not path.is_file():
                continue

            if path.suffix.lower() not in extensions:
                continue

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue

            if query.lower() not in text.lower():
                continue

            results.append(
                {
                    "file": str(path.relative_to(self.project)),
                    "matches": text.lower().count(query.lower()),
                }
            )

        return results

    def python(self, code: str):
        """
        V0.5 compatibility wrapper.

        Preserves the original CodingAgent.python() API while
        using the newer execute_python() implementation.
        """
        return self.execute_python(code)

    def execute_python(self, code: str) -> dict[str, Any]:
        """
        Execute Python through the existing terminal tool when possible.

        This method is intentionally conservative and executes from the
        project directory.
        """

        if not code or not code.strip():
            raise ValueError("Python code cannot be empty.")

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
            ],
            cwd=self.project,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }


__all__ = [
    "CodingAgent",
    "CodingTask",
]


# =============================================================================
# BANKAI V0.6.3 — PLANNER → CODER COMPATIBILITY EXTENSION
# =============================================================================

def _bankai_prepare_from_plan(self, implementation_plan):
    """
    Convert a Planner ImplementationPlan/dict into a CodingTask-compatible
    preparation payload.

    This does not mutate project files. Actual mutation remains a separate
    operation for later autonomous-coding milestones.
    """

    if hasattr(implementation_plan, "to_dict"):
        plan = implementation_plan.to_dict()
    elif isinstance(implementation_plan, dict):
        plan = dict(implementation_plan)
    else:
        raise TypeError(
            "implementation_plan must be a dict or provide to_dict()."
        )

    objective = plan.get("objective", "").strip()

    if not objective:
        raise ValueError(
            "Implementation plan must contain an objective."
        )

    steps = plan.get("implementation_steps", [])

    return {
        "status": "ready",
        "agent": "coder",
        "objective": objective,
        "analysis": plan.get("analysis", ""),
        "files_to_modify": list(
            plan.get("files_to_modify", [])
        ),
        "files_to_create": list(
            plan.get("files_to_create", [])
        ),
        "implementation_steps": list(steps),
        "validation_steps": list(
            plan.get("validation_steps", [])
        ),
        "risks": list(
            plan.get("risks", [])
        ),
        "constraints": list(
            plan.get("constraints", [])
        ),
    }


if not hasattr(CodingAgent, "prepare_from_plan"):
    CodingAgent.prepare_from_plan = _bankai_prepare_from_plan
