"""
TwinNet — Synthetic Dataset Generator
======================================
Generates a labelled network-fault dataset for initial ML training.

IMPORTANT: This is SIMULATED data based on realistic network behaviour ranges.
It is used for early-stage development ONLY.
Results from this data must be labelled as 'preliminary simulation results'
in any academic report — NOT as real-world performance.

Each fault class is generated using realistic sensor value ranges
derived from networking documentation and common fault signatures.

Run from the project root:
    python ml/scripts/generate_dataset.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Random seed for reproducibility
SEED = 42
np.random.seed(SEED)

# Output path
OUTPUT_DIR = Path("ml/data/simulated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "network_fault_dataset.csv"

# ──────────────────────────────────────────────────────────────────────────────
# Fault class definitions
# Each class has:
#   - n_samples   : how many rows to generate
#   - feature distributions (mean, std) or fixed values
# ──────────────────────────────────────────────────────────────────────────────

FAULT_CLASSES = {
    "normal": {
        "n": 300,
        "rssi_dbm":             (-55,  8),    # Strong signal
        "latency_ms":           (20,   5),    # Low latency
        "packet_loss_percent":  (0.2,  0.3),  # Near zero loss
        "internet_reachable":   (0.98, None), # Almost always reachable
        "dns_available":        (0.98, None),
        "ethernet_connected":   (0.95, None),
        "temperature_c":        (45,   5),    # Normal temp
        "network_load":         (30,   10),   # Low-moderate load
    },
    "weak_wifi_signal": {
        "n": 250,
        "rssi_dbm":             (-85,  8),    # Very weak signal
        "latency_ms":           (80,   30),   # High latency due to retransmits
        "packet_loss_percent":  (8,    5),    # Notable packet loss
        "internet_reachable":   (0.70, None),
        "dns_available":        (0.75, None),
        "ethernet_connected":   (0.20, None), # Usually WiFi not ethernet
        "temperature_c":        (48,   5),
        "network_load":         (40,   15),
    },
    "high_latency": {
        "n": 250,
        "rssi_dbm":             (-62,  10),
        "latency_ms":           (350,  100),  # Very high latency
        "packet_loss_percent":  (2,    2),    # Some loss
        "internet_reachable":   (0.85, None),
        "dns_available":        (0.80, None),
        "ethernet_connected":   (0.60, None),
        "temperature_c":        (50,   6),
        "network_load":         (75,   15),   # High load causing latency
    },
    "packet_loss": {
        "n": 250,
        "rssi_dbm":             (-68,  10),
        "latency_ms":           (60,   20),
        "packet_loss_percent":  (25,   10),   # High packet loss
        "internet_reachable":   (0.75, None),
        "dns_available":        (0.70, None),
        "ethernet_connected":   (0.55, None),
        "temperature_c":        (47,   5),
        "network_load":         (55,   15),
    },
    "dns_failure": {
        "n": 200,
        "rssi_dbm":             (-58,  8),    # Signal OK
        "latency_ms":           (25,   8),    # Latency OK
        "packet_loss_percent":  (0.5,  0.5),  # Loss near zero
        "internet_reachable":   (0.50, None), # Partial — IP works, DNS doesn't
        "dns_available":        (0.05, None), # DNS failing
        "ethernet_connected":   (0.70, None),
        "temperature_c":        (46,   4),
        "network_load":         (35,   10),
    },
    "internet_connectivity_failure": {
        "n": 200,
        "rssi_dbm":             (-60,  8),    # Local signal fine
        "latency_ms":           (15,   5),    # Local latency fine
        "packet_loss_percent":  (1,    1),
        "internet_reachable":   (0.02, None), # Internet down
        "dns_available":        (0.10, None), # External DNS also fails
        "ethernet_connected":   (0.65, None),
        "temperature_c":        (46,   4),
        "network_load":         (20,   8),    # Low load (nothing going out)
    },
    "ethernet_problem": {
        "n": 200,
        "rssi_dbm":             (-70,  12),   # Forced onto WiFi
        "latency_ms":           (90,   30),
        "packet_loss_percent":  (10,   8),
        "internet_reachable":   (0.60, None),
        "dns_available":        (0.65, None),
        "ethernet_connected":   (0.02, None), # Ethernet down
        "temperature_c":        (47,   5),
        "network_load":         (50,   15),
    },
    "router_overheating": {
        "n": 200,
        "rssi_dbm":             (-65,  10),
        "latency_ms":           (150,  60),   # Thermal throttling = high latency
        "packet_loss_percent":  (12,   8),
        "internet_reachable":   (0.70, None),
        "dns_available":        (0.72, None),
        "ethernet_connected":   (0.60, None),
        "temperature_c":        (85,   10),   # Very high temperature
        "network_load":         (60,   20),
    },
    "network_congestion": {
        "n": 200,
        "rssi_dbm":             (-60,  8),
        "latency_ms":           (280,  80),   # High latency from congestion
        "packet_loss_percent":  (15,   8),
        "internet_reachable":   (0.80, None),
        "dns_available":        (0.78, None),
        "ethernet_connected":   (0.70, None),
        "temperature_c":        (52,   6),
        "network_load":         (92,   5),    # Very high network load
    },
}


def generate_class(fault_label: str, cfg: dict) -> pd.DataFrame:
    """Generate n_samples rows for one fault class."""
    n = cfg["n"]
    rows = []

    for _ in range(n):
        row = {}

        # RSSI
        rssi_mean, rssi_std = cfg["rssi_dbm"]
        row["rssi_dbm"] = float(np.clip(np.random.normal(rssi_mean, rssi_std), -100, -20))

        # Latency
        lat_mean, lat_std = cfg["latency_ms"]
        row["latency_ms"] = float(np.clip(np.random.normal(lat_mean, lat_std), 1, 2000))

        # Packet loss
        pl_mean, pl_std = cfg["packet_loss_percent"]
        row["packet_loss_percent"] = float(np.clip(np.random.normal(pl_mean, pl_std), 0, 100))

        # Boolean features (modelled as Bernoulli)
        for feat in ["internet_reachable", "dns_available", "ethernet_connected"]:
            prob, _ = cfg[feat]
            row[feat] = bool(np.random.random() < prob)

        # Temperature
        t_mean, t_std = cfg["temperature_c"]
        row["temperature_c"] = float(np.clip(np.random.normal(t_mean, t_std), 20, 120))

        # Network load
        nl_mean, nl_std = cfg["network_load"]
        row["network_load"] = float(np.clip(np.random.normal(nl_mean, nl_std), 0, 100))

        # Label
        row["fault_label"] = fault_label

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    logger.info("Generating synthetic dataset...")

    dfs = []
    for label, cfg in FAULT_CLASSES.items():
        df = generate_class(label, cfg)
        dfs.append(df)
        logger.info("  %-40s %d samples", label, len(df))

    dataset = pd.concat(dfs, ignore_index=True)

    # Shuffle rows so classes are not in blocks
    dataset = dataset.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Save
    dataset.to_csv(OUTPUT_PATH, index=False)

    logger.info("─" * 50)
    logger.info("Dataset saved → %s", OUTPUT_PATH)
    logger.info("Total samples : %d", len(dataset))
    logger.info("Class distribution:")
    for label, count in dataset["fault_label"].value_counts().items():
        logger.info("  %-40s %d", label, count)
    logger.info("─" * 50)
    logger.info("WARNING: This is SIMULATED data for development only.")
    logger.info("Label results as 'preliminary simulation' in reports.")


if __name__ == "__main__":
    main()
