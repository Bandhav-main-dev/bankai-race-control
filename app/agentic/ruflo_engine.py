
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
from datetime import datetime

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

        normalized_task = str(
            task
        ).upper()

        # ---------------------------------------------------------------------
        # Resolve routing information BEFORE making the request.
        # This avoids depending on optional response metadata.
        # ---------------------------------------------------------------------

        requested_models = []

        try:
            requested_models = self.provider.get_models(
                normalized_task
            )
        except Exception:
            requested_models = []

        if not isinstance(
            requested_models,
            list,
        ):
            requested_models = [
                str(requested_models)
            ]

        requested_models = [
            str(model)
            for model in requested_models
            if model
        ]

        requested_model = (
            requested_models[0]
            if requested_models
            else ""
        )

        tier_name = ""

        try:
            tier_name = self.provider.get_tier(
                normalized_task
            )
        except Exception:
            tier_name = ""

        provider_name = (
            getattr(
                self.provider,
                "name",
                None,
            )
            or "openrouter"
        )

        # ---------------------------------------------------------------------
        # REAL MODEL REQUEST
        # ---------------------------------------------------------------------

        result = self.provider.generate(

            prompt=prompt,

            task=normalized_task,

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
            __import__("time").time()
            - started,
            2,
        )

        # ---------------------------------------------------------------------
        # NORMALIZE PROVIDER RESPONSE
        # ---------------------------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            content = result.get(
                "content",
                "",
            )

            response_provider = result.get(
                "provider",
                provider_name,
            )

            response_tier = result.get(
                "tier",
                tier_name,
            )

            response_requested = result.get(
                "requested_model",
                requested_model,
            )

            response_requested_models = result.get(
                "requested_models",
                requested_models,
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

            provider_elapsed = result.get(
                "elapsed",
                elapsed,
            )

            response_status = result.get(
                "status",
                "success",
            )

        else:

            content = str(
                result
            )

            response_provider = provider_name

            response_tier = tier_name

            response_requested = requested_model

            response_requested_models = (
                requested_models
            )

            actual_model = ""

            provider_elapsed = elapsed

            response_status = "success"

        # ---------------------------------------------------------------------
        # GUARANTEE LIST FORMAT
        # ---------------------------------------------------------------------

        if not isinstance(
            response_requested_models,
            list,
        ):

            response_requested_models = [
                str(
                    response_requested_models
                )
            ]

        response_requested_models = [
            str(model)
            for model
            in response_requested_models
            if model
        ]

        if not response_requested:
            response_requested = (
                response_requested_models[0]
                if response_requested_models
                else requested_model
            )

        if not response_tier:
            response_tier = tier_name

        if not response_provider:
            response_provider = provider_name

        # ---------------------------------------------------------------------
        # FALLBACK DETECTION
        # ---------------------------------------------------------------------

        fallback = bool(
            response_requested
            and actual_model
            and response_requested
            != actual_model
        )

        # ---------------------------------------------------------------------
        # APPLICATION-OWNED TELEMETRY
        # ---------------------------------------------------------------------

        self.last_telemetry = {

            "timestamp":
                datetime.now().isoformat(
                    timespec="seconds"
                ),

            "task":
                normalized_task,

            "provider":
                response_provider,

            "tier":
                response_tier,

            "requested_model":
                response_requested,

            "requested_models":
                response_requested_models,

            "actual_model":
                actual_model,

            "selected_model":
                actual_model,

            "latency_seconds":
                provider_elapsed,

            "status":
                response_status,

            "fallback":
                fallback,
        }

        # ---------------------------------------------------------------------
        # VALIDATE CONTENT
        # ---------------------------------------------------------------------

        if not content:

            raise RuntimeError(
                "SOUL FORGE provider returned no content"
            )

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
