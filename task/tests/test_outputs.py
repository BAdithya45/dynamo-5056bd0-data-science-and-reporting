import json
from pathlib import Path


def load():
    return json.loads(Path("/app/output.json").read_text())


def test_output_exists():
    assert Path("/app/output.json").exists()


def test_schema():

    d = load()

    assert "summary" in d
    assert "sensors" in d

    s = d["summary"]

    expected = {
        "total_sensors",
        "excellent",
        "good",
        "warning",
        "critical",
        "average_reliability_index",
    }

    assert expected == set(s.keys())


def test_sensor_schema():

    d = load()

    for sensor in d["sensors"].values():

        assert set(sensor.keys()) == {
            "production_line",
            "average_drift",
            "maintenance_score",
            "reliability_index",
            "health",
        }


def test_health_values():

    d = load()

    allowed = {
        "EXCELLENT",
        "GOOD",
        "WARNING",
        "CRITICAL",
    }

    for sensor in d["sensors"].values():

        assert sensor["health"] in allowed


def test_ranges():

    d = load()

    for sensor in d["sensors"].values():

        assert sensor["average_drift"] >= 0

        assert 0 <= sensor["maintenance_score"] <= 100

        assert sensor["reliability_index"] < 120

        assert sensor["reliability_index"] > -100


def test_summary_counts():

    d = load()

    s = d["summary"]

    total = (
        s["excellent"]
        + s["good"]
        + s["warning"]
        + s["critical"]
    )

    assert total == s["total_sensors"]