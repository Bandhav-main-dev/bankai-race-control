
"""
BANKAI Local AI Router

BANKAI talks to OmniRoute instead of talking directly
to every individual model.
"""

from __future__ import annotations

from .omniroute_client import OmniRouteClient


class LocalAIRouter:
    """Central AI interface for BANKAI."""

    def __init__(self) -> None:
        self.client = OmniRouteClient()

    def ask(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:

        return self.client.chat(
            prompt=prompt,
            model=model,
            system=(
                "You are BANKAI, a local AI coding assistant. "
                "Produce reliable, readable and testable code. "
                "When modifying a project, explain the intended "
                "change before generating implementation."
            ),
        )

    def generate_code(
        self,
        task: str,
        model: str | None = None,
    ) -> str:

        prompt = f"""
You are BANKAI's code-generation engine.

TASK:
{task}

Requirements:

1. Analyze the task.
2. Determine the files that should change.
3. Generate production-quality code.
4. Avoid unnecessary dependencies.
5. Preserve existing architecture.
6. Include tests when appropriate.
7. Clearly separate explanation from code.
"""

        return self.ask(
            prompt=prompt,
            model=model,
        )


if __name__ == "__main__":
    router = LocalAIRouter()

    result = router.generate_code(
        "Create a Python function that checks whether a number is prime."
    )

    print(result)
