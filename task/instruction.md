You are running an A/B test on a payment-processing pipeline. You have been given three data files that contain payment transaction records, experiment assignments, and a list of test-mode transactions to exclude. Your job is to reconcile the raw transaction log, apply experiment logic, and compute the treatment effect on transaction success rates.

Files in /app/data:
- transactions.csv: raw transaction log (timestamp, user_id, transaction_id, success, amount)
- assignments.csv: experiment cohort assignments (user_id, variant)
- test_ids.txt: list of test user IDs to exclude from analysis

Clean the dataset as follows (in order):
1. For each user_id, keep only the first transaction in chronological order (by timestamp); discard later duplicates.
2. Remove all transactions from user IDs listed in test_ids.txt.
3. Remove all transactions from user IDs that do not appear in assignments.csv.
4. Normalize all timestamps to UTC and group by calendar date (YYYY-MM-DD).

For each variant (control/treatment), compute:
- total_users: distinct user_id count
- total_transactions: count of transactions
- success_count: count of transactions where success=true
- success_rate: success_count / total_transactions
- total_amount: sum of transaction amounts (for successful transactions only)

Produce a JSON report at /app/output.json with this schema:
{
  "date_range": {"first": "YYYY-MM-DD", "last": "YYYY-MM-DD"},
  "data_quality": {
    "duplicates_per_user_removed": 0,
    "test_transactions_excluded": 0,
    "unassigned_users_excluded": 0
  },
  "daily_metrics": {
    "YYYY-MM-DD": {
      "control": {"transactions": 0, "successes": 0, "success_rate": 0.0},
      "treatment": {"transactions": 0, "successes": 0, "success_rate": 0.0}
    }
  },
  "summary": {
    "control": {"total_users": 0, "total_transactions": 0, "success_rate": 0.0, "total_amount": 0.0},
    "treatment": {"total_users": 0, "total_transactions": 0, "success_rate": 0.0, "total_amount": 0.0}
  },
  "lift": {
    "success_rate_diff": 0.0,
    "standard_error": 0.0,
    "p_value": 0.0,
    "significant": false
  }
}

For lift statistics, use per-user success rates: for each user, compute their success rate across their transactions, then compute the mean and variance of per-user success rates within each variant. The standard error is sqrt(var_control / n_users_control + var_treatment / n_users_treatment). Compute a two-sided p-value using normal approximation. Report all floating-point values with at least 6 significant digits.

You have 300 seconds to complete this task. Do not cheat by looking up solutions online.
