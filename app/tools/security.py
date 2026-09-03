from pathlib import Path
import shlex


class SecurityPolicy:

    BLOCKED_COMMANDS = {
        "rm",
        "rmdir",
        "shutdown",
        "reboot",
        "mkfs",
        "format",
        "del",
        "erase",
    }

    BLOCKED_PATTERNS = [
        "sudo",
        "chmod 777",
        "curl | bash",
        "wget | bash",
        "rm -rf /",
        "mkfs",
    ]

    def __init__(
        self,
        project_root: Path
    ):

        self.project_root = Path(
            project_root
        ).resolve()

    def validate_path(
        self,
        path
    ):

        target = Path(path)

        if not target.is_absolute():

            target = (
                self.project_root
                / target
            )

        target = target.resolve()

        try:

            target.relative_to(
                self.project_root
            )

        except ValueError:

            raise PermissionError(
                "BANKAI SECURITY: "
                "Path outside project root."
            )

        return target

    def validate_command(
        self,
        command: str
    ):

        if not isinstance(
            command,
            str
        ):

            raise TypeError(
                "Command must be a string."
            )

        normalized = (
            command
            .lower()
            .strip()
        )

        for pattern in self.BLOCKED_PATTERNS:

            if pattern in normalized:

                raise PermissionError(
                    "BANKAI SECURITY: "
                    f"Blocked command pattern: {pattern}"
                )

        try:

            tokens = shlex.split(
                command
            )

        except ValueError as exc:

            raise PermissionError(
                "BANKAI SECURITY: "
                f"Invalid command syntax: {exc}"
            )

        if not tokens:

            raise ValueError(
                "Command cannot be empty."
            )

        executable = (
            Path(
                tokens[0]
            ).name.lower()
        )

        if executable in self.BLOCKED_COMMANDS:

            raise PermissionError(
                "BANKAI SECURITY: "
                f"Blocked command: {executable}"
            )

        return True
