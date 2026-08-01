You are an industrial reliability engineer responsible for assessing the health of factory sensors.

The directory /app/data contains four files:

- sensor_readings.csv
- calibration_history.csv
- maintenance_records.csv
- excluded_sensors.txt

Your objective is to generate a complete sensor reliability report.

Perform the following operations in EXACTLY this order.

1. Remove every sensor whose sensor_id appears in excluded_sensors.txt.

2. Ignore any reading whose current_value is less than or equal to zero.

3. Join sensor_readings.csv with calibration_history.csv using sensor_id.

4. Join the result with maintenance_records.csv using sensor_id.

5. Compute:

drift =
abs(current_value - calibrated_value)

6. For every sensor compute

average_drift

using all remaining readings.

7. Compute the maintenance freshness score

maintenance_score =
max(0, 100 - last_maintenance_days)

8. Compute the reliability index

reliability_index =
100
- (average_drift × 12)
- (last_calibration_days × 0.25)
+ (maintenance_score × 0.10)

Round ONLY the final reported values to six decimal places.

9. Assign a health category

EXCELLENT
reliability_index ≥ 95

GOOD
90 ≤ reliability_index < 95

WARNING
80 ≤ reliability_index < 90

CRITICAL
otherwise

10. Produce

/app/output.json

using EXACTLY the following schema.

{
  "summary": {
    "total_sensors": 0,
    "excellent": 0,
    "good": 0,
    "warning": 0,
    "critical": 0,
    "average_reliability_index": 0.0
  },

  "sensors": {
    "sensor_id": {
      "production_line": "",
      "average_drift": 0.0,
      "maintenance_score": 0.0,
      "reliability_index": 0.0,
      "health": ""
    }
  }
}

Only output the JSON artifact.

You have 300 seconds.