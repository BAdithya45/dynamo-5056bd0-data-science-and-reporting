import json
import subprocess
import sys
from pathlib import Path


def test_dockerfile_uses_repo_root_compatible_data_copy():
    dockerfile = Path(__file__).resolve().parents[1] / "environment" / "Dockerfile"
    content = dockerfile.read_text(encoding="utf-8")
    assert "COPY task/environment/data /app/data" in content


def test_solver_runs_from_repository_context():
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(repo_root / "task" / "solution" / "solve.py")],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0
    assert Path("/app/output.json").exists()


def test_output_exists():
    """The agent must write /app/output.json."""
    assert Path("/app/output.json").exists()


def test_output_schema_and_metrics():
    """The output JSON must contain the expected cleaning counts and reporting metrics."""
    data = json.loads(Path("/app/output.json").read_text(encoding="utf-8"))

    assert set(data.keys()) == {
        "date_range",
        "data_quality",
        "daily_revenue",
        "control",
        "treatment",
        "absolute_lift",
        "standard_error",
        "p_value",
        "significant_at_0.05",
    }

    assert data["date_range"] == {"start": "2024-01-01", "end": "2024-01-05"}
    assert data["data_quality"] == {
        "duplicate_events_dropped": 1,
        "bot_sessions_removed": 1,
        "unassigned_sessions_dropped": 2,
    }
    assert data["daily_revenue"] == {
        "2024-01-01": {"control": 60.0, "treatment": 0.0},
        "2024-01-02": {"control": 25.0, "treatment": 0.0},
        "2024-01-03": {"control": 0.0, "treatment": 95.0},
        "2024-01-04": {"control": 0.0, "treatment": 60.0},
        "2024-01-05": {"control": 0.0, "treatment": 15.0},
    }
    assert data["control"] == {
        "users": 3,
        "sessions": 6,
        "total_revenue": 85.0,
        "revenue_per_session": 14.1666666667,
    }
    assert data["treatment"] == {
        "users": 4,
        "sessions": 6,
        "total_revenue": 170.0,
        "revenue_per_session": 28.3333333333,
    }
    assert data["absolute_lift"] == 13.3333333333
    assert data["standard_error"] == 4.0397332145
    assert data["p_value"] == 0.0009649621
    assert data["significant_at_0.05"] is True
