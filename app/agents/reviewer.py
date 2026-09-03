
"""
BANKAI RACE CONTROL — Reviewer Agent
V0.6.1
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ReviewResult:
    """Result returned by the reviewer."""

    approved: bool
    score: int
    findings: list[str]
    status: str


class ReviewerAgent:
    """
    Reviews implementation results.

    V0.6.1 provides the interface.
    Automated code/test analysis will be expanded in later milestones.
    """

    name = "reviewer"
    role = "review"

    def review(
        self,
        implementation: dict[str, Any],
        validation_passed: bool = False,
    ) -> ReviewResult:
        """Review an implementation result."""

        findings: list[str] = []

        if not implementation:
            findings.append("No implementation result supplied.")

        if not validation_passed:
            findings.append("Validation has not passed.")

        approved = bool(implementation) and validation_passed

        score = 100 if approved else 0

        return ReviewResult(
            approved=approved,
            score=score,
            findings=findings,
            status="approved" if approved else "needs_revision",
        )



# =============================================================================
# V0.6.4 — REVIEWER STRUCTURED IMPLEMENTATION REVIEW REPAIR
# =============================================================================

def _v064_review_implementation_repaired(
    self,
    implementation_plan,
    implementation_result,
    *,
    validation_passed: bool = True,
):
    """
    V0.6.4 structured Coder → Reviewer evaluation.

    Preserves the existing ReviewerAgent API while adding the structured
    implementation review required by the V0.6.4 pipeline.
    """

    if hasattr(implementation_plan, "to_dict"):
        plan = implementation_plan.to_dict()
    elif isinstance(implementation_plan, dict):
        plan = dict(implementation_plan)
    else:
        raise TypeError(
            "implementation_plan must be an ImplementationPlan or dict"
        )

    if hasattr(implementation_result, "to_dict"):
        implementation = implementation_result.to_dict()
    elif isinstance(implementation_result, dict):
        implementation = dict(implementation_result)
    else:
        raise TypeError(
            "implementation_result must be an ImplementationResult or dict"
        )

    planned_modify = set(
        plan.get("files_to_modify", [])
    )

    planned_create = set(
        plan.get("files_to_create", [])
    )

    actual_modify = set(
        implementation.get("files_modified", [])
    )

    actual_create = set(
        implementation.get("files_created", [])
    )

    planned_steps = list(
        plan.get("implementation_steps", [])
    )

    completed_steps = list(
        implementation.get(
            "implementation_steps_completed",
            []
        )
    )

    remaining_steps = list(
        implementation.get(
            "implementation_steps_remaining",
            []
        )
    )

    # -------------------------------------------------------------------------
    # REVIEW CRITERIA
    # -------------------------------------------------------------------------

    criteria = {
        "objective_present": bool(
            implementation.get("objective")
        ),

        "objective_matches_plan": (
            implementation.get("objective", "")
            == plan.get("objective", "")
        ),

        "file_scope_valid": (
            actual_modify.issubset(planned_modify)
            and actual_create.issubset(planned_create)
        ),

        "implementation_steps_present": bool(
            planned_steps
        ),

        "implementation_steps_completed": (
            len(completed_steps) >= len(planned_steps)
        ),

        "validation_evidence_present": bool(
            implementation.get("validation_evidence")
        ),

        "validation_passed": bool(
            validation_passed
        ),

        "no_unresolved_steps": not bool(
            remaining_steps
        ),
    }

    # -------------------------------------------------------------------------
    # REASONS
    # -------------------------------------------------------------------------

    reasons = []

    if not criteria["objective_present"]:
        reasons.append(
            "Coder result does not contain an objective."
        )

    if not criteria["objective_matches_plan"]:
        reasons.append(
            "Coder objective does not match Planner objective."
        )

    if not criteria["file_scope_valid"]:
        reasons.append(
            "Coder output contains files outside the Planner scope."
        )

    if not criteria["implementation_steps_present"]:
        reasons.append(
            "Planner did not provide implementation steps."
        )

    if not criteria["implementation_steps_completed"]:
        reasons.append(
            "Not all planned implementation steps are marked completed."
        )

    if not criteria["validation_evidence_present"]:
        reasons.append(
            "Coder output does not contain validation evidence."
        )

    if not criteria["validation_passed"]:
        reasons.append(
            "Validation gate failed."
        )

    if not criteria["no_unresolved_steps"]:
        reasons.append(
            "Coder reports unresolved implementation steps."
        )

    approved = all(criteria.values())

    if approved:
        status = "approved"
        reasons.append(
            "Coder output satisfies the Planner contract."
        )
    else:
        status = "rejected"

    risks = list(
        implementation.get("risks", [])
    )

    recommendations = []

    if not approved:
        recommendations.append(
            "Repair the failed review criteria before completion."
        )

    # -------------------------------------------------------------------------
    # FIND ReviewResult CLASS
    # -------------------------------------------------------------------------

    ReviewResultClass = globals().get("ReviewResult")

    if ReviewResultClass is None:
        raise RuntimeError(
            "ReviewResult class is missing from reviewer.py"
        )

    return ReviewResultClass(
        status=status,
        approved=approved,
        objective=str(
            plan.get("objective", "")
        ),
        criteria=criteria,
        reasons=reasons,
        risks=risks,
        recommendations=recommendations,
        implementation_status=str(
            implementation.get("status", "")
        ),
    )


# Always repair the method if it is missing.
if "ReviewerAgent" in globals():
    ReviewerAgent.review_implementation = (
        _v064_review_implementation_repaired
    )


# =============================================================================
# BANKAI V0.6.4 — FINAL STRUCTURED CODER → REVIEWER IMPLEMENTATION
# =============================================================================

def _bankai_v064_review_implementation(
    self,
    implementation_plan,
    implementation_result,
    validation_passed=True,
):
    """
    Review a structured ImplementationResult against an ImplementationPlan.

    IMPORTANT:
    ReviewResult in this project has exactly four fields:

        approved
        score
        findings
        status
    """

    findings = []
    checks_passed = 0
    total_checks = 8

    # -------------------------------------------------------------------------
    # 1. PLAN EXISTS
    # -------------------------------------------------------------------------

    if implementation_plan is not None:
        checks_passed += 1
        findings.append(
            "[PASS] Implementation plan received."
        )
    else:
        findings.append(
            "[FAIL] Implementation plan missing."
        )

    # -------------------------------------------------------------------------
    # 2. CODER RESULT EXISTS
    # -------------------------------------------------------------------------

    if implementation_result is not None:
        checks_passed += 1
        findings.append(
            "[PASS] Implementation result received."
        )
    else:
        findings.append(
            "[FAIL] Implementation result missing."
        )

    # -------------------------------------------------------------------------
    # 3. OBJECTIVE ALIGNMENT
    # -------------------------------------------------------------------------

    plan_objective = getattr(
        implementation_plan,
        "objective",
        None,
    )

    result_objective = getattr(
        implementation_result,
        "objective",
        None,
    )

    if (
        plan_objective
        and result_objective
        and plan_objective == result_objective
    ):
        checks_passed += 1
        findings.append(
            "[PASS] Objective alignment confirmed."
        )
    else:
        findings.append(
            "[FAIL] Objective alignment failed."
        )

    # -------------------------------------------------------------------------
    # 4. IMPLEMENTATION STEPS
    # -------------------------------------------------------------------------

    planned_steps = list(
        getattr(
            implementation_plan,
            "implementation_steps",
            [],
        )
        or []
    )

    completed_steps = list(
        getattr(
            implementation_result,
            "implementation_steps_completed",
            [],
        )
        or []
    )

    remaining_steps = list(
        getattr(
            implementation_result,
            "implementation_steps_remaining",
            [],
        )
        or []
    )

    if planned_steps:
        if (
            len(completed_steps) == len(planned_steps)
            and not remaining_steps
        ):
            checks_passed += 1
            findings.append(
                "[PASS] All planned implementation steps completed."
            )
        else:
            findings.append(
                "[FAIL] Implementation steps incomplete."
            )
    else:
        findings.append(
            "[FAIL] No implementation steps supplied by planner."
        )

    # -------------------------------------------------------------------------
    # 5. FILE SCOPE
    # -------------------------------------------------------------------------

    planned_files = set(
        list(
            getattr(
                implementation_plan,
                "files_to_modify",
                [],
            )
            or []
        )
        +
        list(
            getattr(
                implementation_plan,
                "files_to_create",
                [],
            )
            or []
        )
    )

    actual_files = set(
        list(
            getattr(
                implementation_result,
                "files_modified",
                [],
            )
            or []
        )
        +
        list(
            getattr(
                implementation_result,
                "files_created",
                [],
            )
            or []
        )
    )

    # Empty actual file scope is acceptable for V0.6.4 because the current
    # Coder produces a structured implementation result rather than applying
    # autonomous filesystem changes.
    if not actual_files or actual_files.issubset(planned_files):
        checks_passed += 1
        findings.append(
            "[PASS] File scope is within planned scope."
        )
    else:
        findings.append(
            "[FAIL] Coder reported files outside planned scope."
        )

    # -------------------------------------------------------------------------
    # 6. VALIDATION EVIDENCE
    # -------------------------------------------------------------------------

    evidence = list(
        getattr(
            implementation_result,
            "validation_evidence",
            [],
        )
        or []
    )

    if validation_passed and evidence:
        checks_passed += 1
        findings.append(
            "[PASS] Validation evidence present."
        )
    else:
        findings.append(
            "[FAIL] Validation evidence missing or failed."
        )

    # -------------------------------------------------------------------------
    # 7. RISKS / CONSTRAINTS
    # -------------------------------------------------------------------------

    risks = list(
        getattr(
            implementation_result,
            "risks",
            [],
        )
        or []
    )

    constraints = list(
        getattr(
            implementation_result,
            "constraints",
            [],
        )
        or []
    )

    # Risks/constraints are informational in V0.6.4. They do not
    # automatically reject a structured implementation.
    checks_passed += 1

    if risks or constraints:
        findings.append(
            "[PASS] Risks/constraints reviewed."
        )
    else:
        findings.append(
            "[PASS] No blocking risks/constraints reported."
        )

    # -------------------------------------------------------------------------
    # 8. IMPLEMENTATION STATUS
    # -------------------------------------------------------------------------

    implementation_status = str(
        getattr(
            implementation_result,
            "status",
            "",
        )
        or ""
    ).lower()

    valid_statuses = {
        "prepared",
        "implemented",
        "completed",
        "ready",
    }

    if implementation_status in valid_statuses:
        checks_passed += 1
        findings.append(
            "[PASS] Implementation status is reviewable."
        )
    else:
        findings.append(
            "[FAIL] Implementation status is not reviewable."
        )

    # -------------------------------------------------------------------------
    # SCORE
    # -------------------------------------------------------------------------

    score = int(
        round(
            (checks_passed / total_checks) * 100
        )
    )

    approved = (
        checks_passed == total_checks
        and bool(validation_passed)
    )

    status = (
        "approved"
        if approved
        else "rejected"
    )

    # -------------------------------------------------------------------------
    # CRITICAL:
    # Construct ONLY the real ReviewResult schema.
    # -------------------------------------------------------------------------

    return ReviewResult(
        approved=bool(approved),
        score=int(score),
        findings=findings,
        status=str(status),
    )


# Make the V0.6.4 implementation authoritative.
ReviewerAgent.review_implementation = (
    _bankai_v064_review_implementation
)
