"""
TwinNet — Real Network Telemetry Collector
==========================================
Collects REAL network metrics from the local machine and sends them
to the TwinNet backend every N seconds.

Measures:
  - Real ping latency and packet loss (to google.com)
  - Real DNS resolution time
  - Real internet reachability
  - Real CPU and network load (psutil)
  - Real network interface status

Run from project root (with backend venv active):
    python monitoring/telemetry_collector.py

Requirements (already in requirements.txt):
    pip install psutil requests
"""

import time
import socket
import subprocess
import platform
import logging
import json
import re
from datetime import datetime, timezone

import psutil
import requests

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
BACKEND_URL      = "http://localhost:8000/api/v1"
DEVICE_ID        = "windows-laptop-collector"
COLLECT_INTERVAL = 5          # seconds between readings
PING_TARGET      = "8.8.8.8"  # Google DNS — reliable ping target
PING_COUNT       = 4          # pings per measurement
DNS_TARGET       = "google.com"
HTTP_TARGET      = "http://www.google.com"
HTTP_TIMEOUT     = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Measurement functions
# ──────────────────────────────────────────────────────────────────────────────

def measure_ping(target: str = PING_TARGET, count: int = PING_COUNT) -> dict:
    """
    Run real ping and parse latency + packet loss.
    Works on Windows and Linux.
    Returns: { latency_ms, packet_loss_percent, jitter_ms }
    """
    is_windows = platform.system() == "Windows"
    cmd = ["ping", "-n" if is_windows else "-c", str(count), target]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
        output = result.stdout

        # Parse packet loss
        if is_windows:
            loss_match = re.search(r"(\d+)%\s+loss", output)
        else:
            loss_match = re.search(r"(\d+)%\s+packet loss", output)
        packet_loss = float(loss_match.group(1)) if loss_match else 100.0

        # Parse average latency
        if is_windows:
            avg_match = re.search(r"Average\s*=\s*(\d+)ms", output)
            min_match = re.search(r"Minimum\s*=\s*(\d+)ms", output)
            max_match = re.search(r"Maximum\s*=\s*(\d+)ms", output)
        else:
            avg_match = re.search(r"rtt\s+min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", output)

        if is_windows and avg_match:
            latency = float(avg_match.group(1))
            min_lat = float(min_match.group(1)) if min_match else latency
            max_lat = float(max_match.group(1)) if max_match else latency
            jitter = max_lat - min_lat
        elif not is_windows and avg_match:
            latency = float(avg_match.group(2))
            jitter  = float(avg_match.group(4))
        else:
            latency = 999.0
            jitter  = 0.0

        return {
            "latency_ms":           round(latency, 2),
            "packet_loss_percent":  round(packet_loss, 2),
            "jitter_ms":            round(jitter, 2),
        }

    except subprocess.TimeoutExpired:
        logger.warning("Ping timed out to %s", target)
        return {"latency_ms": 999.0, "packet_loss_percent": 100.0, "jitter_ms": 0.0}
    except Exception as e:
        logger.error("Ping error: %s", e)
        return {"latency_ms": 999.0, "packet_loss_percent": 100.0, "jitter_ms": 0.0}


def measure_dns(target: str = DNS_TARGET) -> dict:
    """
    Measure DNS resolution time for a hostname.
    Returns: { dns_available, dns_response_ms }
    """
    start = time.perf_counter()
    try:
        socket.getaddrinfo(target, None)
        elapsed = (time.perf_counter() - start) * 1000
        return {"dns_available": True, "dns_response_ms": round(elapsed, 2)}
    except socket.gaierror:
        return {"dns_available": False, "dns_response_ms": None}


def measure_internet(target: str = HTTP_TARGET) -> dict:
    """
    Check if internet is reachable via HTTP.
    Returns: { internet_reachable }
    """
    try:
        r = requests.get(target, timeout=HTTP_TIMEOUT)
        return {"internet_reachable": r.status_code < 500}
    except Exception:
        return {"internet_reachable": False}


def measure_system() -> dict:
    """
    Collect CPU, memory, and network interface metrics using psutil.
    Returns: { cpu_usage_percent, memory_usage_percent, network_load, ethernet_connected, rssi_dbm }
    """
    cpu    = psutil.cpu_percent(interval=1)
    mem    = psutil.virtual_memory().percent

    # Network load — bytes sent/recv over 1 second
    net1   = psutil.net_io_counters()
    time.sleep(1)
    net2   = psutil.net_io_counters()
    bytes_per_sec = (net2.bytes_sent + net2.bytes_recv) - (net1.bytes_sent + net1.bytes_recv)
    # Rough normalisation: assume 100 Mbps link = 12.5 MB/s max
    network_load = min(100.0, (bytes_per_sec / (12.5 * 1024 * 1024)) * 100)

    # Interface status — check if any non-loopback interface is up
    interfaces = psutil.net_if_stats()
    ethernet_connected = any(
        stats.isup and name.lower() not in ("lo", "loopback")
        for name, stats in interfaces.items()
        if "eth" in name.lower() or "en" in name.lower() or "local" in name.lower()
    )

    # RSSI — Windows only via netsh (returns None on Linux without hardware)
    rssi_dbm = _get_wifi_rssi_windows()

    return {
        "cpu_usage_percent":    round(cpu, 1),
        "memory_usage_percent": round(mem, 1),
        "network_load":         round(network_load, 2),
        "ethernet_connected":   ethernet_connected,
        "rssi_dbm":             rssi_dbm,
    }


def _get_wifi_rssi_windows() -> float | None:
    """Try to get WiFi RSSI on Windows via netsh."""
    if platform.system() != "Windows":
        return None
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"Signal\s*:\s*(\d+)%", result.stdout)
        if match:
            signal_pct = int(match.group(1))
            # Convert percentage to approximate dBm: 100% ≈ -50 dBm, 0% ≈ -100 dBm
            rssi = -100 + (signal_pct / 100) * 50
            return round(rssi, 1)
    except Exception:
        pass
    return None


def measure_temperature() -> dict:
    """
    Try to get system temperature.
    Returns None if not supported (most Windows laptops don't expose this via psutil).
    """
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Get first available sensor
            for key, entries in temps.items():
                if entries:
                    return {"temperature_c": round(entries[0].current, 1)}
    except AttributeError:
        pass  # Windows usually doesn't support this
    return {"temperature_c": None}


# ──────────────────────────────────────────────────────────────────────────────
# Main collector
# ──────────────────────────────────────────────────────────────────────────────

def collect_telemetry() -> dict:
    """Run all measurements and return a combined telemetry dict."""
    logger.info("Collecting telemetry...")

    ping    = measure_ping()
    dns     = measure_dns()
    internet = measure_internet()
    system  = measure_system()
    temp    = measure_temperature()

    telemetry = {
        "device_id":            DEVICE_ID,
        "timestamp":            datetime.now(timezone.utc).isoformat(),
        # Network quality
        "latency_ms":           ping["latency_ms"],
        "packet_loss_percent":  ping["packet_loss_percent"],
        # Connectivity
        "internet_reachable":   internet["internet_reachable"],
        "dns_available":        dns["dns_available"],
        "ethernet_connected":   system["ethernet_connected"],
        # System
        "network_load":         system["network_load"],
        # Optional (may be None)
        "rssi_dbm":             system.get("rssi_dbm"),
        "temperature_c":        temp.get("temperature_c"),
    }

    # Log summary
    logger.info(
        "latency=%.1fms loss=%.1f%% internet=%s dns=%s load=%.1f%% rssi=%s",
        telemetry["latency_ms"],
        telemetry["packet_loss_percent"],
        "✓" if telemetry["internet_reachable"] else "✗",
        "✓" if telemetry["dns_available"] else "✗",
        telemetry["network_load"],
        f"{telemetry['rssi_dbm']}dBm" if telemetry["rssi_dbm"] else "N/A",
    )

    return telemetry


def send_telemetry(telemetry: dict) -> bool:
    """POST telemetry to the backend."""
    # Remove None values — backend treats missing as -1 (not reported)
    payload = {k: v for k, v in telemetry.items() if v is not None}
    try:
        r = requests.post(
            f"{BACKEND_URL}/telemetry/",
            json=payload,
            timeout=5,
        )
        r.raise_for_status()
        logger.info("→ Sent to backend (id=%s)", r.json().get("id"))
        return True
    except requests.ConnectionError:
        logger.warning("Backend not reachable at %s", BACKEND_URL)
        return False
    except Exception as e:
        logger.error("Failed to send telemetry: %s", e)
        return False


def run_once() -> dict:
    """Collect and send one reading. Returns the telemetry dict."""
    t = collect_telemetry()
    send_telemetry(t)
    return t


def run_loop(interval: int = COLLECT_INTERVAL) -> None:
    """Continuously collect and send telemetry."""
    logger.info("=" * 55)
    logger.info("TwinNet Real Telemetry Collector")
    logger.info("Device   : %s", DEVICE_ID)
    logger.info("Backend  : %s", BACKEND_URL)
    logger.info("Interval : %ds", interval)
    logger.info("Ping to  : %s", PING_TARGET)
    logger.info("=" * 55)
    logger.info("Press Ctrl+C to stop.\n")

    while True:
        try:
            run_once()
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Collector stopped.")
            break
        except Exception as e:
            logger.error("Unexpected error: %s — retrying in %ds", e, interval)
            time.sleep(interval)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TwinNet telemetry collector")
    parser.add_argument("--interval", type=int, default=COLLECT_INTERVAL,
                        help=f"Collection interval in seconds (default: {COLLECT_INTERVAL})")
    parser.add_argument("--once", action="store_true",
                        help="Collect a single reading and exit")
    args = parser.parse_args()

    if args.once:
        t = run_once()
        print(json.dumps(t, indent=2, default=str))
    else:
        run_loop(args.interval)
