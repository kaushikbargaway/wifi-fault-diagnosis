"""Sample telemetry payloads for testing."""

SAMPLE_NORMAL = {
    "device_id": "esp32-test-001",
    "rssi_dbm": -55.0,
    "latency_ms": 15.0,
    "packet_loss_percent": 0.0,
    "internet_reachable": True,
    "dns_available": True,
    "ethernet_connected": True,
    "temperature_c": 42.0,
    "network_load": 20.0,
}

SAMPLE_DNS_FAILURE = {
    **SAMPLE_NORMAL,
    "dns_available": False,
    "internet_reachable": False,
}

SAMPLE_HIGH_LATENCY = {
    **SAMPLE_NORMAL,
    "latency_ms": 850.0,
    "packet_loss_percent": 5.0,
}

SAMPLE_WEAK_WIFI = {
    **SAMPLE_NORMAL,
    "rssi_dbm": -88.0,
}
