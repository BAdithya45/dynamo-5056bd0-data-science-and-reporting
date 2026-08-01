You are given operational event exports in /app/data/assignments.csv, /app/data/events.csv, and /app/data/bots.txt. Produce a single JSON report at /app/output.json with exactly this schema:
{
  "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "data_quality": {
    "duplicate_events_dropped": 0,
    "bot_sessions_removed": 0,
    "unassigned_sessions_dropped": 0
  },
  "daily_revenue": {"YYYY-MM-DD": {"control": 0.0, "treatment": 0.0}, "...": {"...": 0.0, "...": 0.0}},
  "control": {"users": 0, "sessions": 0, "total_revenue": 0.0, "revenue_per_session": 0.0},
  "treatment": {"users": 0, "sessions": 0, "total_revenue": 0.0, "revenue_per_session": 0.0},
  "absolute_lift": 0.0,
  "standard_error": 0.0,
  "p_value": 0.0,
  "significant_at_0.05": false
}

Apply the cleaning in this exact order: first drop duplicate events by keeping the earliest timestamped record for each session_id; then remove any sessions whose user_id appears in bots.txt; then remove any sessions whose user_id does not appear in assignments.csv. Normalize timestamps to UTC and bucket by UTC calendar date. Use the assignment table to classify each retained session as control or treatment. For the report, compute daily revenue by UTC day and variant, where the daily_revenue object covers every UTC date from the earliest to the latest retained session date inclusive, and a variant with no retained sessions on a given day reports 0.0. Compute per-variant users as the number of distinct users with at least one retained session, sessions as the number of retained sessions, total_revenue as the sum of retained session revenue, and revenue_per_session as total_revenue divided by sessions. Compute absolute_lift as treatment revenue_per_session minus control revenue_per_session. Compute the clustered standard error for that lift by first computing one per-user mean revenue-per-session value for each user with at least one retained session, then computing the sample variance of those per-user means within each variant, and using standard_error = sqrt(var_control / n_control + var_treatment / n_treatment). Report the two-sided p-value from a normal approximation using the resulting z-score. Report floats with at least 6 significant digits. Do not modify any input files.

You have 300 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
