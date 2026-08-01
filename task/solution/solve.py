#!/usr/bin/env python3

import json
from pathlib import Path

import pandas as pd


def data_dir():
    candidates = [
        Path(__file__).resolve().parents[1] / "environment" / "data",
        Path.cwd() / "task" / "environment" / "data",
        Path("/app/data"),
    ]

    for p in candidates:
        if (p / "robot_events.csv").exists():
            return p

    raise FileNotFoundError("Could not locate robot_events.csv")

def main():
    d = data_dir()

    events = pd.read_csv(d / "robot_events.csv")
    battery = pd.read_csv(d / "battery_history.csv")
    queue = pd.read_csv(d / "mission_queue.csv")

    excluded = set()

    with open(d / "blacklisted_robots.txt") as f:
        for line in f:
            line = line.strip()
            if line:
                excluded.add(line)

    events = events[~events.robot_id.isin(excluded)]
    battery = battery[~battery.robot_id.isin(excluded)]
    queue = queue[~queue.robot_id.isin(excluded)]

    keep = []

    for rid, g in events.groupby("robot_id"):
        g = g.sort_values("timestamp")

        failed = False

        for _, row in g.iterrows():

            if failed:
                continue

            keep.append(row)

            if row["event_type"] == "HARD_FAILURE":
                failed = True

    events = pd.DataFrame(keep)

    df = (
        events.merge(battery, on="robot_id")
        .merge(queue, on="robot_id")
    )

    robots = {}

    low = medium = high = critical = 0
    total_score = 0

    for rid, g in df.groupby("robot_id"):

        completed = (g.event_type == "COMPLETE").sum()
        failed = (g.event_type == "FAIL").sum()

        distance = g.distance_meters.sum()

        avg_battery = g.battery_percent.mean()

        battery_drop = (
            g.battery_percent.max()
            - g.battery_percent.min()
        )

        assigned = int(g.assigned_missions.iloc[0])

        total_events = len(g)

        efficiency = distance / max(1, total_events)

        risk = (
            battery_drop * 0.35
            + failed * 8
            + g.last_service_days.iloc[0] * 0.25
            - efficiency * 0.15
        )

        if risk < 20:
            status = "LOW"
            low += 1
        elif risk < 40:
            status = "MEDIUM"
            medium += 1
        elif risk < 60:
            status = "HIGH"
            high += 1
        else:
            status = "CRITICAL"
            critical += 1

        total_score += risk

        robots[rid] = {
            "assigned_missions": assigned,
            "missions_completed": int(completed),
            "missions_failed": int(failed),
            "battery_drop": round(float(battery_drop), 6),
            "efficiency_score": round(float(efficiency), 6),
            "risk_score": round(float(risk), 6),
            "status": status,
        }

    result = {
        "summary": {
            "robots": len(robots),
            "low": low,
            "medium": medium,
            "high": high,
            "critical": critical,
            "average_risk_score": round(
                total_score / len(robots), 6
            ),
        },
        "robots": robots,
    }

    Path("/app/output.json").write_text(
        json.dumps(result, indent=2)
    )


if __name__ == "__main__":
    main()