# Airport Fleet Safety Reporting Benchmark

This benchmark evaluates an AI agent's ability to analyze commercial aircraft operations and generate a structured fleet safety report.

## Input Files

The benchmark provides:

- flight_logs.csv
- aircraft.csv
- maintenance.csv
- airports.csv
- no_fly_aircraft.txt

## Required Workflow

The agent must:

1. Remove restricted aircraft.
2. Ignore cancelled flights.
3. Join all datasets.
4. Compute operational statistics.
5. Calculate maintenance scores.
6. Compute safety scores.
7. Assign fleet status labels.
8. Produce `/app/output.json`.

## Verification

The verifier validates the output JSON schema together with the computed fleet statistics and safety metrics.