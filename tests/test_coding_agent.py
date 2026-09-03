import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))


@pytest.fixture
def agent():

    from app.agents.coding_agent import CodingAgent

    return CodingAgent(PROJECT)


def test_coding_agent_import():

    from app.agents.coding_agent import CodingAgent

    assert CodingAgent is not None


def test_coding_agent_instance(agent):

    assert agent is not None


def test_inspect_project(agent):

    result = agent.inspect_project()

    assert isinstance(
        result,
        dict
    )

    assert "files" in result


def test_read(agent):

    content = agent.read(
        "README.md"
    )

    assert isinstance(
        content,
        str
    )

    assert "BANKAI" in content


def test_search_code(agent):

    result = agent.search_code(
        "BANKAI"
    )

    assert isinstance(
        result,
        list
    )


def test_python_execution(agent):

    result = agent.python(
        "print('BANKAI TEST')"
    )

    assert result["success"] is True

    assert "BANKAI TEST" in (
        result["stdout"]
    )


def test_safe_security():

    from app.tools.security import SecurityPolicy

    security = SecurityPolicy(
        PROJECT
    )

    assert security.validate_command(
        "python --version"
    ) is True


def test_dangerous_command_blocked():

    from app.tools.security import SecurityPolicy

    security = SecurityPolicy(
        PROJECT
    )

    with pytest.raises(
        PermissionError
    ):

        security.validate_command(
            "rm -rf /"
        )


def test_outside_path_blocked():

    from app.tools.security import SecurityPolicy

    security = SecurityPolicy(
        PROJECT
    )

    with pytest.raises(
        PermissionError
    ):

        security.validate_path(
            "/tmp/outside-bankai.txt"
        )
