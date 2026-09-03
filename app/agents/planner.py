
"""
BANKAI RACE CONTROL — Planner Agent
V0.6.1
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    """One step in an implementation plan."""

    step_id: int
    title: str
    description: str
    tools: list[str] = field(default_factory=list)
    status: str = "pending"


class PlannerAgent:
    """
    Converts a coding mission into an ordered implementation plan.

    V0.6.1 intentionally keeps planning deterministic.
    LLM/Ruflo-driven planning will be connected in later milestones.
    """

    name = "planner"
    role = "planning"

    def create_plan(self, mission: str) -> dict[str, Any]:
        """Create a safe initial implementation plan."""

        if not mission or not mission.strip():
            raise ValueError("Mission cannot be empty.")

        mission = mission.strip()

        steps = [
            PlanStep(
                step_id=1,
                title="Understand mission",
                description=f"Analyze the requested task: {mission}",
            ),
            PlanStep(
                step_id=2,
                title="Inspect project",
                description="Inspect relevant project files and existing architecture.",
                tools=["filesystem", "search"],
            ),
            PlanStep(
                step_id=3,
                title="Implement changes",
                description="Implement the smallest safe change required by the mission.",
                tools=["filesystem"],
            ),
            PlanStep(
                step_id=4,
                title="Validate implementation",
                description="Run appropriate tests and validation checks.",
                tools=["terminal"],
            ),
            PlanStep(
                step_id=5,
                title="Review result",
                description="Review the implementation for correctness and regressions.",
            ),
        ]

        return {
            "agent": self.name,
            "mission": mission,
            "steps": [
                {
                    "step_id": step.step_id,
                    "title": step.title,
                    "description": step.description,
                    "tools": step.tools,
                    "status": step.status,
                }
                for step in steps
            ],
            "status": "planned",
        }
