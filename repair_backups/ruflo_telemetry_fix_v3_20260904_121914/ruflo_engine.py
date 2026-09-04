
"""
SOUL FORGE RUFLO ENGINE
=======================

Ruflo is the orchestration layer.

LLM communication is provided by:
    OpenRouter

Fallback:
    OpenRouter model fallback
    ->
    alternate tier
    ->
    optional Ollama emergency provider

Pipeline:

    UNDERSTAND
        ↓
    PLAN
        ↓
    IMPLEMENT
        ↓
    VALIDATE
        ↓
    REVIEW
        ↓
    FINALIZE
        ↓
    SIMPLE EXPLANATION

Important:

This orchestration layer does not claim that code was executed.

Real execution/testing must come from the execution layer
or actual tool results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.openrouter_provider import (
    get_openrouter_provider,
)


@dataclass
class RufloResult:

    task: str

    understanding: str = ""

    plan: str = ""

    implementation: str = ""

    validation: str = ""

    review: str = ""

    finalization: str = ""

    simple_explanation: str = ""

    status: str = "READY"

    # Production telemetry
    provider: str = ""

    selected_models: list[str] | None = None

    elapsed_seconds: float = 0.0


class RufloEngine:

    """
    SOUL FORGE agentic orchestration layer.

    Ruflo:
        workflow orchestration

    OpenRouter:
        model communication and fallback

    Pipeline:
        UNDERSTAND
        PLAN
        IMPLEMENT
        VALIDATE
        REVIEW
        FINALIZE
        SIMPLE EXPLANATION
    """

    STAGES = [

        "UNDERSTAND",

        "PLAN",

        "IMPLEMENT",

        "VALIDATE",

        "REVIEW",

        "FINALIZE",
    ]

    def __init__(
        self,
        ollama=None,
        provider=None,
    ):

        # Backward compatibility:
        # callers may still pass ollama.
        self.ollama = ollama

        self.provider = (
            provider
            or get_openrouter_provider()
        )

        self.last_telemetry = {}

    # -------------------------------------------------------------------------
    # LLM REQUEST
    # -------------------------------------------------------------------------

    def ask(
        self,
        prompt: str,
        task: str = "CHAT",
    ) -> str:

        started = __import__(
            "time"
        ).time()

        result = self.provider.generate(

            prompt=prompt,

            task=task,

            system=(
                "You are the LLM used by SOUL FORGE. "
                "Ruflo is the orchestration layer. "
                "Never claim that code was executed unless "
                "an actual execution result is provided. "
                "Never claim that files were modified unless "
                "an actual file operation is provided."
            ),
        )

        elapsed = round(
            __import__("time").time() - started,
            2,
        )

        if not isinstance(result, dict):

            result = {
                "content": str(result),
                "status": "success",
            }

        content = result.get(
            "content",
            "",
        )

        if not content:

            raise RuntimeError(
                "SOUL FORGE provider returned no content"
            )

        requested_models = result.get(
            "requested_models",
            [],
        )

        if not isinstance(
            requested_models,
            list,
        ):

            requested_models = [
                str(requested_models)
            ]

        requested_model = result.get(
            "requested_model",
            "",
        )

        actual_model = (
            result.get(
                "selected_model",
                "",
            )
            or result.get(
                "model",
                "",
            )
        )

        provider_name = result.get(
            "provider",
            "openrouter",
        )

        tier_name = result.get(
            "tier",
            "",
        )

        provider_elapsed = result.get(
            "elapsed",
            elapsed,
        )

        fallback = bool(
            requested_model
            and actual_model
            and requested_model != actual_model
        )

        self.last_telemetry = {

            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),

            "task": str(
                task
            ).upper(),

            "provider": provider_name,

            "tier": tier_name,

            "requested_model": requested_model,

            "requested_models": requested_models,

            "actual_model": actual_model,

            "selected_model": actual_model,

            "latency_seconds": provider_elapsed,

            "status": result.get(
                "status",
                "success",
            ),

            "fallback": fallback,
        }

        return content

    def run(
        self,
        task,
        project_context="",
    ):

        started = __import__(
            "time"
        ).time()

        result = RufloResult(

            task=task,

            status="RUNNING",

            provider="openrouter",

            selected_models=[],
        )

        # =====================================================================
        # UNDERSTAND
        # =====================================================================

        result.understanding = self.ask(

            f"""
UNDERSTAND

User development request:

{task}

Project context:

{project_context}

Determine exactly what the user wants.

Identify:

- requirements
- constraints
- risks
- affected components
- assumptions
""",

            task="PLANNING",
        )

        # =====================================================================
        # PLAN
        # =====================================================================

        result.plan = self.ask(

            f"""
PLAN

Development request:

{task}

Understanding:

{result.understanding}

Create a concrete implementation plan.

Include:

- files that may need modification
- architecture
- dependencies
- implementation order
- testing strategy
- risks
""",

            task="PLANNING",
        )

        # =====================================================================
        # IMPLEMENT
        # =====================================================================

        result.implementation = self.ask(

            f"""
IMPLEMENT

Task:

{task}

Understanding:

{result.understanding}

Plan:

{result.plan}

Generate the complete implementation.

Rules:

1. Produce real code.
2. Keep the existing architecture in mind.
3. Do not invent execution results.
4. Clearly identify files for multi-file code.
5. Prefer maintainable production-quality code.
6. Do not claim that files were actually modified.
""",

            task="CODING",
        )

        # =====================================================================
        # VALIDATE
        # =====================================================================

        result.validation = self.ask(

            f"""
VALIDATE

Task:

{task}

Proposed implementation:

{result.implementation}

Perform static engineering validation.

Check:

- Python syntax
- logic
- imports
- dependencies
- security
- edge cases
- integration
- likely runtime failures

Do NOT claim that tests actually ran.
""",

            task="TESTING",
        )

        # =====================================================================
        # REVIEW
        # =====================================================================

        result.review = self.ask(

            f"""
REVIEW

Task:

{task}

Implementation:

{result.implementation}

Validation:

{result.validation}

Act as a senior software reviewer.

Identify:

- bugs
- missing requirements
- architectural problems
- security problems
- maintainability problems
- anything that should be corrected
""",

            task="REVIEW",
        )

        # =====================================================================
        # FINALIZE
        # =====================================================================

        result.finalization = self.ask(

            f"""
FINALIZE

Task:

{task}

Implementation:

{result.implementation}

Validation:

{result.validation}

Review:

{result.review}

Create the final recommended implementation.

List:

- final code
- required changes
- remaining risks
- user testing steps

Do not claim that the implementation was executed.
""",

            task="CODING",
        )

        # =====================================================================
        # SIMPLE EXPLANATION
        # =====================================================================

        result.simple_explanation = self.ask(

            f"""
EXPLAIN SIMPLY

Explain this development task to the user
in very simple language.

Task:

{task}

Final result:

{result.finalization}

Explain:

- what was created
- why it was created
- what the user should test
- what could still fail

Avoid unnecessary technical jargon.
""",

            task="CHAT",
        )

        # =====================================================================
        # TELEMETRY
        # =====================================================================

        result.elapsed_seconds = (
            __import__(
                "time"
            ).time()
            - started
        )

        try:

            all_models = []

            for stage in [
                "PLANNING",
                "CODING",
                "TESTING",
                "REVIEW",
                "CHAT",
            ]:

                models = self.provider.get_models(
                    stage
                )

                for model in models:

                    if model not in all_models:

                        all_models.append(
                            model
                        )

            result.selected_models = all_models

        except Exception:

            result.selected_models = []

        result.status = (
            "READY_FOR_USER_TEST"
        )

        return result
