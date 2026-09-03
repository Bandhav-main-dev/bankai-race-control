"""
BANKAI RACE CONTROL — Multi-AI Model Rotation

This module manages logical conversation continuity.

IMPORTANT:
A model cannot provide infinite context by itself.

BANKAI therefore:
1. monitors context/token usage
2. saves conversation state
3. creates a compact handoff
4. selects the next available model
5. continues the conversation

This creates effectively unbounded conversation continuity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AIModel:
    provider: str
    model: str
    local: bool = False
    enabled: bool = True


class ModelRotationController:

    def __init__(
        self,
        threshold_percent: int = 85,
    ) -> None:
        self.threshold_percent = threshold_percent

        self.models = [
            AIModel(
                provider="ollama",
                model="qwen3:latest",
                local=True,
            ),
            AIModel(
                provider="anthropic",
                model="claude",
                local=False,
            ),
            AIModel(
                provider="openai",
                model="gpt",
                local=False,
            ),
            AIModel(
                provider="google",
                model="gemini",
                local=False,
            ),
        ]

        self.current_index = 0

    def current_model(self) -> AIModel:
        return self.models[self.current_index]

    def should_handoff(
        self,
        used_tokens: int,
        context_limit: int,
    ) -> bool:

        if context_limit <= 0:
            return False

        percentage = (
            used_tokens / context_limit
        ) * 100

        return percentage >= self.threshold_percent

    def next_model(self) -> AIModel:

        start = self.current_index

        for _ in range(len(self.models)):

            self.current_index = (
                self.current_index + 1
            ) % len(self.models)

            candidate = self.models[
                self.current_index
            ]

            if candidate.enabled:
                return candidate

        self.current_index = start

        return self.current_model()

    def reset(self) -> None:
        self.current_index = 0
