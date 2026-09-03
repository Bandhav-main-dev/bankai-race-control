"""Tests for BANKAI V0.6.5 automatic validation."""

from pathlib import Path

from app.agents.coding_agent import ImplementationResult
from app.agents.validator import AutomaticValidator

PROJECT = Path(__file__).resolve().parents[1]


def build_implementation() -> ImplementationResult:
    """Create a schema-compatible V0.6.5 implementation result."""
    return ImplementationResult(
        objective=(
            "Implement automatic validation "
            "for BANKAI Race Control."
        ),
        status="implemented",
        files_modified=[
            "app/agents/validator.py",
            "app/agents/orchestrator.py",
        ],
        files_created=[
            "app/agents/validator.py",
            "tests/test_v065_automatic_validation.py",
        ],
        implementation_steps_completed=[
            "Create AutomaticValidator",
            "Integrate validator with orchestrator",
            "Add validation checks",
            "Add targeted Ruff validation",
        ],
        implementation_steps_remaining=[],
        validation_evidence=[
            "Python syntax validation",
            "Import validation",
            "Targeted Ruff validation",
            "Pytest validation",
        ],
        risks=[],
        constraints=[
            (
                "Do not allow unrelated historical Ruff debt "
                "to block V0.6.5."
            ),
        ],
        notes=(
            "V0.6.5 automatic validation with "
            "targeted Ruff quality gating."
        ),
    )


def test_implementation_result():
    implementation = build_implementation()

    assert implementation.status == "implemented"
    assert len(
        implementation.implementation_steps_completed
    ) == 4


def test_validator_creation():
    validator = AutomaticValidator(PROJECT)

    assert validator is not None


def test_targeted_ruff():
    validator = AutomaticValidator(PROJECT)
    implementation = build_implementation()

    passed, message = validator.validate_ruff(
        implementation
    )

    assert passed, message
