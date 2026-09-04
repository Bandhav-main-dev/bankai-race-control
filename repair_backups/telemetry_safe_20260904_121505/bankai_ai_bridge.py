
"""
BANKAI AI BRIDGE
================

Production provider layer for SOUL FORGE.

Responsibilities:

    CHAT
    PLANNING
    CODING
    TESTING
    REVIEW
    KNOWLEDGE

Architecture:

    BANKAI UI
        ↓
    bankai_chat()
        ↓
    OpenRouter
        ↓
    model fallback
        ↓
    Ollama emergency fallback

This module does not:
    - modify repositories
    - execute shell commands
    - perform Git operations
"""

from __future__ import annotations

from typing import Any

from app.core.openrouter_provider import (
    get_openrouter_provider,
)


# =============================================================================
# MODEL ROUTING
# =============================================================================

MODEL_ROUTING = {

    "CHAT": {
        "provider": "openrouter",
        "tier": "tier_1_primary",
        "description": "General SOUL FORGE conversation",
    },

    "PLANNING": {
        "provider": "openrouter",
        "tier": "tier_3_secondary",
        "description": "Planning and reasoning",
    },

    "CODING": {
        "provider": "openrouter",
        "tier": "tier_1_primary",
        "description": "Coding assistance",
    },

    "TESTING": {
        "provider": "openrouter",
        "tier": "tier_2_coding",
        "description": "Testing and debugging",
    },

    "REVIEW": {
        "provider": "openrouter",
        "tier": "tier_2_coding",
        "description": "Code and architecture review",
    },

    "KNOWLEDGE": {
        "provider": "openrouter",
        "tier": "tier_3_secondary",
        "description": "Knowledge/source-grounded conversation",
    },
}


# =============================================================================
# INTENT DETECTION
# =============================================================================

def detect_intent(message: str) -> str:

    text = message.lower().strip()

    if not text:
        return "CHAT"

    coding_patterns = [

        "write code",
        "build",
        "create an app",
        "create a website",
        "make a website",
        "implement",
        "program",
        "code this",
        "fix this code",
        "modify this code",
        "debug",
        "python code",
        "streamlit app",
        "django app",
        "react app",
        "javascript code",
        "run tests",
        "test this",
        "refactor",
        "repository",
        "repo",
        "github",
    ]

    planning_patterns = [

        "plan",
        "planning",
        "architecture",
        "roadmap",
        "design the system",
        "how should i build",
        "how do i build",
        "strategy",
        "project plan",
    ]

    testing_patterns = [

        "run test",
        "run tests",
        "pytest",
        "test failure",
        "test failed",
        "testing",
        "find the bug",
        "debug this",
    ]

    review_patterns = [

        "review this",
        "review the code",
        "review my code",
        "review this code",
        "review my project",
        "code review",
        "audit",
        "inspect the code",
        "inspect my code",
        "check my code",
        "security review",
    ]

    knowledge_patterns = [

        "according to",
        "from the document",
        "from the documents",
        "from the pdf",
        "from my files",
        "summarize this document",
        "what does the document say",
        "what does the paper say",
    ]

    if any(
        pattern in text
        for pattern in review_patterns
    ):

        return "REVIEW"

    if any(
        pattern in text
        for pattern in testing_patterns
    ):

        return "TESTING"

    if any(
        pattern in text
        for pattern in planning_patterns
    ):

        return "PLANNING"

    if any(
        pattern in text
        for pattern in knowledge_patterns
    ):

        return "KNOWLEDGE"

    if any(
        pattern in text
        for pattern in coding_patterns
    ):

        return "CODING"

    return "CHAT"


# =============================================================================
# PROMPTS
# =============================================================================

PROMPTS = {

    "CHAT": """
You are SOUL FORGE, the conversational AI inside
BANKAI RACE CONTROL.

You can:
- chat naturally
- explain concepts
- answer questions
- brainstorm
- discuss science
- help with projects
- plan tasks
- assist with software

Do not turn every conversation into a coding task.

Be intelligent, direct and helpful.
""",

    "PLANNING": """
You are SOUL FORGE PLANNER.

Analyze the user's objective and create a practical plan.

Focus on:

1. Objective
2. Requirements
3. Architecture
4. Steps
5. Risks
6. Validation

Do not claim that files were modified.
Do not claim tests ran unless actual execution results are supplied.
""",

    "CODING": """
You are SOUL FORGE CODER.

Help the user implement software.

Provide:

- correct code
- architecture
- implementation details
- testing considerations
- edge cases
- security considerations

Never claim code was executed unless actual execution results
are provided.
Never claim files were modified unless an actual file operation
was performed.
""",

    "TESTING": """
You are SOUL FORGE TEST ENGINEER.

Focus on:

- identifying failures
- test strategy
- debugging
- pytest
- validation
- regression prevention
- likely runtime failures

Never claim a test passed unless an actual test result is supplied.
""",

    "REVIEW": """
You are SOUL FORGE REVIEWER.

Review the user's code or architecture.

Look for:

- correctness
- bugs
- maintainability
- security
- performance
- architecture problems
- integration problems

Give actionable fixes.
""",

    "KNOWLEDGE": """
You are SOUL FORGE KNOWLEDGE ASSISTANT.

Answer using supplied source context when available.

Clearly distinguish:

- information from sources
- general knowledge
- uncertainty

Never invent information from a source.
""",
}


# =============================================================================
# BANKAI CHAT
# =============================================================================

def bankai_chat(
    message: str,
    conversation: list[dict[str, Any]] | None = None,
    force_intent: str | None = None,
) -> dict[str, Any]:

    if not message or not message.strip():

        return {
            "text": (
                "SOUL FORGE is ready. "
                "What would you like to do?"
            ),
            "intent": "CHAT",
            "provider": "none",
            "model": "none",
            "status": "ready",
        }

    intent = (
        force_intent.upper()
        if force_intent
        else detect_intent(message)
    )

    if intent not in MODEL_ROUTING:

        intent = "CHAT"

    system_prompt = PROMPTS.get(
        intent,
        PROMPTS["CHAT"],
    )

    provider = get_openrouter_provider()

    try:

        result = provider.generate(

            prompt=message,

            system=system_prompt,

            task=intent,

        )

        if result.get("success"):

            return {

                "text": result["content"],

                "intent": intent,

                "provider": result["provider"],

                "model": result["selected_model"],

                "requested_model": result[
                    "requested_model"
                ],

                "requested_models": result[
                    "requested_models"
                ],

                "tier": result["tier"],

                "elapsed": result["elapsed"],

                "status": "success",
            }

        return {

            "text": (
                "SOUL FORGE received the request, "
                "but the model returned no text."
            ),

            "intent": intent,

            "provider": "openrouter",

            "model": result.get(
                "selected_model",
                "unknown",
            ),

            "status": "empty",

        }

    except Exception as exc:

        return {

            "text": (
                "SOUL FORGE detected this as "
                f"**{intent}**, but the OpenRouter "
                "provider failed.\n\n"
                f"Error: `{exc}`"
            ),

            "intent": intent,

            "provider": "openrouter",

            "model": "unknown",

            "status": "error",

            "error": str(exc),
        }


# =============================================================================
# ROUTING INFORMATION
# =============================================================================

def get_route_info(
    intent: str | None = None,
) -> dict[str, Any]:

    if intent:

        return MODEL_ROUTING.get(
            intent.upper(),
            MODEL_ROUTING["CHAT"],
        )

    return MODEL_ROUTING


# =============================================================================
# HEALTH CHECK
# =============================================================================

def health_check() -> dict[str, Any]:

    try:

        provider = get_openrouter_provider()

        routes = {}

        for intent in MODEL_ROUTING:

            routes[intent] = {

                "provider": "openrouter",

                "tier": provider.get_tier(
                    intent
                ),

                "models": provider.get_models(
                    intent
                ),
            }

        return {

            "openrouter": True,

            "ollama_emergency": True,

            "routes": routes,

            "status": "healthy",
        }

    except Exception as exc:

        return {

            "openrouter": False,

            "ollama_emergency": True,

            "routes": MODEL_ROUTING,

            "status": "error",

            "error": str(exc),
        }
