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
    assignments_path = data_dir / "assignments.csv"
    events_path = data_dir / "events.csv"
    bots_path = data_dir / "bots.txt"
    output_path = Path("/app/output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with assignments_path.open(encoding="utf-8") as handle:
        assignments = {row["user_id"]: row["variant"] for row in csv.DictReader(handle)}

    with events_path.open(encoding="utf-8") as handle:
        events = list(csv.DictReader(handle))

    bots = {line.strip() for line in bots_path.read_text(encoding="utf-8").splitlines() if line.strip()}

    deduped: dict[str, dict[str, str]] = {}
    for event in events:
        sid = event["session_id"]
        ts = parse_ts(event["session_ts"])
        existing = deduped.get(sid)
        if existing is None:
            deduped[sid] = event
        else:
            existing_ts = parse_ts(existing["session_ts"])
            if ts < existing_ts:
                deduped[sid] = event

    retained = []
    duplicate_events_dropped = len(events) - len(deduped)
    bot_sessions_removed = 0
    unassigned_sessions_dropped = 0

    for event in deduped.values():
        user_id = event["user_id"]
        if user_id in bots:
            bot_sessions_removed += 1
            continue
        if user_id not in assignments:
            unassigned_sessions_dropped += 1
            continue
        retained.append(event)

    daily_revenue: dict[str, dict[str, float]] = defaultdict(lambda: {"control": 0.0, "treatment": 0.0})
    per_variant_users: dict[str, set[str]] = {"control": set(), "treatment": set()}
    per_variant_sessions: dict[str, int] = {"control": 0, "treatment": 0}
    per_variant_total_revenue: dict[str, float] = {"control": 0.0, "treatment": 0.0}

    for event in retained:
        user_id = event["user_id"]
        variant = assignments[user_id]
        ts = parse_ts(event["session_ts"])
        day = ts.strftime("%Y-%m-%d")
        revenue = float(event["revenue"])
        daily_revenue[day][variant] += revenue
        per_variant_users[variant].add(user_id)
        per_variant_sessions[variant] += 1
        per_variant_total_revenue[variant] += revenue

    sorted_days = []
    if retained:
        retained_dates = sorted({parse_ts(event["session_ts"]).strftime("%Y-%m-%d") for event in retained})
        if retained_dates:
            start_day = retained_dates[0]
            end_day = retained_dates[-1]
            current = datetime.strptime(start_day, "%Y-%m-%d")
            end = datetime.strptime(end_day, "%Y-%m-%d")
            while current <= end:
                day = current.strftime("%Y-%m-%d")
                daily_revenue.setdefault(day, {"control": 0.0, "treatment": 0.0})
                sorted_days.append(day)
                current = current.fromordinal(current.toordinal() + 1)
        else:
            start_day = end_day = ""
    else:
        start_day = end_day = ""

    control_means = []
    treatment_means = []
    for user_id in sorted(assignments):
        user_events = [evt for evt in retained if evt["user_id"] == user_id]
        if not user_events:
            continue
        revenue_mean = sum(float(evt["revenue"]) for evt in user_events) / len(user_events)
        if assignments[user_id] == "control":
            control_means.append(revenue_mean)
        else:
            treatment_means.append(revenue_mean)

    control_mean = sum(control_means) / len(control_means) if control_means else 0.0
    treatment_mean = sum(treatment_means) / len(treatment_means) if treatment_means else 0.0
    diff = treatment_mean - control_mean

    if len(control_means) > 1 and len(treatment_means) > 1:
        var_control = sum((x - control_mean) ** 2 for x in control_means) / (len(control_means) - 1)
        var_treatment = sum((x - treatment_mean) ** 2 for x in treatment_means) / (len(treatment_means) - 1)
        se = math.sqrt(var_control / len(control_means) + var_treatment / len(treatment_means))
    else:
        se = 0.0

    z_score = diff / se if se > 0 else 0.0
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(z_score) / math.sqrt(2)))) if se > 0 else 0.0

    payload = {
        "date_range": {"start": start_day, "end": end_day},
        "data_quality": {
            "duplicate_events_dropped": duplicate_events_dropped,
            "bot_sessions_removed": bot_sessions_removed,
            "unassigned_sessions_dropped": unassigned_sessions_dropped,
        },
        "daily_revenue": {
            day: {
                "control": round(daily_revenue[day].get("control", 0.0), 10),
                "treatment": round(daily_revenue[day].get("treatment", 0.0), 10),
            }
            for day in sorted_days
        },
        "control": {
            "users": len(per_variant_users["control"]),
            "sessions": per_variant_sessions["control"],
            "total_revenue": round(per_variant_total_revenue["control"], 10),
            "revenue_per_session": round(per_variant_total_revenue["control"] / per_variant_sessions["control"], 10) if per_variant_sessions["control"] else 0.0,
        },
        "treatment": {
            "users": len(per_variant_users["treatment"]),
            "sessions": per_variant_sessions["treatment"],
            "total_revenue": round(per_variant_total_revenue["treatment"], 10),
            "revenue_per_session": round(per_variant_total_revenue["treatment"] / per_variant_sessions["treatment"], 10) if per_variant_sessions["treatment"] else 0.0,
        },
        "absolute_lift": round(diff, 10),
        "standard_error": round(se, 10),
        "p_value": round(p_value, 10),
        "significant_at_0.05": bool(p_value < 0.05),
    }

    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
