from pathlib import Path
import json

from app.core.local_ai import LocalAIEngine
from app.utils.logger import log


class AgentPlanner:

    def __init__(self, project_root: Path):

        self.project_root = Path(project_root)

        self.ai = LocalAIEngine()

    def build_context(self):

        files = []

        ignored = {
            ".git",
            "__pycache__",
            ".cache",
        }

        for path in self.project_root.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            try:

                relative = path.relative_to(
                    self.project_root
                )

                files.append(
                    str(relative)
                )

            except ValueError:
                continue

        return files

    def create_plan(
        self,
        objective: str
    ):

        log(
            f"AI planner received: {objective}"
        )

        files = self.build_context()

        context = "\n".join(
            files[:200]
        )

        prompt = f"""
Analyze this software engineering task.

PROJECT:
BANKAI RACE CONTROL

TASK:
{objective}

CURRENT PROJECT FILES:
{context}

Create an implementation plan.

Return:

OBJECTIVE:
...

ANALYSIS:
...

PLAN:
1.
2.
3.

FILES:
...

TESTS:
...

RISKS:
...
"""

        result = self.ai.ask(prompt)

        return {
            "objective": objective,
            "project_files": files,
            "ai_plan": result,
        }
