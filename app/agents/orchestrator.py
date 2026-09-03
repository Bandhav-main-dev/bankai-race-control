
"""
BANKAI RACE CONTROL — Agent Orchestrator
V0.6.1
"""

from dataclasses import dataclass, field
from typing import Any

from app.agents.planner import PlannerAgent
from app.agents.coding_agent import CodingAgent
from app.agents.reviewer import ReviewerAgent


@dataclass
class MissionState:
    """State of a multi-agent coding mission."""

    mission: str
    phase: str = "created"
    history: list[dict[str, Any]] = field(default_factory=list)


class AgentOrchestrator:
    """
    Coordinates BANKAI's coding agents.

    V0.6.1 flow:

        Mission
           ↓
        Planner
           ↓
        Coder
           ↓
        Reviewer

    Actual tool execution and autonomous repair are added later.
    """

    name = "agent_orchestrator"

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.coder = CodingAgent()
        self.reviewer = ReviewerAgent()

    def create_mission(self, mission: str) -> MissionState:
        """Create a new coding mission."""

        if not mission or not mission.strip():
            raise ValueError("Mission cannot be empty.")

        return MissionState(
            mission=mission.strip(),
            phase="created",
        )

    def plan(self, state: MissionState) -> dict[str, Any]:
        """Send mission to planner."""

        result = self.planner.create_plan(state.mission)

        state.phase = "planned"
        state.history.append(result)

        return result

    def prepare_coding(
        self,
        state: MissionState,
        title: str,
        description: str,
        files: list[str] | None = None,
    ) -> dict[str, Any]:
        """Prepare the coding phase."""

        task = self.coder.create_task(
            title=title,
            description=description,
            files=files,
        )

        result = self.coder.prepare_implementation(task)

        state.phase = "coding"
        state.history.append(result)

        return result

    def review(
        self,
        state: MissionState,
        implementation: dict[str, Any],
        validation_passed: bool = False,
    ) -> dict[str, Any]:
        """Send implementation to reviewer."""

        result = self.reviewer.review(
            implementation=implementation,
            validation_passed=validation_passed,
        )

        state.phase = "complete" if result.approved else "needs_revision"

        review_data = {
            "agent": self.reviewer.name,
            "approved": result.approved,
            "score": result.score,
            "findings": result.findings,
            "status": result.status,
        }

        state.history.append(review_data)

        return review_data

    def run_pipeline(self, mission: str) -> dict[str, Any]:
        """
        Execute the V0.6.1 planning pipeline.

        This does NOT modify project files.
        """

        state = self.create_mission(mission)

        plan = self.plan(state)

        return {
            "mission": state.mission,
            "phase": state.phase,
            "plan": plan,
            "history": state.history,
        }
