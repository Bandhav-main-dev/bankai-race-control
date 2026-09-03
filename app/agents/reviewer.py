
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
