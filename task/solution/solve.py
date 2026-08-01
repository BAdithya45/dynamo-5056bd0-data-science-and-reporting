#!/usr/bin/env python3

import json
from pathlib import Path

import pandas as pd


def data_dir():
    for p in [
        Path(__file__).resolve().parents[1] / "environment" / "data",
        Path("/app/data"),
    ]:
        if p.exists():
            return p

    raise FileNotFoundError("data directory not found")


def main():
    d = data_dir()

    flights = pd.read_csv(d / "flight_logs.csv")
    aircraft = pd.read_csv(d / "aircraft.csv")
    maint = pd.read_csv(d / "maintenance.csv")
    airports = pd.read_csv(d / "airports.csv")

    banned = set()

    with open(d / "no_fly_aircraft.txt") as f:
        for x in f:
            x = x.strip()
            if x:
                banned.add(x)

    flights = flights[~flights.aircraft_id.isin(banned)]

    flights = flights[flights.status != "CANCELLED"]

    df = flights.merge(aircraft, on="aircraft_id")
    df = df.merge(maint, on="aircraft_id")
    df = df.merge(airports, left_on="departure", right_on="airport")

    g = (
        df.groupby("aircraft_id")
        .agg(
            home_airport=("home_airport", "first"),
            completed_flights=("status", lambda x: (x == "COMPLETED").sum()),
            delayed_flights=("status", lambda x: (x == "DELAYED").sum()),
            average_delay_minutes=("delay_minutes", "mean"),
            average_fuel_used=("fuel_used", "mean"),
            days_since_service=("days_since_service", "first"),
        )
        .reset_index()
    )

    out = {}

    ready = monitor = service = ground = 0
    total = 0.0

    for _, r in g.iterrows():

        maintenance_score = max(
            0.0,
            100.0 - r.days_since_service
        )

        utilization_score = (
            r.completed_flights * 3
            - r.delayed_flights * 2
        )

        safety_score = (
            100
            - r.average_delay_minutes * 0.40
            - r.average_fuel_used * 0.002
            + maintenance_score * 0.20
            + utilization_score * 0.30
        )

        if safety_score >= 95:
            status = "READY"
            ready += 1
        elif safety_score >= 90:
            status = "MONITOR"
            monitor += 1
        elif safety_score >= 80:
            status = "SERVICE"
            service += 1
        else:
            status = "GROUND"
            ground += 1

        total += safety_score

        out[r.aircraft_id] = {
            "home_airport": r.home_airport,
            "completed_flights": int(r.completed_flights),
            "delayed_flights": int(r.delayed_flights),
            "average_delay_minutes": round(float(r.average_delay_minutes), 6),
            "average_fuel_used": round(float(r.average_fuel_used), 6),
            "maintenance_score": round(float(maintenance_score), 6),
            "safety_score": round(float(safety_score), 6),
            "status": status,
        }

    result = {
        "fleet_summary": {
            "total_aircraft": len(out),
            "ready": ready,
            "monitor": monitor,
            "service": service,
            "ground": ground,
            "average_safety_score": round(total / len(out), 6),
        },
        "aircraft": out,
    }

    Path("/app/output.json").write_text(
        json.dumps(result, indent=2)
    )


if __name__ == "__main__":
    main()