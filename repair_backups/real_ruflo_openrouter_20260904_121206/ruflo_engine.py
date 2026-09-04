from dataclasses import dataclass

from app.core.ollama_provider import OllamaProvider


@dataclass
class RufloResult:
    """Result produced by the SOUL FORGE Ruflo pipeline."""

    task: str
    understanding: str = ""
    plan: str = ""
    implementation: str = ""
    validation: str = ""
    review: str = ""
    finalization: str = ""
    simple_explanation: str = ""
    status: str = "READY"


class RufloEngine:
    """
    SOUL FORGE agentic orchestration layer.

    Ollama:
        LLM communication, reasoning and code generation.

    Ruflo:
        Agentic workflow orchestration.

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

    Important:
        This orchestration layer does not claim that code was executed.
        Real execution/testing must come from the execution layer or the user.
    """

    STAGES = [
        "UNDERSTAND",
        "PLAN",
        "IMPLEMENT",
        "VALIDATE",
        "REVIEW",
        "FINALIZE",
    ]

    def __init__(self, ollama=None):
        self.ollama = ollama or OllamaProvider()

    def ask(self, prompt):
        """
        Send one request to the configured Ollama model.
        """
        return self.ollama.generate(
            prompt,
            system=(
                "You are the LLM used by SOUL FORGE. "
                "Ruflo is the orchestration layer. "
                "Never claim that code was executed unless "
                "an actual execution result is provided."
            ),
        )

    def run(self, task, project_context=""):
        """
        Execute the complete Ruflo reasoning pipeline.
        """

        result = RufloResult(
            task=task,
            status="RUNNING",
        )

        # ---------------------------------------------------------------------
        # UNDERSTAND
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # PLAN
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # IMPLEMENT
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # VALIDATE
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # REVIEW
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # FINALIZE
        # ---------------------------------------------------------------------

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
"""
        )

        # ---------------------------------------------------------------------
        # SIMPLE EXPLANATION
        # ---------------------------------------------------------------------

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
"""
        )

        result.status = "READY_FOR_USER_TEST"

        return result
