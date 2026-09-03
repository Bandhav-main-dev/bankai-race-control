from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


class ContextHandoffManager:

    def __init__(
        self,
        project_root: str | Path,
        threshold_percent: int = 85,
        max_messages_before_compaction: int = 40,
    ):

        self.project_root = Path(project_root)

        self.session_dir = (
            self.project_root
            / "data"
            / "sessions"
        )

        self.session_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.threshold_percent = threshold_percent
        self.max_messages = max_messages_before_compaction

    # -------------------------------------------------------------------------
    # Approximate token count
    # -------------------------------------------------------------------------

    @staticmethod
    def estimate_tokens(messages):

        text = "\n".join(
            message.get("content", "")
            for message in messages
        )

        # Conservative rough estimate.
        return max(
            1,
            len(text) // 4,
        )

    # -------------------------------------------------------------------------
    # Handoff decision
    # -------------------------------------------------------------------------

    def should_handoff(
        self,
        messages,
        context_limit: int = 32768,
    ):

        tokens = self.estimate_tokens(messages)

        percentage = (
            tokens / context_limit
        ) * 100

        return {
            "handoff": (
                percentage >= self.threshold_percent
                or len(messages) >= self.max_messages
            ),
            "estimated_tokens": tokens,
            "context_limit": context_limit,
            "usage_percent": round(
                percentage,
                2,
            ),
        }

    # -------------------------------------------------------------------------
    # Build compact context
    # -------------------------------------------------------------------------

    def build_handoff(
        self,
        messages,
        previous_provider: str,
        previous_model: str,
    ):

        recent = messages[-12:]

        summary_lines = [
            "BANKAI CONTEXT HANDOFF",
            f"Previous provider: {previous_provider}",
            f"Previous model: {previous_model}",
            "",
            "Conversation state:",
        ]

        for message in recent:

            role = message.get(
                "role",
                "unknown",
            )

            content = message.get(
                "content",
                "",
            )

            if len(content) > 1000:
                content = content[:1000] + "..."

            summary_lines.append(
                f"{role.upper()}: {content}"
            )

        summary_lines.extend([
            "",
            "Instruction:",
            "Continue the conversation using the preserved "
            "context above. Do not restart the task.",
        ])

        return "\n".join(summary_lines)

    # -------------------------------------------------------------------------
    # Persist handoff
    # -------------------------------------------------------------------------

    def save_handoff(
        self,
        session_id: str,
        messages,
        previous_provider: str,
        previous_model: str,
    ):

        handoff = {
            "session_id": session_id,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "previous_provider": previous_provider,
            "previous_model": previous_model,
            "messages": messages[-12:],
            "handoff_context": self.build_handoff(
                messages,
                previous_provider,
                previous_model,
            ),
        }

        path = (
            self.session_dir
            / f"{session_id}_handoff.json"
        )

        path.write_text(
            json.dumps(
                handoff,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path
