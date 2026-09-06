"""Input validation helpers."""

from typing import Any, Dict, List


def validate_feature_completeness(telemetry_dict: Dict[str, Any], required_features: List[str]) -> List[str]:
    """Return a list of feature names that are missing or None."""
    return [f for f in required_features if telemetry_dict.get(f) is None]
