You are an aviation operations analyst responsible for evaluating the operational safety of a commercial aircraft fleet.

The directory /app/data contains:

- flight_logs.csv
- aircraft.csv
- maintenance.csv
- airports.csv
- no_fly_aircraft.txt

Generate a fleet safety report.

Perform the following steps in EXACTLY this order.

1. Remove every aircraft listed in no_fly_aircraft.txt.

2. Ignore every flight whose status is CANCELLED.

3. Join flight_logs.csv with aircraft.csv using aircraft_id.

4. Join the result with maintenance.csv using aircraft_id.

5. Join the result with airports.csv using departure = airport.

6. For every aircraft compute:

completed_flights

delayed_flights

average_delay_minutes

average_fuel_used

7. Compute

utilization_score =
completed_flights × 3
− delayed_flights × 2

8. Compute

maintenance_score =
max(0,100−days_since_service)

9. Compute

safety_score =
100
− average_delay_minutes × 0.40
− average_fuel_used × 0.002
+ maintenance_score × 0.20
+ utilization_score × 0.30

Round only final reported values to six decimal places.

10. Assign

READY
if safety_score ≥ 95

MONITOR
if 90 ≤ safety_score < 95

SERVICE
if 80 ≤ safety_score < 90

GROUND
otherwise

11. Produce

/app/output.json

using EXACTLY this schema

{
  "fleet_summary":{
    "total_aircraft":0,
    "ready":0,
    "monitor":0,
    "service":0,
    "ground":0,
    "average_safety_score":0.0
  },

  "aircraft":{
    "AC001":{
      "home_airport":"",
      "completed_flights":0,
      "delayed_flights":0,
      "average_delay_minutes":0.0,
      "average_fuel_used":0.0,
      "maintenance_score":0.0,
      "safety_score":0.0,
      "status":""
    }
  }
}

Only output the JSON artifact.