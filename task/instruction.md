You are a warehouse operations analyst responsible for diagnosing autonomous robot failures.

The directory /app/data contains:

- robot_events.csv
- battery_history.csv
- mission_queue.csv
- blacklisted_robots.txt

Generate a robot fleet diagnostic report.

Perform the following operations EXACTLY in order.

1. Remove every robot whose robot_id appears in blacklisted_robots.txt.

2. Ignore every event occurring after the first HARD_FAILURE event for that robot.

3. Join robot_events.csv with battery_history.csv using robot_id.

4. Join the result with mission_queue.csv using robot_id.

5. Compute for every robot:

missions_completed =
number of COMPLETE events

missions_failed =
number of FAIL events

distance_travelled =
sum(distance_meters)

average_battery =
mean(battery_percent)

battery_drop =
max(battery_percent) - min(battery_percent)

queue_completion_rate =
missions_completed /
assigned_missions

6. Compute

efficiency_score =
distance_travelled /
(max(1, total_events))

7. Compute

risk_score =
battery_drop * 0.35
+
missions_failed * 8
+
(last_service_days * 0.25)
-
(efficiency_score * 0.15)

Round ONLY final reported values to six decimals.

8. Health category

LOW
risk_score < 20

MEDIUM
20 <= risk_score < 40

HIGH
40 <= risk_score < 60

CRITICAL
otherwise

9. Produce

/app/output.json

using EXACTLY this schema

{
  "summary":{
      "robots":0,
      "low":0,
      "medium":0,
      "high":0,
      "critical":0,
      "average_risk_score":0.0
  },

  "robots":{
      "RB001":{
          "assigned_missions":0,
          "missions_completed":0,
          "missions_failed":0,
          "battery_drop":0.0,
          "efficiency_score":0.0,
          "risk_score":0.0,
          "status":""
      }
  }
}

Only produce the JSON artifact.