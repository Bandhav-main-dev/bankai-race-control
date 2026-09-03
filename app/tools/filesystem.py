from pathlib import Path

from app.tools.security import SecurityPolicy
from app.utils.logger import log


class FileSystemTools:

    def __init__(
        self,
        project_root: Path
    ):

        self.project_root = Path(
            project_root
        ).resolve()

        self.security = SecurityPolicy(
            self.project_root
        )

    def list_files(
        self,
        relative_path="."
    ):

        directory = self.security.validate_path(
            relative_path
        )

        if not directory.exists():

            raise FileNotFoundError(
                directory
            )

        results = []

        for path in sorted(
            directory.rglob("*")
        ):

            if not path.is_file():
                continue

            if "__pycache__" in path.parts:
                continue

            if ".git" in path.parts:
                continue

            results.append(
                str(
                    path.relative_to(
                        self.project_root
                    )
                )
            )

        return results

    def read_file(
        self,
        relative_path
    ):

        path = self.security.validate_path(
            relative_path
        )

        if not path.exists():

            raise FileNotFoundError(
                relative_path
            )

        if not path.is_file():

            raise IsADirectoryError(
                relative_path
            )

        log(
            f"READ {relative_path}"
        )

        return path.read_text(
            encoding="utf-8"
        )

    def write_file(
        self,
        relative_path,
        content
    ):

        path = self.security.validate_path(
            relative_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

        log(
            f"WRITE {relative_path}"
        )

        return {
            "path": relative_path,
            "bytes": len(
                content.encode("utf-8")
            )
        }

    def append_file(
        self,
        relative_path,
        content
    ):

        path = self.security.validate_path(
            relative_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with path.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(content)

        log(
            f"APPEND {relative_path}"
        )
