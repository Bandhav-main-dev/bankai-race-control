from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "logs" / "bankai.log"


def log(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] {message}"

    print(line)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line + "\n")
