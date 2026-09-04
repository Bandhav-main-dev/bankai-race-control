
"""
BANKAI AI BRIDGE
================

Safe provider layer for BANKAI RACE CONTROL.

Responsibilities:
    CHAT      -> General chatbot
    PLANNING  -> Planning/reasoning
    KNOWLEDGE -> Knowledge questions
    AGENT     -> Agentic/coding requests

This file does NOT modify repositories, execute shell commands,
or perform Git operations.

It only provides model communication.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any


# =============================================================================
# MODEL ROUTING
# =============================================================================

MODEL_ROUTING = {
    "CHAT": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_CHAT_MODEL", "qwen3:latest"),
        "description": "General BANKAI conversation",
    },

    "PLANNING": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_PLANNER_MODEL", "qwen3:latest"),
        "description": "Planning and reasoning",
    },

    "CODING": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_CODER_MODEL", "qwen3:latest"),
        "description": "Coding assistance",
    },

    "TESTING": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_TESTER_MODEL", "qwen3:latest"),
        "description": "Testing and debugging",
    },

    "REVIEW": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_REVIEWER_MODEL", "qwen3:latest"),
        "description": "Code and architecture review",
    },

    "KNOWLEDGE": {
        "provider": "ollama",
        "model": os.getenv("BANKAI_KNOWLEDGE_MODEL", "qwen3:latest"),
        "description": "Knowledge/source-grounded conversation",
    },
}


# =============================================================================
# INTENT DETECTION
# =============================================================================

def detect_intent(message: str) -> str:
    """
    Determine what BANKAI should do with the user's message.

    BANKAI is a general chatbot first.
    Coding/agent behavior is activated only when appropriate.
    """

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
        "code review",
        "audit",
        "inspect the code",
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

    if any(pattern in text for pattern in review_patterns):
        return "REVIEW"

    if any(pattern in text for pattern in testing_patterns):
        return "TESTING"

    if any(pattern in text for pattern in planning_patterns):
        return "PLANNING"

    if any(pattern in text for pattern in knowledge_patterns):
        return "KNOWLEDGE"

    if any(pattern in text for pattern in coding_patterns):
        return "CODING"

    return "CHAT"


# =============================================================================
# OLLAMA
# =============================================================================

def ollama_available() -> bool:
    """Check whether Ollama is reachable."""

    try:
        import requests

        response = requests.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=3,
        )

        return response.ok

    except Exception:
        return False


def ollama_chat(
    message: str,
    model: str,
    system_prompt: str = "",
) -> str:
    """Send a chat request to Ollama."""

    import requests

    payload = {
        "model": model,
        "stream": False,
        "messages": [],
    }

    if system_prompt:
        payload["messages"].append({
            "role": "system",
            "content": system_prompt,
        })

    payload["messages"].append({
        "role": "user",
        "content": message,
    })

    response = requests.post(
        "http://127.0.0.1:11434/api/chat",
        json=payload,
        timeout=180,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data.get("message", {}).get("content")
        or data.get("response")
        or "BANKAI received the request but the model returned no text."
    )


# =============================================================================
# PROMPTS
# =============================================================================

PROMPTS = {

    "CHAT": """
You are BANKAI, the conversational AI inside BANKAI RACE CONTROL.

You are not only a coding assistant.

You can:
- chat naturally
- explain concepts
- answer questions
- brainstorm
- help with projects
- discuss science
- help plan tasks
- assist with coding when requested

Do not turn every conversation into a coding task.

Be intelligent, direct and helpful.
""",

    "PLANNING": """
You are BANKAI PLANNER.

Analyze the user's objective and create a practical plan.

Focus on:
1. Objective
2. Requirements
3. Architecture
4. Steps
5. Risks
6. Validation

Do not modify files.
""",

    "CODING": """
You are BANKAI CODER.

Help the user implement software.

Provide:
- correct code
- explanation
- file structure when useful
- implementation steps
- testing considerations

Do not claim that code was executed unless it actually was.
""",

    "TESTING": """
You are BANKAI TEST ENGINEER.

Focus on:
- identifying failures
- test strategy
- debugging
- pytest
- validation
- regression prevention

Do not claim a test passed unless it actually ran.
""",

    "REVIEW": """
You are BANKAI REVIEWER.

Review the user's code or architecture.

Look for:
- correctness
- bugs
- maintainability
- security
- performance
- architecture problems

Give actionable fixes.
""",

    "KNOWLEDGE": """
You are BANKAI KNOWLEDGE ASSISTANT.

Answer using the supplied source context when available.

Clearly distinguish:
- information from sources
- general knowledge
- uncertainty

Never invent information from a source.
""",
}


# =============================================================================
# MAIN BANKAI FUNCTION
# =============================================================================

def bankai_chat(
    message: str,
    conversation: list[dict[str, Any]] | None = None,
    force_intent: str | None = None,
) -> dict[str, Any]:

    if not message or not message.strip():
        return {
            "text": "BANKAI is ready. What would you like to do?",
            "intent": "CHAT",
            "provider": "none",
            "model": "none",
        }

    intent = (
        force_intent.upper()
        if force_intent
        else detect_intent(message)
    )

    route = MODEL_ROUTING.get(
        intent,
        MODEL_ROUTING["CHAT"],
    )

    provider = route["provider"]
    model = route["model"]

    system_prompt = PROMPTS.get(
        intent,
        PROMPTS["CHAT"],
    )

    # -------------------------------------------------------------------------
    # Ollama
    # -------------------------------------------------------------------------

    if provider == "ollama":

        if ollama_available():

            try:
                answer = ollama_chat(
                    message=message,
                    model=model,
                    system_prompt=system_prompt,
                )

                return {
                    "text": answer,
                    "intent": intent,
                    "provider": "ollama",
                    "model": model,
                    "status": "success",
                }

            except Exception as exc:

                return {
                    "text": (
                        "BANKAI detected the request as "
                        f"**{intent}**, but the local model failed.\n\n"
                        f"Error: `{exc}`"
                    ),
                    "intent": intent,
                    "provider": "ollama",
                    "model": model,
                    "status": "error",
                    "error": str(exc),
                }

        return {
            "text": (
                "BANKAI detected this as "
                f"**{intent}**.\n\n"
                "The configured Ollama server is not currently "
                "reachable at `127.0.0.1:11434`.\n\n"
                f"Configured model: `{model}`"
            ),
            "intent": intent,
            "provider": "ollama",
            "model": model,
            "status": "offline",
        }

    return {
        "text": "No model provider is configured.",
        "intent": intent,
        "provider": provider,
        "model": model,
        "status": "unconfigured",
    }


# =============================================================================
# ROUTING INFORMATION
# =============================================================================

def get_route_info(intent: str | None = None) -> dict[str, Any]:

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

    return {
        "ollama": ollama_available(),
        "routes": MODEL_ROUTING,
    }
