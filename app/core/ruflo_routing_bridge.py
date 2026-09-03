from __future__ import annotations

import subprocess
import shutil


class RufloRoutingBridge:

    def __init__(self, command: str = "ruflo"):

        self.command = command

    def available(self):

        return shutil.which(
            self.command
        ) is not None

    def route_task(self, task: str):

        if not self.available():

            return {
                "success": False,
                "provider": None,
                "model": None,
                "reason": "Ruflo executable unavailable",
            }

        try:

            result = subprocess.run(
                [
                    self.command,
                    "route",
                    "--task",
                    task,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            ).strip()

            return {
                "success": result.returncode == 0,
                "provider": None,
                "model": None,
                "raw_output": output,
            }

        except Exception as exc:

            return {
                "success": False,
                "provider": None,
                "model": None,
                "reason": str(exc),
            }
