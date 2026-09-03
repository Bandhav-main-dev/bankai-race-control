from pathlib import Path

from app.tools.filesystem import FileSystemTools
from app.tools.terminal import TerminalTools
from app.tools.search import CodeSearch
from app.utils.logger import log


class CodingAgent:

    name = "BANKAI-CODER"

    def __init__(
        self,
        project_root: Path
    ):

        self.project_root = Path(
            project_root
        ).resolve()

        self.files = FileSystemTools(
            self.project_root
        )

        self.terminal = TerminalTools(
            self.project_root
        )

        self.search = CodeSearch(
            self.project_root
        )

        log(
            "BANKAI-CODER initialized"
        )

    def inspect_project(self):

        log(
            "CODING AGENT: project inspection"
        )

        files = self.files.list_files()

        return {
            "file_count": len(files),
            "files": files
        }

    def read(
        self,
        path
    ):

        return self.files.read_file(
            path
        )

    def write(
        self,
        path,
        content
    ):

        return self.files.write_file(
            path,
            content
        )

    def append(
        self,
        path,
        content
    ):

        return self.files.append_file(
            path,
            content
        )

    def search_code(
        self,
        query
    ):

        return self.search.search(
            query
        )

    def execute(
        self,
        command,
        timeout=120
    ):

        return self.terminal.run(
            command,
            timeout
        )

    def python(
        self,
        code,
        timeout=120
    ):

        return self.terminal.python(
            code,
            timeout
        )

    def test(
        self
    ):

        return self.terminal.pytest()

    def lint(
        self
    ):

        return self.terminal.ruff()

    def git_status(
        self
    ):

        return self.terminal.git_status()
