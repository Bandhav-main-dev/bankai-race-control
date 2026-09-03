import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))


def test_local_ai_module_import():
    """
    Verify that the LocalAI module can be imported.

    IMPORTANT:
    Do not instantiate the Qwen model during pytest collection.
    """

    from app.core.local_ai import LocalAIEngine

    assert LocalAIEngine is not None


def test_local_ai_class_exists():

    from app.core.local_ai import LocalAIEngine

    assert isinstance(
        LocalAIEngine,
        type
    )


def test_bankai_config_exists():

    config = (
        PROJECT
        / "config"
        / "bankai_config.json"
    )

    assert config.exists()


def test_local_ai_configuration():

    import json

    config_file = (
        PROJECT
        / "config"
        / "bankai_config.json"
    )

    data = json.loads(
        config_file.read_text(
            encoding="utf-8"
        )
    )

    local_ai = data.get(
        "local_ai",
        {}
    )

    # Configuration is allowed to use either
    # model or model_name depending on previous versions.

    model_name = (
        local_ai.get("model")
        or local_ai.get("model_name")
    )

    assert model_name is not None
    assert len(model_name) > 0
