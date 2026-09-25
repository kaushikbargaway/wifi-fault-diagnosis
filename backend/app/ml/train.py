"""
TwinNet — Random Forest Training Pipeline
==========================================
Trains a Random Forest fault-diagnosis classifier and saves the model.

Run from the project root (with venv activated):
    python -m app.ml.train --dataset ml/data/simulated/network_fault_dataset.csv

Output:
    backend/models/random_forest.pkl
    ml/reports/training_report.txt
"""

import argparse
import logging
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import joblib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Features the model uses — must match config.py ML_FEATURES
FEATURE_COLS = [
    "rssi_dbm",
    "latency_ms",
    "packet_loss_percent",
    "internet_reachable",
    "dns_available",
    "ethernet_connected",
    "temperature_c",
    "network_load",
]

LABEL_COL = "fault_label"

# Ordered fault labels — must match config.py FAULT_LABELS
FAULT_LABELS = [
    "normal",
    "weak_wifi_signal",
    "high_latency",
    "packet_loss",
    "dns_failure",
    "internet_connectivity_failure",
    "ethernet_problem",
    "router_overheating",
    "network_congestion",
]


# ─────────────────────────────────────────────────────────────────────────────
# Data loading & preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def load_and_preprocess(dataset_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load CSV, encode features, return (X, y)."""
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_csv(dataset_path)

    logger.info("Dataset shape: %s", df.shape)
    logger.info("Columns: %s", list(df.columns))

    # Validate required columns
    missing = [c for c in FEATURE_COLS + [LABEL_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    # Check class distribution
    logger.info("Class distribution:\n%s", df[LABEL_COL].value_counts().to_string())

    # Feature matrix
    X = df[FEATURE_COLS].copy()

    # Convert booleans to float (True→1.0, False→0.0)
    for col in ["internet_reachable", "dns_available", "ethernet_connected"]:
        X[col] = X[col].astype(float)

    # Fill any missing values with -1.0 (sentinel for "not reported")
    X = X.fillna(-1.0)

    X_array = X.values.astype(np.float32)

    # Label encoding — fixed order to match FAULT_LABELS
    label_to_idx = {label: idx for idx, label in enumerate(FAULT_LABELS)}
    y = df[LABEL_COL].map(label_to_idx).values

    unknown = df[LABEL_COL][~df[LABEL_COL].isin(label_to_idx)].unique()
    if len(unknown) > 0:
        raise ValueError(f"Unknown labels in dataset: {unknown}")

    return X_array, y


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────

def train(dataset_path: str, output_model_path: str) -> None:
    """Full training pipeline."""

    # 1. Load data
    X, y = load_and_preprocess(dataset_path)

    # 2. Split — stratified to preserve class proportions
    #    70% train / 15% validation / 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    logger.info("Split → train: %d | val: %d | test: %d", len(X_train), len(X_val), len(X_test))

    # 3. Train Random Forest
    logger.info("Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,       # 200 trees
        max_depth=None,         # Grow full trees
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced", # Handle any class imbalance
        random_state=42,
        n_jobs=-1,              # Use all CPU cores
    )
    model.fit(X_train, y_train)
    logger.info("Training complete.")

    # 4. Validation accuracy
    val_preds = model.predict(X_val)
    val_acc = accuracy_score(y_val, val_preds)
    logger.info("Validation accuracy: %.4f (%.1f%%)", val_acc, val_acc * 100)

    # 5. Cross-validation on training set (5-fold)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1_macro", n_jobs=-1)
    logger.info(
        "5-fold CV macro-F1: %.4f ± %.4f",
        cv_scores.mean(), cv_scores.std()
    )

    # 6. Final evaluation on held-out test set
    test_preds = model.predict(X_test)
    test_acc = accuracy_score(y_test, test_preds)

    logger.info("=" * 60)
    logger.info("TEST SET RESULTS")
    logger.info("=" * 60)
    logger.info("Test Accuracy: %.4f (%.1f%%)", test_acc, test_acc * 100)

    report = classification_report(
        y_test,
        test_preds,
        target_names=FAULT_LABELS,
        digits=4,
    )
    logger.info("Classification Report:\n%s", report)

    # 7. Feature importance
    importances = model.feature_importances_
    feat_importance = sorted(
        zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True
    )
    logger.info("Feature Importances:")
    for feat, imp in feat_importance:
        bar = "█" * int(imp * 40)
        logger.info("  %-30s %.4f  %s", feat, imp, bar)

    # 8. Save model
    output_path = Path(output_model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    logger.info("Model saved → %s", output_path)

    # 9. Save training report
    report_dir = Path("ml/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "training_report.txt"

    with open(report_path, "w") as f:
        f.write("TwinNet — Random Forest Training Report\n")
        f.write("=" * 60 + "\n\n")
        f.write("IMPORTANT: Results are from SIMULATED data.\n")
        f.write("Label as 'preliminary simulation results' in reports.\n\n")
        f.write(f"Dataset       : {dataset_path}\n")
        f.write(f"Train samples : {len(X_train)}\n")
        f.write(f"Val samples   : {len(X_val)}\n")
        f.write(f"Test samples  : {len(X_test)}\n\n")
        f.write(f"Val Accuracy  : {val_acc:.4f}\n")
        f.write(f"CV macro-F1   : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}\n")
        f.write(f"Test Accuracy : {test_acc:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report + "\n")
        f.write("Feature Importances:\n")
        for feat, imp in feat_importance:
            f.write(f"  {feat:<30} {imp:.4f}\n")

    logger.info("Training report saved → %s", report_path)
    logger.info("=" * 60)
    logger.info("Training complete! Model ready at: %s", output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train TwinNet fault diagnosis model.")
    parser.add_argument(
        "--dataset",
        default="ml/data/simulated/network_fault_dataset.csv",
        help="Path to training CSV",
    )
    parser.add_argument(
        "--output",
        default="backend/models/random_forest.pkl",
        help="Output model path",
    )
    args = parser.parse_args()
    train(args.dataset, args.output)
