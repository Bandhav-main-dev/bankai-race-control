from pathlib import Path
import json
from datetime import datetime

from app.agents.coding_agent import BankaiAgent
from app.agents.planner import AgentPlanner
from app.core.mission_controller import MissionController
from app.utils.logger import log


class RaceControl:

    def __init__(self, project_root: Path):

        self.project_root = Path(project_root)

        self.agent = BankaiAgent(
            self.project_root
        )

        self.planner = AgentPlanner(
            self.project_root
        )

        self.missions = MissionController(
            self.project_root
        )

    def dispatch(
        self,
        objective: str
    ):

        log("=" * 70)
        log("BANKAI RACE CONTROL — MISSION DISPATCH")
        log("=" * 70)

        mission = self.missions.create_mission(
            objective
        )

        log(
            "Generating AI engineering plan..."
        )

        ai_result = self.planner.create_plan(
            objective
        )

        mission["phase"] = "AI_PLAN"

        mission["ai_plan"] = (
            ai_result["ai_plan"]
        )

        mission["project_files"] = (
            ai_result["project_files"]
        )

        mission["updated_at"] = (
            datetime.now().isoformat()
        )

        self.missions.update(
            **mission
        )

        log(
            "AI planning completed."
        )

        return mission
