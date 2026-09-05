
"""
===============================================================================
⚔️ SOUL FORGE MEMORY ENGINE V1
===============================================================================

Persistent memory and conversation storage for SOUL FORGE.

Memory layers:

GLOBAL
PROJECT
RULES
DECISIONS
SUMMARIES
CONVERSATIONS

No credentials are stored here.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MEMORY_DIR = PROJECT_ROOT / "data" / "memory"
CHAT_DIR = PROJECT_ROOT / "data" / "conversations"

GLOBAL_MEMORY_FILE = MEMORY_DIR / "global_memory.json"
PROJECT_MEMORY_FILE = MEMORY_DIR / "project_memory.json"
RULES_FILE = MEMORY_DIR / "rules.json"
DECISIONS_FILE = MEMORY_DIR / "decisions.json"
SUMMARY_FILE = MEMORY_DIR / "summaries.json"
CHAT_INDEX_FILE = CHAT_DIR / "index.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ensure() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    CHAT_DIR.mkdir(parents=True, exist_ok=True)

    defaults = {
        GLOBAL_MEMORY_FILE: [],
        PROJECT_MEMORY_FILE: {},
        RULES_FILE: [],
        DECISIONS_FILE: [],
        SUMMARY_FILE: [],
        CHAT_INDEX_FILE: [],
    }

    for path, default in defaults.items():
        if not path.exists():
            path.write_text(
                json.dumps(default, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )


def _load(path: Path, default: Any) -> Any:
    _ensure()

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(path: Path, value: Any) -> None:
    _ensure()

    tmp = path.with_suffix(path.suffix + ".tmp")

    tmp.write_text(
        json.dumps(value, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    tmp.replace(path)


def new_id(prefix: str = "sf") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


# =============================================================================
# MEMORY
# =============================================================================

def add_memory(
    content: str,
    *,
    memory_type: str = "fact",
    importance: int = 5,
    scope: str = "global",
    project: str = "",
    source: str = "conversation",
) -> dict:

    content = content.strip()

    if not content:
        return {}

    importance = max(1, min(10, int(importance)))

    item = {
        "memory_id": new_id("mem"),
        "content": content,
        "memory_type": memory_type,
        "importance": importance,
        "scope": scope,
        "project": project,
        "source": source,
        "created_at": _now(),
        "updated_at": _now(),
        "active": True,
    }

    if scope == "project":
        data = _load(PROJECT_MEMORY_FILE, {})

        data.setdefault(project or "unknown", [])

        data[project or "unknown"].append(item)

        _save(PROJECT_MEMORY_FILE, data)

    elif memory_type == "rule":
        data = _load(RULES_FILE, [])
        data.append(item)
        _save(RULES_FILE, data)

    elif memory_type == "decision":
        data = _load(DECISIONS_FILE, [])
        data.append(item)
        _save(DECISIONS_FILE, data)

    else:
        data = _load(GLOBAL_MEMORY_FILE, [])
        data.append(item)
        _save(GLOBAL_MEMORY_FILE, data)

    return item


def get_all_memories(project: str = "") -> list[dict]:

    result = []

    global_memories = _load(GLOBAL_MEMORY_FILE, [])

    for item in global_memories:
        if item.get("active", True):
            result.append(item)

    rules = _load(RULES_FILE, [])

    for item in rules:
        if item.get("active", True):
            result.append(item)

    decisions = _load(DECISIONS_FILE, [])

    for item in decisions:
        if item.get("active", True):
            result.append(item)

    project_data = _load(PROJECT_MEMORY_FILE, {})

    if project:
        for item in project_data.get(project, []):
            if item.get("active", True):
                result.append(item)

    return result


def search_memory(
    query: str,
    project: str = "",
    limit: int = 12,
) -> list[dict]:

    query = query.lower().strip()

    if not query:
        return []

    tokens = {
        token
        for token in re.findall(r"[a-zA-Z0-9_'-]+", query)
        if len(token) > 2
    }

    scored = []

    for item in get_all_memories(project):

        text = str(item.get("content", "")).lower()

        score = 0

        for token in tokens:
            if token in text:
                score += 1

        score += int(item.get("importance", 5)) * 0.25

        if item.get("memory_type") == "rule":
            score += 3

        if item.get("memory_type") == "decision":
            score += 2

        if score > 0:
            scored.append((score, item))

    scored.sort(
        key=lambda x: (
            x[0],
            x[1].get("importance", 5),
        ),
        reverse=True,
    )

    return [item for _, item in scored[:limit]]


def memory_context(
    query: str,
    project: str = "",
    limit: int = 12,
) -> str:

    memories = search_memory(
        query=query,
        project=project,
        limit=limit,
    )

    if not memories:
        return ""

    lines = [
        "SOUL FORGE LONG-TERM MEMORY:",
        "",
    ]

    for item in memories:

        importance = item.get("importance", 5)
        memory_type = item.get("memory_type", "fact")
        content = item.get("content", "")

        lines.append(
            f"[{memory_type.upper()} | importance={importance}/10] "
            f"{content}"
        )

    return "\n".join(lines)


# =============================================================================
# MEMORY EXTRACTION
# =============================================================================

IMPORTANT_PATTERNS = [
    (
        r"\bremember\b",
        "fact",
        9,
    ),
    (
        r"\bdon't forget\b",
        "rule",
        10,
    ),
    (
        r"\bdo not forget\b",
        "rule",
        10,
    ),
    (
        r"\balways\b",
        "rule",
        9,
    ),
    (
        r"\bnever\b",
        "rule",
        10,
    ),
    (
        r"\bimportant\b",
        "fact",
        9,
    ),
    (
        r"\bmust\b",
        "rule",
        9,
    ),
    (
        r"\bwe decided\b",
        "decision",
        8,
    ),
    (
        r"\bdecision\b",
        "decision",
        8,
    ),
    (
        r"\bpreference\b",
        "preference",
        7,
    ),
]


def extract_candidate_memories(
    message: str,
) -> list[dict]:

    message = message.strip()

    if not message:
        return []

    candidates = []

    lowered = message.lower()

    for pattern, memory_type, importance in IMPORTANT_PATTERNS:

        if re.search(pattern, lowered):

            content = message

            if len(content) > 500:
                content = content[:500] + "..."

            candidates.append(
                {
                    "content": content,
                    "memory_type": memory_type,
                    "importance": importance,
                }
            )

            break

    return candidates


def remember_from_message(
    message: str,
    project: str = "",
) -> list[dict]:

    saved = []

    for candidate in extract_candidate_memories(message):

        item = add_memory(
            candidate["content"],
            memory_type=candidate["memory_type"],
            importance=candidate["importance"],
            scope="project" if project else "global",
            project=project,
            source="automatic_extraction",
        )

        if item:
            saved.append(item)

    return saved


# =============================================================================
# CONFLICT DETECTION
# =============================================================================

def detect_conflicts(
    new_content: str,
    project: str = "",
) -> list[dict]:

    new_lower = new_content.lower()

    conflicts = []

    memories = get_all_memories(project)

    negative_pairs = [
        ("never", "always"),
        ("do not", "do"),
        ("don't", "do"),
        ("avoid", "use"),
        ("disable", "enable"),
    ]

    for item in memories:

        old = item.get("content", "").lower()

        common_words = set(
            re.findall(r"[a-zA-Z]{4,}", old)
        ) & set(
            re.findall(r"[a-zA-Z]{4,}", new_lower)
        )

        if len(common_words) < 2:
            continue

        for left, right in negative_pairs:

            if (
                (left in old and right in new_lower)
                or
                (right in old and left in new_lower)
            ):
                conflicts.append(item)
                break

    return conflicts


# =============================================================================
# CONVERSATIONS
# =============================================================================

def create_conversation(
    title: str = "New Chat",
    project: str = "",
) -> dict:

    conversation_id = new_id("chat")

    conversation = {
        "conversation_id": conversation_id,
        "title": title,
        "project": project,
        "created_at": _now(),
        "updated_at": _now(),
        "summary": "",
        "messages": [],
    }

    path = CHAT_DIR / f"{conversation_id}.json"

    _save(path, conversation)

    index = _load(CHAT_INDEX_FILE, [])

    index.insert(
        0,
        {
            "conversation_id": conversation_id,
            "title": title,
            "project": project,
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
        },
    )

    _save(CHAT_INDEX_FILE, index)

    return conversation


def load_conversation(
    conversation_id: str,
) -> dict | None:

    path = CHAT_DIR / f"{conversation_id}.json"

    if not path.exists():
        return None

    return _load(path, None)


def save_message(
    conversation_id: str,
    role: str,
    content: str,
) -> dict | None:

    conversation = load_conversation(conversation_id)

    if not conversation:
        return None

    message = {
        "message_id": new_id("msg"),
        "role": role,
        "content": content,
        "timestamp": _now(),
    }

    conversation.setdefault("messages", []).append(message)

    conversation["updated_at"] = _now()

    _save(
        CHAT_DIR / f"{conversation_id}.json",
        conversation,
    )

    update_conversation_index(
        conversation_id,
        conversation.get("title", "New Chat"),
        conversation.get("project", ""),
        conversation["updated_at"],
    )

    return message


def update_conversation_index(
    conversation_id: str,
    title: str,
    project: str,
    updated_at: str,
) -> None:

    index = _load(CHAT_INDEX_FILE, [])

    found = False

    for item in index:

        if item.get("conversation_id") == conversation_id:

            item["title"] = title
            item["project"] = project
            item["updated_at"] = updated_at

            found = True
            break

    if not found:

        index.insert(
            0,
            {
                "conversation_id": conversation_id,
                "title": title,
                "project": project,
                "updated_at": updated_at,
            },
        )

    index.sort(
        key=lambda x: x.get("updated_at", ""),
        reverse=True,
    )

    _save(CHAT_INDEX_FILE, index)


def list_conversations(
    limit: int = 50,
) -> list[dict]:

    return _load(
        CHAT_INDEX_FILE,
        [],
    )[:limit]


def rename_conversation(
    conversation_id: str,
    title: str,
) -> bool:

    conversation = load_conversation(conversation_id)

    if not conversation:
        return False

    conversation["title"] = title.strip() or "New Chat"
    conversation["updated_at"] = _now()

    _save(
        CHAT_DIR / f"{conversation_id}.json",
        conversation,
    )

    update_conversation_index(
        conversation_id,
        conversation["title"],
        conversation.get("project", ""),
        conversation["updated_at"],
    )

    return True


def delete_conversation(
    conversation_id: str,
) -> bool:

    path = CHAT_DIR / f"{conversation_id}.json"

    if path.exists():
        path.unlink()

    index = _load(CHAT_INDEX_FILE, [])

    index = [
        item
        for item in index
        if item.get("conversation_id") != conversation_id
    ]

    _save(CHAT_INDEX_FILE, index)

    return True


# =============================================================================
# SUMMARY
# =============================================================================

def update_summary(
    conversation_id: str,
    summary: str,
) -> bool:

    conversation = load_conversation(conversation_id)

    if not conversation:
        return False

    conversation["summary"] = summary
    conversation["updated_at"] = _now()

    _save(
        CHAT_DIR / f"{conversation_id}.json",
        conversation,
    )

    summaries = _load(SUMMARY_FILE, [])

    found = False

    for item in summaries:

        if item.get("conversation_id") == conversation_id:

            item["summary"] = summary
            item["updated_at"] = _now()

            found = True
            break

    if not found:

        summaries.append(
            {
                "conversation_id": conversation_id,
                "summary": summary,
                "updated_at": _now(),
            }
        )

    _save(SUMMARY_FILE, summaries)

    return True


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_ai_memory_context(
    user_message: str,
    project: str = "",
) -> str:

    context = memory_context(
        query=user_message,
        project=project,
        limit=12,
    )

    if not context:
        return ""

    return (
        "\n\n"
        "===== SOUL FORGE MEMORY =====\n"
        f"{context}\n"
        "===== END SOUL FORGE MEMORY =====\n"
    )
