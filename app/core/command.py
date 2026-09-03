from dataclasses import dataclass, field
from typing import Any


@dataclass
class BankaiCommand:
    raw: str
    intent: str = "unknown"
    arguments: dict[str, Any] = field(default_factory=dict)
