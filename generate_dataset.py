import random
from pathlib import Path
import pandas as pd

random.seed(2026)

out = Path("task/environment/data")
out.mkdir(parents=True, exist_ok=True)

airports = [
    ("DEL", "India"),
    ("DXB", "UAE"),
    ("SIN", "Singapore"),
    ("LHR", "UK"),
    ("FRA", "Germany"),
    ("NRT", "Japan"),
]

aircraft = []
for i in range(1, 41):
    aircraft.append({
        "aircraft_id": f"AC{i:03}",
        "home_airport": random.choice(airports)[0],
        "capacity": random.randint(120, 320),
        "age_years": random.randint(1, 25),
    })

pd.DataFrame(aircraft).to_csv(out / "aircraft.csv", index=False)

pd.DataFrame(
    [{"airport": a, "country": c} for a, c in airports]
).to_csv(out / "airports.csv", index=False)

maintenance = []
for a in aircraft:
    maintenance.append({
        "aircraft_id": a["aircraft_id"],
        "days_since_service": random.randint(1, 250),
    })

pd.DataFrame(maintenance).to_csv(out / "maintenance.csv", index=False)

logs = []
statuses = ["COMPLETED", "DELAYED", "COMPLETED", "COMPLETED", "CANCELLED"]

for _ in range(700):
    ac = random.choice(aircraft)["aircraft_id"]
    dep = random.choice(airports)[0]
    arr = random.choice(airports)[0]

    while arr == dep:
        arr = random.choice(airports)[0]

    st = random.choice(statuses)

    logs.append({
        "flight_id": f"FL{random.randint(100000,999999)}",
        "aircraft_id": ac,
        "departure": dep,
        "arrival": arr,
        "status": st,
        "delay_minutes": random.randint(0, 180),
        "fuel_used": random.randint(3000, 18000),
    })

pd.DataFrame(logs).to_csv(out / "flight_logs.csv", index=False)

with open(out / "no_fly_aircraft.txt", "w") as f:
    f.write("AC007\n")
    f.write("AC019\n")

print("dataset regenerated")