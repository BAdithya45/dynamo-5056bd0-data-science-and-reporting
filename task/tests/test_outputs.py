import json
import sys
from pathlib import Path


def test_dockerfile_uses_repo_root_compatible_data_copy():
    dockerfile = Path(__file__).resolve().parents[1] / "environment" / "Dockerfile"
    content = dockerfile.read_text(encoding="utf-8")
    assert "COPY task/environment/data /app/data" in content


def test_output_exists():
    """The agent must write /app/output.json."""
    assert Path("/app/output.json").exists()


def test_output_schema_and_metrics():
    """The output JSON must contain churn prediction model results."""
    data = json.loads(Path("/app/output.json").read_text(encoding="utf-8"))

    # Validate top-level keys for churn prediction task
    assert set(data.keys()) == {
        "dataset",
        "model",
        "performance",
        "feature_importance",
    }

    # Validate dataset section
    assert data["dataset"]["total_customers_initial"] > 0
    assert data["dataset"]["excluded_test_users"] >= 0
    assert data["dataset"]["excluded_young_accounts"] >= 0
    assert data["dataset"]["final_dataset_size"] > 0
    assert 0 <= data["dataset"]["churn_rate_percent"] <= 100

    # Validate model section
    assert data["model"]["train_size"] > 0
    assert data["model"]["test_size"] > 0

    # Validate performance metrics are in valid ranges [0, 1]
    assert 0 <= data["performance"]["train_accuracy"] <= 1
    assert 0 <= data["performance"]["test_accuracy"] <= 1
    assert 0 <= data["performance"]["test_precision"] <= 1
    assert 0 <= data["performance"]["test_recall"] <= 1
    assert 0 <= data["performance"]["test_auc_roc"] <= 1

    # Validate feature importance keys
    expected_features = {
        "avg_login_days",
        "avg_features_used",
        "total_support_tickets",
        "account_age_months",
        "support_intensity",
        "login_features_interaction",
    }
    assert set(data["feature_importance"].keys()) == expected_features

    # Validate feature importance values sum to 1.0 (within tolerance)
    importance_sum = sum(data["feature_importance"].values())
    assert 0.99 <= importance_sum <= 1.01

    # Validate all feature importance values are non-negative
    for feat_name, importance in data["feature_importance"].items():
        assert importance >= 0, f"Feature {feat_name} has negative importance: {importance}"
