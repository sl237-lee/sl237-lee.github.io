import os
import joblib
import pandas as pd
import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report


def main():
    df = pd.read_parquet("data/training_dataset.parquet")

    features = [
        "api_calls",
        "errors",
        "error_rate",
        "latency_ms_p50_avg",
        "amount_succeeded",
        "payment_failures",
        "tickets",
        "severity_points",
        "api_calls_7d",
        "api_calls_30d",
        "payment_failures_30d",
        "tickets_30d",
        "severity_points_30d",
    ]

    X = df[features]
    y = df["churn_30d"].astype(int)

    # Handle imbalance for XGBoost
    pos = int(y.sum())
    neg = int((1 - y).sum())
    scale_pos_weight = (neg / max(pos, 1))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        min_child_weight=1,
        objective="binary:logistic",
        eval_metric="aucpr",
        scale_pos_weight=scale_pos_weight,
        n_jobs=8,
        tree_method="hist",
    )

    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, proba)
    pr_auc = average_precision_score(y_test, proba)

    print(f"Rows: {len(df):,} | Positives: {pos:,} | Churn rate: {y.mean():.4%}")
    print(f"scale_pos_weight: {scale_pos_weight:.2f}")
    print(f"ROC AUC:  {auc:.4f}")
    print(f"PR  AUC:  {pr_auc:.4f}")

    # Quick threshold report (not optimized)
    preds = (proba >= 0.5).astype(int)
    print("\nClassification report @0.50 threshold:")
    print(classification_report(y_test, preds, digits=4))

    os.makedirs("models", exist_ok=True)
    joblib.dump({"model": model, "features": features}, "models/churn_xgb.joblib")
    print("\nSaved model to models/churn_xgb.joblib")


if __name__ == "__main__":
    main()
