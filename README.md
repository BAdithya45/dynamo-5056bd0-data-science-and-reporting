# Report-cleanup benchmark task

This repository contains a Harbor-style data-science task in which an agent must clean a messy operational export and write a single report to /app/output.json.

## What the agent must do

The agent receives three input files in /app/data:
- assignments.csv for control/treatment mapping
- events.csv for session-level events
- bots.txt for bot-user filtering

The required workflow is fixed: remove duplicate events by keeping the earliest record per session, drop bot sessions, drop unassigned sessions, normalize timestamps to UTC, and compute the requested reporting metrics.

## What the reference solution provides

The reference oracle lives in task/solution/solve.py and task/solution/solve.sh. It produces the expected JSON artifact and writes it to /app/output.json.

## How verification works

The verifier in task/tests/test_outputs.py checks the generated artifact for schema and exact values, including date range, data-quality counters, daily revenue, variant summaries, and lift statistics. The shared environment in task/environment/Dockerfile installs Python and pytest so the verifier can run inside the same container image.
