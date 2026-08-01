import random
from pathlib import Path
import pandas as pd

random.seed(42)

out = Path("task/environment/data")
out.mkdir(parents=True, exist_ok=True)

airports = ["DEL","BOM","MAA","BLR","HYD","CCU"]

fleet = []
for i in range(1,41):
    fleet.append({
        "aircraft_id":f"AC{i:03}",
        "home_airport":random.choice(airports),
        "aircraft_type":random.choice(["A320","B737","ATR72"]),
        "age_years":random.randint(1,18)
    })

pd.DataFrame(fleet).to_csv(out/"aircraft.csv",index=False)

flights=[]
fid=1

for a in fleet:
    for _ in range(random.randint(8,15)):
        dep=random.choice(airports)
        arr=random.choice([x for x in airports if x!=dep])

        delay=max(0,int(random.gauss(18,14)))

        fuel=random.randint(2200,6200)

        status=random.choices(
            ["COMPLETED","DELAYED","CANCELLED"],
            weights=[75,20,5]
        )[0]

        flights.append({
            "flight_id":f"FL{fid:04}",
            "aircraft_id":a["aircraft_id"],
            "departure":dep,
            "arrival":arr,
            "delay_minutes":delay,
            "fuel_used":fuel,
            "status":status
        })

        fid+=1

pd.DataFrame(flights).to_csv(out/"flight_logs.csv",index=False)

maint=[]

for a in fleet:
    maint.append({
        "aircraft_id":a["aircraft_id"],
        "days_since_service":random.randint(1,120),
        "maintenance_events":random.randint(0,8)
    })

pd.DataFrame(maint).to_csv(out/"maintenance.csv",index=False)

aps=[]

for ap in airports:
    aps.append({
        "airport":ap,
        "traffic_index":random.randint(1,10)
    })

pd.DataFrame(aps).to_csv(out/"airports.csv",index=False)

with open(out/"no_fly_aircraft.txt","w") as f:
    f.write("AC005\n")
    f.write("AC017\n")
    f.write("AC033\n")

print("Dataset generated.")