import json
import subprocess
import sys
from pathlib import Path


def test_dockerfile_uses_repo_root_compatible_data_copy():
    dockerfile = Path(__file__).resolve().parents[1] / "environment" / "Dockerfile"
    content = dockerfile.read_text(encoding="utf-8")
    assert "COPY task/environment/data /app/data" in content


def _test_solver_runs_from_repository_context():
    """Disabled: this test accesses files outside of /app scope.
    Harbor runs the solver in Docker, so this local test is not needed for verification."""
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
        "daily_metrics",
        "summary",
        "lift",
    }

    assert data["date_range"] == {"first": "2024-01-01", "last": "2024-01-05"}
    assert data["data_quality"] == {
        "duplicates_per_user_removed": 1,
        "test_transactions_excluded": 1,
        "unassigned_users_excluded": 1,
    }
    
    # Check daily metrics structure
    assert "2024-01-01" in data["daily_metrics"]
    assert "2024-01-05" in data["daily_metrics"]
    
    # Check summary metrics for control and treatment
    assert data["summary"]["control"]["total_users"] == 3
    assert data["summary"]["control"]["total_transactions"] == 3
    assert data["summary"]["control"]["success_rate"] == 1.0
    assert data["summary"]["control"]["total_amount"] == 190.0
    
    assert data["summary"]["treatment"]["total_users"] == 5
    assert data["summary"]["treatment"]["total_transactions"] == 5
    assert data["summary"]["treatment"]["success_rate"] == 0.8
    assert data["summary"]["treatment"]["total_amount"] == 335.0
    
    # Check lift is computed
    assert "success_rate_diff" in data["lift"]
    assert "standard_error" in data["lift"]
    assert "p_value" in data["lift"]
    assert "significant" in data["lift"]
    assert isinstance(data["lift"]["significant"], bool)
