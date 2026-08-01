You are analyzing manufacturing quality metrics from factory production lines. You have three CSV files: production records, defect reports, and equipment specifications. Your job is to: (1) clean and validate quality data, (2) compute defect rates and quality scores, (3) identify problematic equipment, (4) generate quality control summary, and (5) forecast trend direction.

Files in /app/data:
- production.csv: batch_id, equipment_id, shift (morning/afternoon/night), units_produced, timestamp (ISO 8601 UTC)
- defects.csv: batch_id, defect_count, defect_type (material/alignment/wear), severity (1-5)
- equipment.csv: equipment_id, installation_date (YYYY-MM-DD), model (TypeA/TypeB/TypeC), maintenance_days_ago
- excluded_batches.txt: test batch IDs to exclude from analysis

Data cleaning (in order):
1. Remove batches listed in excluded_batches.txt (test runs).
2. Filter out batches with units_produced < 10 (incomplete runs).
3. Remove equipment with maintenance_days_ago < 0 (invalid maintenance dates).
4. Merge production and defects on batch_id; keep rows with valid defect data.
5. Group by equipment_id and compute: avg_defect_rate (defects/units), avg_severity, total_defects.

Metric computation:
- defect_rate_percent = (total_defects / total_units_produced) * 100
- quality_score = 100 - defect_rate_percent (capped at 100)
- severity_score = avg_severity (normalized 0-1, divided by 5)
- equipment_health_index = quality_score * 0.7 + (100 - severity_score * 100) * 0.3

Trend analysis: For each equipment, compute defect trend (ascending/descending/stable) using linear regression on defect_rate over batches (R-squared threshold > 0.3 for trend confidence).

Produce a JSON report at /app/output.json with this schema:
{
  "summary": {
    "total_batches_processed": 0,
    "excluded_test_batches": 0,
    "excluded_incomplete_batches": 0,
    "equipment_count": 0,
    "overall_defect_rate_percent": 0.0,
    "overall_quality_score": 0.0
  },
  "equipment_performance": {
    "equipment_id": {
      "total_units": 0,
      "total_defects": 0,
      "defect_rate_percent": 0.0,
      "quality_score": 0.0,
      "avg_severity": 0.0,
      "health_index": 0.0,
      "trend": "ascending|descending|stable",
      "trend_confidence": 0.0
    }
  },
  "alerts": {
    "critical_equipment": [],
    "deteriorating_equipment": []
  }
}

Critical equipment: quality_score < 85 or avg_severity > 3.5. Deteriorating: trend = "ascending" and trend_confidence > 0.5.

Report all metrics with at least 6 significant digits. You have 300 seconds to complete this task.
