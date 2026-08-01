import json
from pathlib import Path


def test_output_exists():
    assert Path("/app/output.json").exists()


def test_schema():

    data = json.loads(Path("/app/output.json").read_text())

    assert "fleet_summary" in data
    assert "aircraft" in data

    s = data["fleet_summary"]

    assert "total_aircraft" in s
    assert "ready" in s
    assert "monitor" in s
    assert "service" in s
    assert "ground" in s
    assert "average_safety_score" in s

    assert isinstance(data["aircraft"], dict)

    for a in data["aircraft"].values():

        assert "home_airport" in a
        assert "completed_flights" in a
        assert "delayed_flights" in a
        assert "average_delay_minutes" in a
        assert "average_fuel_used" in a
        assert "maintenance_score" in a
        assert "safety_score" in a
        assert "status" in a

        assert a["status"] in {
            "READY",
            "MONITOR",
            "SERVICE",
            "GROUND",
        }