"""
BANKAI RACE CONTROL — Ruflo Client

Ruflo is the orchestration/provider layer.

BANKAI remains responsible for:
- commands
- security
- workspace
- coding agents
- monitoring
- conversation state

Ollama remains the local LLM provider.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class RufloClient:
    """Lightweight BANKAI interface to the Ruflo CLI."""

    def __init__(
        self,
        project_root: str | Path,
        ruflo_command: str = "ruflo",
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.ruflo_command = ruflo_command

    def version(self) -> str:
        """Return the installed Ruflo version."""
        result = subprocess.run(
            [self.ruflo_command, "--version"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Ruflo version command failed: {output}"
            )

        return output

    def doctor(self) -> str:
        """Run Ruflo health diagnostics."""
        result = subprocess.run(
            [self.ruflo_command, "doctor"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        output = (
            result.stdout.strip()
            + "\n"
            + result.stderr.strip()
        ).strip()

        if result.returncode != 0:
            raise RuntimeError(output)

        return output

    def status(self) -> dict[str, Any]:
        """Return BANKAI/Ruflo provider state."""
        config_path = (
            self.project_root
            / "config"
            / "ruflo_providers.json"
        )

        if not config_path.exists():
            return {
                "status": "NOT_CONFIGURED",
                "config": None,
            }

        config = json.loads(
            config_path.read_text(
                encoding="utf-8"
            )
        )

        return {
            "status": "READY",
            "config": config,
        }

    def available(self) -> bool:
        """Check whether Ruflo executable exists."""
        try:
            self.version()
            return True
        except Exception:
            return False
