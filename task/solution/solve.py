#!/usr/bin/env python3

import json
from pathlib import Path

import pandas as pd


def data_dir():
    for p in [
        Path("/app/data"),
        Path(__file__).resolve().parents[1] / "environment" / "data",
    ]:
        if p.exists():
            return p
    raise FileNotFoundError("data directory not found")


def main():
    d = data_dir()

    readings = pd.read_csv(d / "sensor_readings.csv")
    calib = pd.read_csv(d / "calibration_history.csv")
    maint = pd.read_csv(d / "maintenance_records.csv")

    excluded = set()

    with open(d / "excluded_sensors.txt") as f:
        for x in f:
            x = x.strip()
            if x:
                excluded.add(x)

    readings = readings[~readings.sensor_id.isin(excluded)]

    readings = readings[readings.current_value > 0]

    df = readings.merge(calib, on="sensor_id", how="inner")
    df = df.merge(maint, on="sensor_id", how="inner")

    df["drift"] = (df["current_value"] - df["calibrated_value"]).abs()

    g = (
        df.groupby("sensor_id")
        .agg(
            production_line=("production_line", "first"),
            average_drift=("drift", "mean"),
            last_calibration_days=("last_calibration_days", "first"),
            last_maintenance_days=("last_maintenance_days", "first"),
        )
        .reset_index()
    )

    out = {}

    ex = good = warn = crit = 0

    total_index = 0

    for _, r in g.iterrows():

        maintenance_score = max(0.0, 100.0 - r.last_maintenance_days)

        reliability = (
            100
            - r.average_drift * 12
            - r.last_calibration_days * 0.25
            + maintenance_score * 0.10
        )

        if reliability >= 95:
            health = "EXCELLENT"
            ex += 1
        elif reliability >= 90:
            health = "GOOD"
            good += 1
        elif reliability >= 80:
            health = "WARNING"
            warn += 1
        else:
            health = "CRITICAL"
            crit += 1

        total_index += reliability

        out[r.sensor_id] = {
            "production_line": r.production_line,
            "average_drift": round(float(r.average_drift), 6),
            "maintenance_score": round(float(maintenance_score), 6),
            "reliability_index": round(float(reliability), 6),
            "health": health,
        }

    result = {
        "summary": {
            "total_sensors": len(out),
            "excellent": ex,
            "good": good,
            "warning": warn,
            "critical": crit,
            "average_reliability_index": round(total_index / len(out), 6),
        },
        "sensors": out,
    }

    Path("/app/output.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()