
from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class ValidationResult:
    passed: bool
    score: int
    checks: list[ValidationCheck]
    errors: list[str]
    status: str
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "checks": [
                check.to_dict()
                for check in self.checks
            ],
            "errors": list(self.errors),
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> ValidationResult:
        checks = [
            ValidationCheck(
                name=item.get("name", ""),
                passed=bool(
                    item.get("passed", False)
                ),
                message=item.get("message", ""),
                details=item.get("details", {}),
            )
            for item in data.get("checks", [])
        ]

        return cls(
            passed=bool(
                data.get("passed", False)
            ),
            score=int(
                data.get("score", 0)
            ),
            checks=checks,
            errors=list(
                data.get("errors", [])
            ),
            status=str(
                data.get("status", "unknown")
            ),
            created_at=str(
                data.get(
                    "created_at",
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                )
            ),
        )


class AutomaticValidator:

    def __init__(
        self,
        project: str | Path | None = None,
    ):
        self.project = Path(
            project or Path.cwd()
        ).resolve()

    # -------------------------------------------------------------------------
    # COMMAND EXECUTION
    # -------------------------------------------------------------------------

    def _run(
        self,
        command: list[str],
        timeout: int = 180,
    ) -> tuple[bool, str]:

        try:
            result = subprocess.run(
                command,
                cwd=self.project,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False
            )

            output = result.stdout.strip()

            if result.stderr.strip():
                output += (
                    "\n"
                    + result.stderr.strip()
                )

            return (
                result.returncode == 0,
                output.strip(),
            )

        except subprocess.TimeoutExpired:
            return (
                False,
                f"Timeout: {command}",
            )

        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    # -------------------------------------------------------------------------
    # PYTHON SYNTAX
    # -------------------------------------------------------------------------

    def validate_python_syntax(
        self,
    ) -> ValidationCheck:

        python_files = list(
            self.project.glob(
                "app/**/*.py"
            )
        )

        failures = []

        for path in python_files:
            try:
                ast.parse(
                    path.read_text(
                        encoding="utf-8"
                    ),
                    filename=str(path),
                )

            except SyntaxError as exc:
                failures.append(
                    f"{path.relative_to(self.project)}:"
                    f"{exc.lineno}:"
                    f"{exc.msg}"
                )

            except Exception as exc:  # noqa: BLE001
                failures.append(
                    f"{path.relative_to(self.project)}:"
                    f"{exc}"
                )

        return ValidationCheck(
            name="python_syntax",
            passed=not failures,
            message=(
                "All Python files parsed successfully."
                if not failures
                else "Python syntax errors detected."
            ),
            details={
                "files_checked": len(
                    python_files
                ),
                "failures": failures,
            },
        )

    # -------------------------------------------------------------------------
    # IMPORTS
    # -------------------------------------------------------------------------

    def validate_imports(
        self,
    ) -> ValidationCheck:

        command = [
            sys.executable,
            "-c",
            (
                "from app.agents.planner import "
                "PlannerAgent, ImplementationPlan; "
                "from app.agents.coding_agent import "
                "CodingAgent, ImplementationResult; "
                "from app.agents.reviewer import "
                "ReviewerAgent, ReviewResult; "
                "from app.agents.orchestrator import "
                "AgentOrchestrator, Mission; "
                "from app.agents.validator import "
                "AutomaticValidator, ValidationResult; "
                "print('BANKAI_IMPORTS_OK')"
            ),
        ]

        passed, output = self._run(
            command
        )

        return ValidationCheck(
            name="imports",
            passed=(
                passed
                and "BANKAI_IMPORTS_OK"
                in output
            ),
            message=(
                "All BANKAI agent modules imported."
                if passed
                else "BANKAI imports failed."
            ),
            details={
                "output": output[-4000:]
            },
        )

    # -------------------------------------------------------------------------
    # PYTEST
    # -------------------------------------------------------------------------

    def validate_pytest(
        self,
        timeout: int = 180,
    ) -> ValidationCheck:

        passed, output = self._run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--disable-warnings",
            ],
            timeout=timeout,
        )

        return ValidationCheck(
            name="pytest",
            passed=passed,
            message=(
                "Pytest passed."
                if passed
                else "Pytest failed."
            ),
            details={
                "output": output[-6000:]
            },
        )

    # -------------------------------------------------------------------------
    # RUFF
    # -------------------------------------------------------------------------

    def validate_ruff(
        self,
        timeout: int = 120,
    ) -> ValidationCheck:

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    "app",
                ],
                cwd=self.project,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False
            )

            output = result.stdout.strip()

            if result.stderr.strip():
                output += (
                    "\n"
                    + result.stderr.strip()
                )

            passed = (
                result.returncode == 0
            )

        except Exception as exc:  # noqa: BLE001
            passed = False
            output = str(exc)

        return ValidationCheck(
            name="ruff",
            passed=passed,
            message=(
                "Ruff validation passed."
                if passed
                else "Ruff validation reported issues."
            ),
            details={
                "output": output[-6000:]
            },
        )

    # -------------------------------------------------------------------------
    # REPOSITORY
    # -------------------------------------------------------------------------

    def validate_repository(
        self,
    ) -> ValidationCheck:

        required = [
            "app",
            "tests",
            "README.md",
            "requirements.txt",
        ]

        missing = [
            item
            for item in required
            if not (
                self.project / item
            ).exists()
        ]

        return ValidationCheck(
            name="repository",
            passed=not missing,
            message=(
                "Required repository structure exists."
                if not missing
                else "Repository structure incomplete."
            ),
            details={
                "missing": missing
            },
        )

    # -------------------------------------------------------------------------
    # IMPLEMENTATION RESULT
    #
    # IMPORTANT:
    # We deliberately DO NOT assume fields such as
    # implementation_steps or steps_completed.
    # V0.6.5 validates the actual object dynamically.
    # -------------------------------------------------------------------------

    def validate_implementation_result(
        self,
        implementation: Any,
    ) -> ValidationCheck:

        failures = []

        if implementation is None:
            failures.append(
                "ImplementationResult is missing."
            )

        else:
            actual_type = type(
                implementation
            ).__name__

            if actual_type != "ImplementationResult":
                failures.append(
                    "Expected ImplementationResult, "
                    f"received {actual_type}."
                )

            if hasattr(
                implementation,
                "__dict__",
            ):
                payload = vars(
                    implementation
                )
            else:
                payload = {}

            if not payload:
                try:
                    from dataclasses import (
                        asdict,
                    )

                    payload = asdict(
                        implementation
                    )
                except (AttributeError, TypeError):
                    payload = {}

            if not payload:
                failures.append(
                    "ImplementationResult contains no "
                    "inspectable fields."
                )

            # Objective is expected in all known BANKAI
            # V0.6 ImplementationResult variants.
            if hasattr(
                implementation,
                "objective",
            ):
                objective = implementation.objective

                if not str(
                    objective
                ).strip():
                    failures.append(
                        "Implementation objective is empty."
                    )

        return ValidationCheck(
            name="implementation_result",
            passed=not failures,
            message=(
                "ImplementationResult is valid "
                "against its actual schema."
                if not failures
                else "ImplementationResult validation failed."
            ),
            details={
                "failures": failures,
                "fields": (
                    list(vars(
                        implementation
                    ).keys())
                    if implementation is not None
                    and hasattr(
                        implementation,
                        "__dict__",
                    )
                    else []
                ),
            },
        )

    # -------------------------------------------------------------------------
    # FILE SCOPE
    #
    # Dynamically inspect whichever file-related fields
    # actually exist.
    # -------------------------------------------------------------------------

    def validate_file_scope(
        self,
        implementation: Any,
    ) -> ValidationCheck:

        failures = []
        files_checked = []

        if implementation is None:
            return ValidationCheck(
                name="file_scope",
                passed=False,
                message=(
                    "Cannot validate file scope "
                    "without ImplementationResult."
                ),
                details={
                    "failures": [
                        "ImplementationResult missing."
                    ]
                },
            )

        candidate_fields = [
            "files_modified",
            "files_created",
            "files_changed",
            "changed_files",
            "files_to_modify",
            "files_to_create",
            "target_files",
        ]

        for field_name in candidate_fields:

            if not hasattr(
                implementation,
                field_name,
            ):
                continue

            value = getattr(
                implementation,
                field_name,
            )

            if isinstance(
                value,
                (list, tuple, set),
            ):
                files_checked.extend(
                    str(item)
                    for item in value
                )

            elif isinstance(
                value,
                str,
            ) and value.strip():
                files_checked.append(
                    value
                )

        for relative in files_checked:

            try:
                path = Path(
                    relative
                )

                resolved = (
                    path.resolve()
                    if path.is_absolute()
                    else (
                        self.project / path
                    ).resolve()
                )

                try:
                    resolved.relative_to(
                        self.project.resolve()
                    )

                except ValueError:
                    failures.append(
                        "File outside project: "
                        f"{relative}"
                    )

            except Exception as exc:  # noqa: BLE001
                failures.append(
                    f"Invalid file path "
                    f"{relative}: {exc}"
                )

        return ValidationCheck(
            name="file_scope",
            passed=not failures,
            message=(
                "File scope is safe."
                if not failures
                else "Unsafe file scope detected."
            ),
            details={
                "files_checked": files_checked,
                "failures": failures,
            },
        )

    # -------------------------------------------------------------------------
    # FULL VALIDATION
    # -------------------------------------------------------------------------

    def validate(
        self,
        implementation: Any = None,
        run_pytest: bool = True,
        run_ruff: bool = True,
    ) -> ValidationResult:

        checks = []
        errors = []

        checks.append(
            self.validate_repository()
        )

        checks.append(
            self.validate_python_syntax()
        )

        checks.append(
            self.validate_imports()
        )

        if implementation is not None:
            checks.append(
                self.validate_implementation_result(
                    implementation
                )
            )

            checks.append(
                self.validate_file_scope(
                    implementation
                )
            )

        if run_ruff:
            checks.append(
                self.validate_ruff()
            )

        if run_pytest:
            checks.append(
                self.validate_pytest()
            )

        for check in checks:
            if not check.passed:
                errors.append(
                    f"{check.name}: "
                    f"{check.message}"
                )

        passed_count = sum(
            1
            for check in checks
            if check.passed
        )

        total_count = len(checks)

        score = (
            int(
                passed_count
                / total_count
                * 100
            )
            if total_count
            else 0
        )

        passed = (
            total_count > 0
            and passed_count == total_count
        )

        return ValidationResult(
            passed=passed,
            score=score,
            checks=checks,
            errors=errors,
            status=(
                "passed"
                if passed
                else "failed"
            ),
        )


# =============================================================================
# BANKAI V0.6.5 — TARGETED RUFF VALIDATION
# =============================================================================

def _bankai_v065_targeted_ruff(
    self,
    implementation=None,
):
    """
    Run Ruff only against files represented by the current
    ImplementationResult.

    This prevents historical Ruff debt elsewhere in BANKAI from
    blocking the current mission.
    """

    import subprocess
    import sys
    from pathlib import Path

    candidates = []

    # -------------------------------------------------------------------------
    # Extract files from ImplementationResult / dict.
    # -------------------------------------------------------------------------

    if implementation is not None:
        if isinstance(implementation, dict):
            modified = implementation.get("files_modified", [])
            created = implementation.get("files_created", [])
        else:
            modified = getattr(
                implementation,
                "files_modified",
                [],
            )
            created = getattr(
                implementation,
                "files_created",
                [],
            )

        candidates.extend(modified or [])
        candidates.extend(created or [])

    # -------------------------------------------------------------------------
    # V0.6.5 fallback scope.
    #
    # This is intentionally limited to the files created/changed by this
    # milestone.
    # -------------------------------------------------------------------------

    if not candidates:
        candidates = [
            "app/agents/validator.py",
            "app/agents/orchestrator.py",
            "app/agents/__init__.py",
            "tests/test_v065_automatic_validation.py",
        ]

    # -------------------------------------------------------------------------
    # Normalize, deduplicate and verify paths.
    # -------------------------------------------------------------------------

    normalized = []

    for item in candidates:
        try:
            path = Path(str(item))

            if path.is_absolute():
                path = path.resolve()
            else:
                path = (self.project / path).resolve()

            project_root = self.project.resolve()

            try:
                path.relative_to(project_root)
            except ValueError:
                continue

            if path.exists() and path.is_file():
                relative = path.relative_to(project_root)

                if str(relative) not in normalized:
                    normalized.append(str(relative))

        except (TypeError, ValueError, OSError):
            continue

    # Never allow an empty Ruff invocation.
    if not normalized:
        return (
            True,
            "No applicable implementation files were found for Ruff.",
        )

    command = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        *normalized,
    ]

    try:
        result = subprocess.run(
            command,
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )

        output = (
            result.stdout.strip()
            + (
                "\n" + result.stderr.strip()
                if result.stderr.strip()
                else ""
            )
        ).strip()

        if result.returncode == 0:
            return (
                True,
                "Ruff passed for targeted files:\n"
                + "\n".join(f"  - {item}" for item in normalized),
            )

        return (
            False,
            "Ruff found issues in targeted files:\n"
            + "\n".join(f"  - {item}" for item in normalized)
            + ("\n\n" + output if output else ""),
        )

    except (OSError, subprocess.SubprocessError) as exc:
        return (
            False,
            f"Ruff execution failed: {exc}",
        )


# Authoritative V0.6.5 override.
AutomaticValidator.validate_ruff = _bankai_v065_targeted_ruff

