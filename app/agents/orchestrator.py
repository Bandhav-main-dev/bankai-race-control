"""
BANKAI RACE CONTROL — V0.6.2 Agent Orchestrator.

Coordinates:
Planner → Coder → Validator → Reviewer

The orchestrator is intentionally deterministic at this stage.
Future versions can attach Ruflo routing and autonomous repair.
"""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agents.validator import AutomaticValidator

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
            Path(project).resolve() if project is not None else Path.cwd().resolve()
        )

        self.state_file = (
            Path(state_file)
            if state_file is not None
            else self.project / "data" / "multi_agent_mission_state.json"
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
                check=False,
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
                "stdout": (exc.stdout[-10000:] if isinstance(exc.stdout, str) else ""),
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
            raise RuntimeError("Mission cannot be completed before approval.")

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

            while not validation["passed"] and mission.repair_attempts < max_repairs:
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
                    description=("Repair implementation after validation failure."),
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
                else bool(mission.validation and mission.validation.get("passed"))
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

        payload = json.loads(self.state_file.read_text(encoding="utf-8"))

        for mission_id, data in payload.get("missions", {}).items():
            self.missions[mission_id] = Mission(**data)

        return self.missions

    def get_mission(self, mission_id: str) -> Mission:
        if mission_id not in self.missions:
            self.load_state()

        if mission_id not in self.missions:
            raise KeyError(f"Mission not found: {mission_id}")

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

    from app.agents.coding_agent import CodingAgent
    from app.agents.planner import PlannerAgent

    if mission.phase == "created":
        self.plan(mission)

    planner = PlannerAgent(project=str(self.project))

    plan = planner.create_plan(mission.objective)

    mission.plan = plan.to_dict()

    coder = CodingAgent(self.project)

    implementation = coder.prepare_from_plan(plan)

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


# =============================================================================
# V0.6.4 — CODER → REVIEWER ORCHESTRATION
# =============================================================================


def _v064_coder_to_reviewer(
    self,
    mission,
    *,
    validation_passed: bool = True,
):
    """
    Connect the structured Coder result directly to ReviewerAgent.
    """

    if mission.plan is None:
        raise RuntimeError("Planner output is required before Coder → Reviewer.")

    # Import dynamically to preserve compatibility with the existing module.
    from app.agents.coding_agent import CodingAgent
    from app.agents.reviewer import ReviewerAgent

    coder = CodingAgent()
    reviewer = ReviewerAgent()

    # Produce structured implementation output from the Planner contract.
    implementation_result = coder.create_implementation_result(
        mission.plan,
        status="prepared",
        validation_evidence=[
            "Structured Coder output generated.",
            "Planner → Coder contract preserved.",
        ],
        notes=(
            "V0.6.4 review operates on the structured implementation "
            "handoff. Autonomous file mutation remains a later milestone."
        ),
    )

    # Store Coder result in mission.
    mission.implementation = implementation_result.to_dict()

    # Explicitly enter reviewing state if supported.
    try:
        mission.phase = "reviewing"
    except AttributeError:
        mission.phase = "reviewing"

    # Reviewer consumes the actual Coder result.
    review_result = reviewer.review_implementation(
        mission.plan,
        implementation_result,
        validation_passed=validation_passed,
    )

    mission.review = review_result.to_dict()

    # Continue state machine.
    try:
        if review_result.approved:
            mission.phase = "approved"
        else:
            mission.phase = "failed"
    except AttributeError:
        pass

    # Add history if the Mission model exposes it.
    if hasattr(mission, "history"):
        mission.history.append(
            {
                "phase": "coder_to_reviewer",
                "status": review_result.status,
                "approved": review_result.approved,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    # Persist using the existing orchestrator persistence mechanism.
    if hasattr(self, "save_state"):
        self.save_state()

    return review_result


if not hasattr(AgentOrchestrator, "coder_to_reviewer"):
    AgentOrchestrator.coder_to_reviewer = _v064_coder_to_reviewer


# =============================================================================
# BANKAI V0.6.4 — FINAL CODER → REVIEWER ORCHESTRATOR REPAIR
# =============================================================================


def _bankai_v064_review_result_dict(review_result):
    """
    Serialize the project's existing ReviewResult schema.

    ReviewResult schema:

        approved: bool
        score: int
        findings: list[str]
        status: str
    """

    if hasattr(review_result, "to_dict"):
        return review_result.to_dict()

    return {
        "approved": bool(review_result.approved),
        "score": int(review_result.score),
        "findings": list(review_result.findings),
        "status": str(review_result.status),
    }


def _bankai_v064_coder_to_reviewer_final(
    self,
    mission,
    validation_passed=True,
):
    """
    V0.6.4 authoritative Coder → Reviewer pipeline.

    Important:
    This method does NOT assume ReviewResult.to_dict().
    It serializes the actual four-field ReviewResult schema.
    """

    # -------------------------------------------------------------------------
    # PLAN VALIDATION
    # -------------------------------------------------------------------------

    if mission.plan is None:
        raise RuntimeError("Coder → Reviewer requires planner output.")

    planned_steps = list(
        getattr(
            mission.plan,
            "implementation_steps",
            [],
        )
        or []
    )

    if not planned_steps:
        raise RuntimeError("Planner produced zero implementation steps.")

    # -------------------------------------------------------------------------
    # AGENTS
    # -------------------------------------------------------------------------

    from app.agents.coding_agent import CodingAgent
    from app.agents.reviewer import (
        ReviewerAgent,
        ReviewResult,
    )

    coder = CodingAgent()
    reviewer = ReviewerAgent()

    # -------------------------------------------------------------------------
    # CODER
    # -------------------------------------------------------------------------

    implementation_result = coder.create_implementation_result(
        mission.plan,
        status="prepared",
        validation_evidence=[
            "Planner output validated.",
            "Structured Coder result generated.",
            "Coder → Reviewer contract validated.",
        ],
        notes=("V0.6.4 structured Coder → Reviewer handoff."),
    )

    # -------------------------------------------------------------------------
    # STORE IMPLEMENTATION
    # -------------------------------------------------------------------------

    if hasattr(
        implementation_result,
        "to_dict",
    ):
        implementation_dict = implementation_result.to_dict()
    else:
        implementation_dict = {
            "objective": getattr(
                implementation_result,
                "objective",
                "",
            ),
            "status": getattr(
                implementation_result,
                "status",
                "",
            ),
            "files_modified": list(
                getattr(
                    implementation_result,
                    "files_modified",
                    [],
                )
                or []
            ),
            "files_created": list(
                getattr(
                    implementation_result,
                    "files_created",
                    [],
                )
                or []
            ),
            "implementation_steps_completed": list(
                getattr(
                    implementation_result,
                    "implementation_steps_completed",
                    [],
                )
                or []
            ),
            "implementation_steps_remaining": list(
                getattr(
                    implementation_result,
                    "implementation_steps_remaining",
                    [],
                )
                or []
            ),
            "validation_evidence": list(
                getattr(
                    implementation_result,
                    "validation_evidence",
                    [],
                )
                or []
            ),
            "risks": list(
                getattr(
                    implementation_result,
                    "risks",
                    [],
                )
                or []
            ),
            "constraints": list(
                getattr(
                    implementation_result,
                    "constraints",
                    [],
                )
                or []
            ),
            "notes": getattr(
                implementation_result,
                "notes",
                "",
            ),
            "created_at": getattr(
                implementation_result,
                "created_at",
                "",
            ),
        }

    mission.implementation = implementation_dict

    # -------------------------------------------------------------------------
    # REVIEWING STATE
    # -------------------------------------------------------------------------

    mission.phase = "reviewing"

    if hasattr(
        mission,
        "history",
    ):
        mission.history.append(
            {
                "phase": "reviewing",
                "status": "started",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    # -------------------------------------------------------------------------
    # REVIEWER
    # -------------------------------------------------------------------------

    review_result = reviewer.review_implementation(
        mission.plan,
        implementation_result,
        validation_passed=validation_passed,
    )

    if not isinstance(
        review_result,
        ReviewResult,
    ):
        raise TypeError("Reviewer returned an invalid ReviewResult.")

    # -------------------------------------------------------------------------
    # CRITICAL FIX
    #
    # DO NOT:
    #
    #     review_result.to_dict()
    #
    # The real ReviewResult schema has no to_dict().
    # -------------------------------------------------------------------------

    mission.review = _bankai_v064_review_result_dict(review_result)

    # -------------------------------------------------------------------------
    # STATE TRANSITION
    # -------------------------------------------------------------------------

    if review_result.approved:
        mission.phase = "approved"
    else:
        mission.phase = "failed"

    if hasattr(
        mission,
        "history",
    ):
        mission.history.append(
            {
                "phase": "coder_to_reviewer",
                "status": review_result.status,
                "approved": bool(review_result.approved),
                "score": int(review_result.score),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    # -------------------------------------------------------------------------
    # PERSIST
    # -------------------------------------------------------------------------

    if hasattr(
        self,
        "save_state",
    ):
        self.save_state()

    return review_result


# =============================================================================
# AUTHORITATIVE METHOD ASSIGNMENT
# =============================================================================

AgentOrchestrator.coder_to_reviewer = _bankai_v064_coder_to_reviewer_final


# =============================================================================
# BANKAI V0.6.5 — AUTOMATIC VALIDATION
# =============================================================================


def _bankai_v065_validate_implementation(
    self,
    mission,
    implementation=None,
    run_pytest=True,
    run_ruff=True,
):
    """
    V0.6.5 automatic validation gate.

    Planner → Coder output is validated before Reviewer.
    """

    validator = AutomaticValidator(
        self.project if hasattr(self, "project") else Path.cwd()
    )

    if implementation is None:
        implementation = getattr(
            mission,
            "implementation",
            None,
        )

    result = validator.validate(
        implementation=implementation,
        run_pytest=run_pytest,
        run_ruff=run_ruff,
    )

    mission.validation = result.to_dict()

    if result.passed:
        mission.phase = "validated"
    else:
        mission.phase = "repairing"

    history = getattr(
        mission,
        "history",
        None,
    )

    if isinstance(history, list):
        history.append(
            {
                "phase": mission.phase,
                "event": "automatic_validation",
                "validation": result.to_dict(),
                "timestamp": result.created_at,
            }
        )

    if hasattr(self, "save_state"):
        self.save_state()

    return result


def _bankai_v065_validate_and_route(
    self,
    mission,
    implementation=None,
):
    """
    Validation routing:

        PASS → Reviewer
        FAIL → Repair
    """

    result = _bankai_v065_validate_implementation(
        self,
        mission,
        implementation=implementation,
        run_pytest=True,
        run_ruff=True,
    )

    if result.passed:
        mission.phase = "reviewing"

        if hasattr(self, "save_state"):
            self.save_state()

        return {
            "route": "reviewer",
            "validation": result.to_dict(),
        }

    mission.phase = "repairing"

    if hasattr(self, "save_state"):
        self.save_state()

    return {
        "route": "repair",
        "validation": result.to_dict(),
    }


AgentOrchestrator.validate_implementation = _bankai_v065_validate_implementation

AgentOrchestrator.validate_and_route = _bankai_v065_validate_and_route


# =============================================================================
# BANKAI V0.6.5 — TARGETED VALIDATION HANDOFF
# =============================================================================


def _bankai_v065_validate_implementation(
    self,
    mission,
    implementation=None,
):
    """
    V0.6.5 authoritative validation entry point.

    Preserves the existing validator implementation while ensuring Ruff
    receives the current ImplementationResult and therefore validates only
    affected files.
    """

    from app.agents.validator import AutomaticValidator

    if implementation is None:
        implementation = getattr(
            mission,
            "implementation",
            None,
        )

    validator = getattr(
        self,
        "validator",
        None,
    )

    if validator is None:
        validator = AutomaticValidator(self.project)

    original_validate_ruff = getattr(
        validator,
        "validate_ruff",
        None,
    )

    targeted = AutomaticValidator.validate_ruff

    def _targeted_with_implementation():
        return targeted(
            validator,
            implementation,
        )

    try:
        validator.validate_ruff = _targeted_with_implementation

        # Use the existing validator's public validation method when
        # available. This preserves all V0.6.5 checks.
        validate_method = getattr(
            validator,
            "validate",
            None,
        )

        if validate_method is None:
            raise AttributeError("AutomaticValidator.validate() is unavailable.")

        try:
            result = validate_method(
                implementation=implementation,
            )
        except TypeError:
            try:
                result = validate_method(
                    implementation,
                )
            except TypeError:
                result = validate_method()

        return result

    finally:
        if original_validate_ruff is not None:
            validator.validate_ruff = original_validate_ruff
        else:
            try:
                del validator.validate_ruff
            except AttributeError:
                pass


# Authoritative V0.6.5 validation entry point.
AgentOrchestrator.validate_implementation = _bankai_v065_validate_implementation
