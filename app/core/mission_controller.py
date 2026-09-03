from pathlib import Path
import json
import uuid
from datetime import datetime


class MissionController:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

        self.mission_file = (
            self.project_root
            / "data"
            / "missions"
            / "current_mission.json"
        )

    def create_mission(self, objective: str) -> dict:

        mission = {
            "mission_id": str(uuid.uuid4())[:8],
            "objective": objective,
            "status": "CREATED",
            "phase": "PLAN",
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "iteration": 0
        }

        self.mission_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.mission_file.write_text(
            json.dumps(mission, indent=2),
            encoding="utf-8"
        )

        return mission

    def load_mission(self) -> dict:

        if not self.mission_file.exists():
            return {}

        return json.loads(
            self.mission_file.read_text(
                encoding="utf-8"
            )
        )

    def update(self, **changes):

        mission = self.load_mission()

        mission.update(changes)

        self.mission_file.write_text(
            json.dumps(mission, indent=2),
            encoding="utf-8"
        )

        return mission
