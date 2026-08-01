You have customer data and need to predict churn. You are given three CSV files containing customer attributes, monthly usage metrics, and churn labels. Your task is to: (1) clean and validate the data, (2) engineer features for a predictive model, (3) train a logistic regression classifier, (4) evaluate model performance, and (5) compute feature importance.

Files in /app/data:
- customers.csv: customer_id, account_age_months, subscription_tier (basic/premium/enterprise), region (US/EU/APAC)
- usage.csv: customer_id, month, login_days, features_used, support_tickets, payment_method (card/ach/paypal)
- churn.csv: customer_id, churned (0/1)

Data cleaning (in order):
1. Remove customers with account_age_months < 3 (excluded from churn analysis).
2. Remove customers in the exclusion list (test_customers.txt).
3. For each customer, aggregate usage.csv to compute: avg_login_days, avg_features_used, total_support_tickets over all months.
4. Merge the three datasets; drop rows with missing values.

Feature engineering:
- Create interaction: (login_days) × (features_used)
- Create: support_intensity = support_tickets / account_age_months
- Encode categorical: subscription_tier and region as binary (one-hot)

Train logistic regression on 80% of data (random split, seed=42). Evaluate on 20% test set.

Produce a JSON report at /app/output.json with this schema:
{
  "dataset": {
    "total_customers_initial": 0,
    "excluded_test_users": 0,
    "excluded_young_accounts": 0,
    "final_dataset_size": 0,
    "churn_rate_percent": 0.0
  },
  "model": {
    "train_size": 0,
    "test_size": 0
  },
  "performance": {
    "train_accuracy": 0.0,
    "test_accuracy": 0.0,
    "test_precision": 0.0,
    "test_recall": 0.0,
    "test_auc_roc": 0.0
  },
  "feature_importance": {
    "avg_login_days": 0.0,
    "avg_features_used": 0.0,
    "total_support_tickets": 0.0,
    "account_age_months": 0.0,
    "support_intensity": 0.0,
    "login_features_interaction": 0.0
  }
}

Use sklearn.linear_model.LogisticRegression with default parameters. Feature importance = absolute values of coefficients, normalized to sum to 1.0. Report all metrics with at least 6 significant digits.

You have 300 seconds to complete this task. Do not cheat by looking up solutions online.
