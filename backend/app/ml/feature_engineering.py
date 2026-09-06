"""Feature engineering utilities.

Placeholder — add domain-specific derived features here.
Examples:
 - signal_quality_index combining RSSI and packet loss
 - congestion_score combining latency and network_load
"""

from typing import Dict, Any


def engineer_features(telemetry_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add derived features to a raw telemetry dictionary.

    Returns the augmented dictionary (does not mutate the original).
    """
    features = dict(telemetry_dict)
    # TODO: Add derived features
    # Example:
    # rssi = features.get("rssi_dbm", -1)
    # pl   = features.get("packet_loss_percent", -1)
    # features["signal_quality_index"] = rssi + pl * -0.1  # illustrative only
    return features
