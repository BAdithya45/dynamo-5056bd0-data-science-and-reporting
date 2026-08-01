#!/usr/bin/env python3
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def parse_ts(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def resolve_data_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1] / "environment" / "data",
        Path(__file__).resolve().parents[2] / "task" / "environment" / "data",
        Path.cwd() / "environment" / "data",
        Path.cwd() / "task" / "environment" / "data",
        Path("/app/data"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path("/app/data")


def main() -> None:
    data_dir = resolve_data_dir()
    transactions_path = data_dir / "transactions.csv"
    assignments_path = data_dir / "assignments.csv"
    test_ids_path = data_dir / "test_ids.txt"
    output_path = Path("/app/output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with assignments_path.open(encoding="utf-8") as handle:
        assignments = {row["user_id"]: row["variant"] for row in csv.DictReader(handle)}

    with transactions_path.open(encoding="utf-8") as handle:
        transactions = list(csv.DictReader(handle))

    test_ids = {line.strip() for line in test_ids_path.read_text(encoding="utf-8").splitlines() if line.strip()}

    # Step 1: Keep first transaction per user (by timestamp)
    first_per_user: dict[str, dict[str, str]] = {}
    duplicates_per_user_removed = 0
    for txn in transactions:
        user_id = txn["user_id"]
        ts = parse_ts(txn["timestamp"])
        existing = first_per_user.get(user_id)
        if existing is None:
            first_per_user[user_id] = txn
        else:
            existing_ts = parse_ts(existing["timestamp"])
            if ts < existing_ts:
                duplicates_per_user_removed += 1
                first_per_user[user_id] = txn
            else:
                duplicates_per_user_removed += 1

    # Step 2 & 3: Filter test users and unassigned users
    retained = []
    test_transactions_excluded = 0
    unassigned_users_excluded = 0

    for txn in first_per_user.values():
        user_id = txn["user_id"]
        if user_id in test_ids:
            test_transactions_excluded += 1
            continue
        if user_id not in assignments:
            unassigned_users_excluded += 1
            continue
        retained.append(txn)

    # Step 4: Build daily metrics and summary by variant
    daily_metrics: dict[str, dict[str, dict[str, int | float]]] = defaultdict(
        lambda: {"control": {"transactions": 0, "successes": 0}, "treatment": {"transactions": 0, "successes": 0}}
    )
    
    variant_users: dict[str, set[str]] = {"control": set(), "treatment": set()}
    variant_transactions: dict[str, int] = {"control": 0, "treatment": 0}
    variant_successes: dict[str, int] = {"control": 0, "treatment": 0}
    variant_amounts: dict[str, float] = {"control": 0.0, "treatment": 0.0}

    for txn in retained:
        user_id = txn["user_id"]
        variant = assignments[user_id]
        ts = parse_ts(txn["timestamp"])
        day = ts.strftime("%Y-%m-%d")
        success = txn["success"].lower() == "true"
        amount = float(txn["amount"])

        daily_metrics[day][variant]["transactions"] += 1
        if success:
            daily_metrics[day][variant]["successes"] += 1
        
        variant_users[variant].add(user_id)
        variant_transactions[variant] += 1
        if success:
            variant_successes[variant] += 1
            variant_amounts[variant] += amount

    # Add success_rate to daily_metrics
    for day in sorted(daily_metrics.keys()):
        for variant in ["control", "treatment"]:
            txns = daily_metrics[day][variant]["transactions"]
            succs = daily_metrics[day][variant]["successes"]
            daily_metrics[day][variant]["success_rate"] = round(succs / txns, 10) if txns > 0 else 0.0

    # Compute per-variant summary
    control_success_rate = variant_successes["control"] / variant_transactions["control"] if variant_transactions["control"] > 0 else 0.0
    treatment_success_rate = variant_successes["treatment"] / variant_transactions["treatment"] if variant_transactions["treatment"] > 0 else 0.0
    
    # Compute per-user success rates and statistics
    user_success_rates: dict[str, list[float]] = {"control": [], "treatment": []}
    for user_id in set(list(variant_users["control"]) + list(variant_users["treatment"])):
        user_txns = [t for t in retained if t["user_id"] == user_id]
        if not user_txns:
            continue
        user_success_count = sum(1 for t in user_txns if t["success"].lower() == "true")
        user_rate = user_success_count / len(user_txns)
        variant = assignments[user_id]
        user_success_rates[variant].append(user_rate)

    # Compute lift statistics
    control_mean = sum(user_success_rates["control"]) / len(user_success_rates["control"]) if user_success_rates["control"] else 0.0
    treatment_mean = sum(user_success_rates["treatment"]) / len(user_success_rates["treatment"]) if user_success_rates["treatment"] else 0.0
    diff = treatment_mean - control_mean

    if len(user_success_rates["control"]) > 1 and len(user_success_rates["treatment"]) > 1:
        var_control = sum((x - control_mean) ** 2 for x in user_success_rates["control"]) / (len(user_success_rates["control"]) - 1)
        var_treatment = sum((x - treatment_mean) ** 2 for x in user_success_rates["treatment"]) / (len(user_success_rates["treatment"]) - 1)
        se = math.sqrt(var_control / len(user_success_rates["control"]) + var_treatment / len(user_success_rates["treatment"]))
    else:
        se = 0.0

    z_score = diff / se if se > 0 else 0.0
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(z_score) / math.sqrt(2)))) if se > 0 else 0.0

    # Date range
    sorted_days = sorted(daily_metrics.keys()) if daily_metrics else []
    first_day = sorted_days[0] if sorted_days else ""
    last_day = sorted_days[-1] if sorted_days else ""

    payload = {
        "date_range": {"first": first_day, "last": last_day},
        "data_quality": {
            "duplicates_per_user_removed": duplicates_per_user_removed,
            "test_transactions_excluded": test_transactions_excluded,
            "unassigned_users_excluded": unassigned_users_excluded,
        },
        "daily_metrics": {
            day: {
                "control": {
                    "transactions": daily_metrics[day]["control"]["transactions"],
                    "successes": daily_metrics[day]["control"]["successes"],
                    "success_rate": daily_metrics[day]["control"]["success_rate"],
                },
                "treatment": {
                    "transactions": daily_metrics[day]["treatment"]["transactions"],
                    "successes": daily_metrics[day]["treatment"]["successes"],
                    "success_rate": daily_metrics[day]["treatment"]["success_rate"],
                },
            }
            for day in sorted_days
        },
        "summary": {
            "control": {
                "total_users": len(variant_users["control"]),
                "total_transactions": variant_transactions["control"],
                "success_rate": round(control_success_rate, 10),
                "total_amount": round(variant_amounts["control"], 10),
            },
            "treatment": {
                "total_users": len(variant_users["treatment"]),
                "total_transactions": variant_transactions["treatment"],
                "success_rate": round(treatment_success_rate, 10),
                "total_amount": round(variant_amounts["treatment"], 10),
            },
        },
        "lift": {
            "success_rate_diff": round(diff, 10),
            "standard_error": round(se, 10),
            "p_value": round(p_value, 10),
            "significant": bool(p_value < 0.05),
        },
    }

    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
