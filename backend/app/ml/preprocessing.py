"""Telemetry preprocessing for ML inference and training."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# Value used when an optional field is absent
_MISSING_VALUE = -1.0


def telemetry_to_feature_vector(telemetry_dict: Dict[str, Any]) -> np.ndarray:
    """Convert a telemetry dictionary to a numeric feature vector.

    Missing values are replaced with `_MISSING_VALUE` so that the model
    can distinguish "not reported" from a real zero measurement.
    """
    vector: List[float] = []
    for feature in settings.ML_FEATURES:
        value = telemetry_dict.get(feature)
        if value is None:
            vector.append(_MISSING_VALUE)
        elif isinstance(value, bool):
            vector.append(float(value))
        else:
            vector.append(float(value))
    return np.array(vector, dtype=np.float32)
