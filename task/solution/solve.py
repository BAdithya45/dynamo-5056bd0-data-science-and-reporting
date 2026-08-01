#!/usr/bin/env python3
"""
Customer Churn Prediction Task Solution
Trains a logistic regression classifier to predict customer churn
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score


def resolve_data_dir() -> Path:
    """Resolve data directory for both container and local testing."""
    candidates = [
        Path(__file__).resolve().parents[1] / "environment" / "data",
        Path(__file__).resolve().parents[2] / "task" / "environment" / "data",
        Path("/app/data"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find data directory in any of: {candidates}")


def main():
    data_dir = resolve_data_dir()
    
    # Load data files
    customers = pd.read_csv(data_dir / 'customers.csv')
    usage = pd.read_csv(data_dir / 'usage.csv')
    churn = pd.read_csv(data_dir / 'churn.csv')
    
    # Load test customers exclusion list
    test_customers_file = data_dir / 'test_customers.txt'
    test_customers = set()
    if test_customers_file.exists():
        with open(test_customers_file) as f:
            test_customers = set(line.strip() for line in f if line.strip())
    
    # Tracking metrics
    total_initial = len(customers)
    excluded_test = 0
    excluded_young = 0
    
    # Filter 1: Remove test customers
    customers_filtered = customers[~customers['customer_id'].isin(test_customers)]
    excluded_test = total_initial - len(customers_filtered)
    
    # Filter 2: Keep only customers with account_age_months >= 3
    customers_filtered = customers_filtered[customers_filtered['account_age_months'] >= 3]
    excluded_young = (total_initial - excluded_test) - len(customers_filtered)
    
    # Aggregate usage data by customer
    usage_agg = usage.groupby('customer_id').agg({
        'login_days': 'mean',
        'features_used': 'mean',
        'support_tickets': 'sum'
    }).reset_index()
    usage_agg.columns = ['customer_id', 'avg_login_days', 'avg_features_used', 'total_support_tickets']
    
    # Merge datasets
    merged = customers_filtered.merge(usage_agg, on='customer_id', how='inner')
    merged = merged.merge(churn, on='customer_id', how='inner')
    
    final_size = len(merged)
    
    # Feature engineering
    merged['support_intensity'] = merged['total_support_tickets'] / merged['account_age_months']
    merged['login_features_interaction'] = merged['avg_login_days'] * merged['avg_features_used']
    
    # Encode categorical variables (one-hot)
    merged = pd.get_dummies(merged, columns=['subscription_tier', 'region'], drop_first=True)
    
    # Prepare features and target
    # Select feature columns: the engineered and original features we care about
    feature_cols = [
        'avg_login_days',
        'avg_features_used', 
        'total_support_tickets',
        'account_age_months',
        'support_intensity',
        'login_features_interaction'
    ]
    
    X = merged[feature_cols]
    y = merged['churned']
    
    # Train/test split (80/20, seed=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train logistic regression
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    # Predictions and evaluation
    y_train_pred = model.predict(X_train_scaled)
    y_test_pred = model.predict(X_test_scaled)
    y_test_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred, zero_division=0)
    test_recall = recall_score(y_test, y_test_pred, zero_division=0)
    test_auc = roc_auc_score(y_test, y_test_pred_proba)
    
    # Feature importance: absolute values of coefficients, normalized
    coef_abs = np.abs(model.coef_[0])
    feature_importance = coef_abs / coef_abs.sum()
    
    feature_importance_dict = {
        col: float(imp) for col, imp in zip(feature_cols, feature_importance)
    }
    
    # Churn rate
    churn_rate = (y.sum() / len(y)) * 100.0
    
    # Build output
    output = {
        "dataset": {
            "total_customers_initial": int(total_initial),
            "excluded_test_users": int(excluded_test),
            "excluded_young_accounts": int(excluded_young),
            "final_dataset_size": int(final_size),
            "churn_rate_percent": float(churn_rate)
        },
        "model": {
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test))
        },
        "performance": {
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "test_precision": float(test_precision),
            "test_recall": float(test_recall),
            "test_auc_roc": float(test_auc)
        },
        "feature_importance": feature_importance_dict
    }
    
    # Write output
    output_path = Path('/app/output.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"Output written to {output_path}")


if __name__ == '__main__':
    main()
