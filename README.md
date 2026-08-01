# Warehouse Robot Fleet Diagnostics Benchmark

This benchmark evaluates an autonomous warehouse robot fleet.

## Input Files

- robot_events.csv
- battery_history.csv
- mission_queue.csv
- blacklisted_robots.txt

## Workflow

The agent must

1. Remove blacklisted robots
2. Ignore events after the first hard failure
3. Merge operational datasets
4. Compute robot efficiency metrics
5. Calculate battery degradation
6. Compute risk scores
7. Categorize robot health
8. Produce `/app/output.json`

## Verification

The verifier checks

- output schema
- robot statistics
- calculated efficiency metrics
- risk scores
- category counts