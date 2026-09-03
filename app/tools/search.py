from pathlib import Path


class CodeSearch:

    EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".md",
        ".yaml",
        ".yml",
        ".toml",
        ".txt",
    }

    def __init__(
        self,
        project_root: Path
    ):

        self.project_root = Path(
            project_root
        ).resolve()

    def search(
        self,
        query: str,
        max_results: int = 50
    ):

        results = []

        for path in self.project_root.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in self.EXTENSIONS:
                continue

            if "__pycache__" in path.parts:
                continue

            if ".git" in path.parts:
                continue

            try:

                text = path.read_text(
                    encoding="utf-8"
                )

            except (
                UnicodeDecodeError,
                PermissionError
            ):

                continue

            for line_number, line in enumerate(
                text.splitlines(),
                start=1
            ):

                if query.lower() in line.lower():

                    results.append({
                        "file": str(
                            path.relative_to(
                                self.project_root
                            )
                        ),
                        "line": line_number,
                        "text": line.strip(),
                    })

                    if len(results) >= max_results:

                        return results

        return results
