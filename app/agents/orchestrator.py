
"""
BANKAI RACE CONTROL — V0.6.2 Agent Orchestrator.

Coordinates:
Planner → Coder → Validator → Reviewer

The orchestrator is intentionally deterministic at this stage.
Future versions can attach Ruflo routing and autonomous repair.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import subprocess
import sys
import uuid


MISSION_STATES = (
    "created",
    "planning",
    "planned",
    "coding",
    "implemented",
    "validating",
    "repairing",
    "reviewing",
    "approved",
    "failed",
    "completed",
)


@dataclass
class Mission:
    mission_id: str
    objective: str
    phase: str = "created"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    plan: dict[str, Any] | None = None
    implementation: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    repair_attempts: int = 0

    def transition(self, new_phase: str, **metadata: Any) -> None:
        if new_phase not in MISSION_STATES:
            raise ValueError(f"Invalid mission state: {new_phase}")

        previous = self.phase
        self.phase = new_phase
        self.updated_at = datetime.now(timezone.utc).isoformat()

        event = {
            "timestamp": self.updated_at,
            "from": previous,
            "to": new_phase,
        }

        if metadata:
            event["metadata"] = metadata

        self.history.append(event)


class AgentOrchestrator:
    """
    V0.6.2 mission orchestrator.

    Keeps the V0.6.1 public methods while adding a complete mission lifecycle.
    """

    def __init__(
        self,
        project: str | Path | None = None,
        state_file: str | Path | None = None,
    ) -> None:
        self.project = (
            Path(project).resolve()
            if project is not None
            else Path.cwd().resolve()
        )

        self.state_file = (
            Path(state_file)
            if state_file is not None
            else self.project
            / "data"
            / "multi_agent_mission_state.json"
        )

        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.missions: dict[str, Mission] = {}

    # -------------------------------------------------------------------------
    # Mission creation
    # -------------------------------------------------------------------------

    def create_mission(self, objective: str) -> Mission:
        if not objective or not objective.strip():
            raise ValueError("Mission objective cannot be empty.")

        mission = Mission(
            mission_id=f"mission-{uuid.uuid4().hex[:12]}",
            objective=objective.strip(),
        )

        mission.history.append(
            {
                "timestamp": mission.created_at,
                "from": None,
                "to": "created",
            }
        )

        self.missions[mission.mission_id] = mission
        self.save_state()

        return mission

    # -------------------------------------------------------------------------
    # Planner
    # -------------------------------------------------------------------------

    def plan(self, mission: Mission) -> dict[str, Any]:
        mission.transition("planning")

        steps = [
            {
                "step": 1,
                "agent": "planner",
                "action": "analyze mission",
            },
            {
                "step": 2,
                "agent": "coder",
                "action": "implement changes",
            },
            {
                "step": 3,
                "agent": "validator",
                "action": "run validation",
            },
            {
                "step": 4,
                "agent": "reviewer",
                "action": "review implementation",
            },
            {
                "step": 5,
                "agent": "orchestrator",
                "action": "complete mission",
            },
        ]

        mission.plan = {
            "status": "planned",
            "objective": mission.objective,
            "steps": steps,
        }

        mission.transition(
            "planned",
            steps=len(steps),
        )

        self.save_state()

        return mission.plan

    # -------------------------------------------------------------------------
    # Coder
    # -------------------------------------------------------------------------

    def prepare_coding(
        self,
        mission: Mission,
        title: str,
        description: str,
    ) -> dict[str, Any]:
        mission.transition("coding")

        implementation = {
            "status": "ready",
            "agent": "coder",
            "title": title,
            "description": description,
            "files": [],
        }

        mission.implementation = implementation

        mission.transition("implemented")

        self.save_state()

        return implementation

    # -------------------------------------------------------------------------
    # Validator
    # -------------------------------------------------------------------------

    def validate(
        self,
        mission: Mission,
        command: list[str] | None = None,
    ) -> dict[str, Any]:
        mission.transition("validating")

        if command is None:
            command = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
            ]

        try:
            result = subprocess.run(
                command,
                cwd=self.project,
                capture_output=True,
                text=True,
                timeout=300,
            )

            validation = {
                "passed": result.returncode == 0,
                "returncode": result.returncode,
                "command": command,
                "stdout": result.stdout[-10000:],
                "stderr": result.stderr[-10000:],
            }

        except subprocess.TimeoutExpired as exc:
            validation = {
                "passed": False,
                "returncode": -1,
                "command": command,
                "stdout": (
                    exc.stdout[-10000:]
                    if isinstance(exc.stdout, str)
                    else ""
                ),
                "stderr": "Validation timed out.",
            }

        mission.validation = validation

        if validation["passed"]:
            mission.transition(
                "reviewing",
                validation="passed",
            )
        else:
            mission.transition(
                "failed",
                validation="failed",
            )

        self.save_state()

        return validation

    # -------------------------------------------------------------------------
    # Repair
    # -------------------------------------------------------------------------

    def repair(self, mission: Mission, reason: str) -> dict[str, Any]:
        mission.repair_attempts += 1

        mission.transition(
            "repairing",
            reason=reason,
            attempt=mission.repair_attempts,
        )

        repair = {
            "status": "ready",
            "agent": "coder",
            "attempt": mission.repair_attempts,
            "reason": reason,
        }

        mission.implementation = {
            **(mission.implementation or {}),
            "repair": repair,
        }

        self.save_state()

        return repair

    # -------------------------------------------------------------------------
    # Reviewer
    # -------------------------------------------------------------------------

    def review(
        self,
        mission: Mission,
        implementation: dict[str, Any] | None = None,
        validation_passed: bool = False,
    ) -> dict[str, Any]:

        if implementation is not None:
            mission.implementation = implementation

        if not validation_passed:
            result = {
                "approved": False,
                "status": "rejected",
                "reason": "Validation did not pass.",
            }

            mission.review = result
            mission.transition("failed", review="rejected")
            self.save_state()

            return result

        result = {
            "approved": True,
            "status": "approved",
            "reason": "Implementation passed validation.",
        }

        mission.review = result
        mission.transition("approved")

        self.save_state()

        return result

    # -------------------------------------------------------------------------
    # Completion
    # -------------------------------------------------------------------------

    def complete(self, mission: Mission) -> Mission:
        if mission.phase != "approved":
            raise RuntimeError(
                "Mission cannot be completed before approval."
            )

        mission.transition("completed")
        self.save_state()

        return mission

    # -------------------------------------------------------------------------
    # Full deterministic pipeline
    # -------------------------------------------------------------------------

    def execute_mission(
        self,
        objective: str,
        title: str = "Multi-agent implementation",
        description: str | None = None,
        max_repairs: int = 2,
        run_validation: bool = True,
    ) -> Mission:

        mission = self.create_mission(objective)

        self.plan(mission)

        self.prepare_coding(
            mission,
            title=title,
            description=description or objective,
        )

        if run_validation:
            validation = self.validate(mission)

            while (
                not validation["passed"]
                and mission.repair_attempts < max_repairs
            ):
                self.repair(
                    mission,
                    reason=validation["stderr"]
                    or validation["stdout"]
                    or "Validation failed.",
                )

                # Repair execution is deliberately separated from
                # automatic code mutation in V0.6.2.
                self.prepare_coding(
                    mission,
                    title=f"Repair attempt {mission.repair_attempts}",
                    description=(
                        "Repair implementation after validation failure."
                    ),
                )

                validation = self.validate(mission)

            if not validation["passed"]:
                return mission

        else:
            mission.transition(
                "reviewing",
                validation="skipped",
            )

        review = self.review(
            mission,
            implementation=mission.implementation,
            validation_passed=(
                True
                if not run_validation
                else bool(
                    mission.validation
                    and mission.validation.get("passed")
                )
            ),
        )

        if review["approved"]:
            self.complete(mission)

        return mission

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def save_state(self) -> None:
        payload = {
            "version": "0.6.2",
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "missions": {
                mission_id: asdict(mission)
                for mission_id, mission in self.missions.items()
            },
        }

        self.state_file.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def load_state(self) -> dict[str, Mission]:
        if not self.state_file.exists():
            return self.missions

        payload = json.loads(
            self.state_file.read_text(encoding="utf-8")
        )

        for mission_id, data in payload.get("missions", {}).items():
            self.missions[mission_id] = Mission(**data)

        return self.missions

    def get_mission(self, mission_id: str) -> Mission:
        if mission_id not in self.missions:
            self.load_state()

        if mission_id not in self.missions:
            raise KeyError(
                f"Mission not found: {mission_id}"
            )

        return self.missions[mission_id]


# =============================================================================
# BANKAI V0.6.3 — PLANNER → CODER INTEGRATION
# =============================================================================

def _bankai_plan_to_coder(self, mission):
    """
    Execute the V0.6.3 Planner → Coder handoff.

    The Planner generates the structured plan.
    The Coder receives that exact plan.
    """

    from app.agents.planner import PlannerAgent

    from app.agents.coding_agent import CodingAgent

    if mission.phase == "created":
        self.plan(mission)

    planner = PlannerAgent(
        project=str(self.project)
    )

    plan = planner.create_plan(
        mission.objective
    )

    mission.plan = plan.to_dict()

    coder = CodingAgent(
        self.project
    )

    implementation = coder.prepare_from_plan(
        plan
    )

    mission.transition(
        "coding",
        planner="completed",
        coder="received_plan",
    )

    mission.implementation = implementation

    mission.transition(
        "implemented",
        planner_to_coder=True,
    )

    self.save_state()

    return {
        "status": "handoff_complete",
        "plan": mission.plan,
        "implementation": mission.implementation,
    }


if not hasattr(AgentOrchestrator, "planner_to_coder"):
    AgentOrchestrator.planner_to_coder = _bankai_plan_to_coder
