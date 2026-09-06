# ESP32 Firmware — Telemetry Layer

This directory contains the firmware and sensor integration code for the ESP32 microcontroller.

## What the ESP32 Does

- Measures Wi-Fi RSSI.
- Pings a target host to measure latency and detect packet loss.
- Checks DNS availability.
- Checks internet reachability.
- Reads temperature from an attached sensor (e.g. DS18B20).
- Periodically sends a JSON telemetry payload to the FastAPI backend via HTTP POST.

## Structure

```
esp32/
├── firmware/     Main Arduino / ESP-IDF firmware sketch
├── sensors/      Sensor driver code (temperature, etc.)
├── network/      Wi-Fi connectivity, HTTP client, ping utilities
└── README.md
```

## Development Without Hardware

Set `USE_SIMULATED_TELEMETRY=true` in `.env`.
The backend will generate synthetic telemetry on a configurable interval.

## Telemetry Payload Format

```json
{
  "device_id": "esp32-lab-01",
  "rssi_dbm": -65,
  "latency_ms": 22,
  "packet_loss_percent": 0.5,
  "internet_reachable": true,
  "dns_available": true,
  "ethernet_connected": false,
  "temperature_c": 44.2,
  "network_load": 18.5
}
```

POST to: `http://<backend-ip>:8000/api/v1/telemetry/`
