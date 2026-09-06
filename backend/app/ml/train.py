"""Random Forest training script (placeholder).

Run this module directly once a dataset is available:
    python -m app.ml.train
"""

import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


def train(dataset_path: str, output_model_path: str) -> None:
    """Train the Random Forest classifier and serialise it to disk.

    Steps (to be implemented):
    1. Load dataset from `dataset_path`.
    2. Preprocess features.
    3. Apply feature engineering.
    4. Split into train / validation / test sets.
    5. Fit RandomForestClassifier.
    6. Evaluate on test set.
    7. Persist model to `output_model_path`.
    """
    raise NotImplementedError(
        "Training pipeline not yet implemented. Provide a dataset and implement this function."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train the fault diagnosis Random Forest model.")
    parser.add_argument("--dataset", required=True, help="Path to training CSV")
    parser.add_argument("--output", default="models/random_forest.pkl", help="Output model path")
    args = parser.parse_args()
    train(args.dataset, args.output)
