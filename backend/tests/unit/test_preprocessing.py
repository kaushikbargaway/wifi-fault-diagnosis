"""Unit tests for the ML preprocessing module."""

import numpy as np
from app.ml.preprocessing import telemetry_to_feature_vector


def test_telemetry_to_feature_vector_all_present():
    """All features present — vector should have no -1.0 sentinel values."""
    telemetry = {
        "rssi_dbm": -60.0,
        "latency_ms": 20.0,
        "packet_loss_percent": 0.5,
        "internet_reachable": True,
        "dns_available": True,
        "ethernet_connected": True,
        "temperature_c": 45.0,
        "network_load": 30.0,
    }
    vector = telemetry_to_feature_vector(telemetry)
    assert vector.shape[0] == 8
    assert all(v != -1.0 for v in vector)


def test_telemetry_to_feature_vector_missing_fields():
    """Missing fields should be filled with the -1.0 sentinel."""
    telemetry = {"rssi_dbm": -80.0}  # only RSSI provided
    vector = telemetry_to_feature_vector(telemetry)
    assert vector[0] == -80.0
    # All other features should be the sentinel
    assert all(v == -1.0 for v in vector[1:])
