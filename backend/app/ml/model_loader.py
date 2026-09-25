"""Loads the serialised Random Forest model from disk."""

import logging
from pathlib import Path
from typing import Any, Optional

import joblib

from app.core.config import settings

logger = logging.getLogger(__name__)

_cached_model: Optional[Any] = None


def load_model() -> Optional[Any]:
    """Load (and cache) the Random Forest model from settings.MODEL_PATH.

    Uses joblib (matches how the model is saved in train.py).
    Returns None if no model file exists so the app degrades gracefully.
    """
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    model_path = Path(settings.MODEL_PATH)
    if not model_path.exists():
        logger.warning(
            "Model file not found at %s. Diagnosis will use placeholder logic.",
            model_path,
        )
        return None

    _cached_model = joblib.load(model_path)
    logger.info("Model loaded from %s", model_path)
    return _cached_model
