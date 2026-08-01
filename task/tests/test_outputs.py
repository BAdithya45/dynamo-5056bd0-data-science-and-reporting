import json
from pathlib import Path


def load():
    return json.loads(Path("/app/output.json").read_text())


def test_output_exists():
    assert Path("/app/output.json").exists()


def test_schema():
    d = load()

    assert "summary" in d
    assert "robots" in d

    s = d["summary"]

    assert "robots" in s
    assert "low" in s
    assert "medium" in s
    assert "high" in s
    assert "critical" in s
    assert "average_risk_score" in s

    assert isinstance(d["robots"], dict)

    for robot in d["robots"].values():
        assert "assigned_missions" in robot
        assert "missions_completed" in robot
        assert "missions_failed" in robot
        assert "battery_drop" in robot
        assert "efficiency_score" in robot
        assert "risk_score" in robot
        assert "status" in robot

        assert robot["status"] in {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }