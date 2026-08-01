# Payment A/B test reconciliation benchmark

This repository contains a Harbor-style A/B testing task in which an agent must reconcile payment transaction logs, apply experiment logic, and measure the treatment effect on transaction success rates.

## What the agent must do

The agent receives three input files in /app/data:
- transactions.csv for raw transaction logs (timestamp, user_id, transaction_id, success, amount)
- assignments.csv for A/B test cohort assignments (control/treatment)
- test_ids.txt for test-mode transactions to exclude

The required workflow is fixed: deduplicate by keeping the first transaction per user, filter test and unassigned users, normalize timestamps to UTC, and compute success-rate metrics and lift statistics.

## What the reference solution provides

The reference oracle lives in task/solution/solve.py and task/solution/solve.sh. It produces the expected JSON artifact and writes it to /app/output.json.

## How verification works

The verifier in task/tests/test_outputs.py checks the generated artifact for schema and expected summary metrics, including per-variant success rates and lift statistics. The shared environment in task/environment/Dockerfile installs Python and pytest so the verifier can run inside the same container image.
