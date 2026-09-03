from __future__ import annotations

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from .multi_ai_provider import (
    MultiAIProviderEngine,
    ProviderError,
)

from .context_handoff import (
    ContextHandoffManager,
)


class BankaiMultiAIChat:

    def __init__(
        self,
        project_root: str | Path,
    ):

        self.project_root = Path(
            project_root
        )

        self.provider_engine = (
            MultiAIProviderEngine()
        )

        self.handoff = (
            ContextHandoffManager(
                self.project_root
            )
        )

        self.session_id = uuid.uuid4().hex

        self.messages = []

        self.current_provider = "ollama"
        self.current_model = None

        self.session_file = (
            self.project_root
            / "data"
            / "sessions"
            / f"{self.session_id}.json"
        )

    # -------------------------------------------------------------------------
    # Add message
    # -------------------------------------------------------------------------

    def add_message(
        self,
        role: str,
        content: str,
    ):

        self.messages.append({
            "role": role,
            "content": content,
        })

    # -------------------------------------------------------------------------
    # Choose model
    # -------------------------------------------------------------------------

    def select_model(
        self,
        provider: str | None = None,
        model: str | None = None,
    ):

        if provider and model:

            self.current_provider = provider
            self.current_model = model

            return provider, model

        # Local-first default.
        if not self.current_model:

            self.current_provider = "ollama"

            self.current_model = (
                "qwen3:latest"
            )

        return (
            self.current_provider,
            self.current_model,
        )

    # -------------------------------------------------------------------------
    # Handoff
    # -------------------------------------------------------------------------

    def perform_handoff(self):

        state = self.handoff.should_handoff(
            self.messages
        )

        if not state["handoff"]:
            return False

        path = self.handoff.save_handoff(
            self.session_id,
            self.messages,
            self.current_provider,
            self.current_model,
        )

        # Preserve recent context while preventing
        # unlimited context growth.
        recent = self.messages[-10:]

        handoff_message = {
            "role": "system",
            "content": self.handoff.build_handoff(
                self.messages,
                self.current_provider,
                self.current_model,
            ),
        }

        self.messages = [
            handoff_message,
            *recent,
        ]

        print(
            f"[BANKAI HANDOFF] {path}"
        )

        return True

    # -------------------------------------------------------------------------
    # Ask
    # -------------------------------------------------------------------------

    def ask(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ):

        self.add_message(
            "user",
            prompt,
        )

        provider, model = self.select_model(
            provider,
            model,
        )

        try:

            result = (
                self.provider_engine.complete(
                    provider,
                    model,
                    self.messages,
                )
            )

        except ProviderError as exc:

            self.messages.pop()

            raise RuntimeError(
                f"{provider}/{model}: {exc}"
            ) from exc

        self.add_message(
            "assistant",
            result["content"],
        )

        self.perform_handoff()

        self.save()

        return result

    # -------------------------------------------------------------------------
    # Save session
    # -------------------------------------------------------------------------

    def save(self):

        data = {
            "session_id": self.session_id,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "current_provider": self.current_provider,
            "current_model": self.current_model,
            "messages": self.messages,
        }

        self.session_file.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return self.session_file
