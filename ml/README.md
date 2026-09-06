# ML — Machine Learning Component

This directory contains everything needed to develop and train the Random Forest fault classifier **outside** the FastAPI backend.

## Structure

```
ml/
├── data/
│   ├── raw/          Raw datasets (gitignored)
│   ├── processed/    Cleaned and feature-engineered datasets (gitignored)
│   └── sample/       Small sample data for development testing
├── notebooks/        Jupyter notebooks for exploration and experimentation
├── scripts/          Training and evaluation scripts
├── models/           Saved model artefacts (gitignored)
└── reports/          Evaluation reports, confusion matrices, plots
```

## Workflow

1. Place your dataset CSV in `data/raw/`.
2. Run the preprocessing notebook or script to produce `data/processed/`.
3. Run `scripts/train.py` to train the Random Forest and save the model.
4. Run `scripts/evaluate.py` to generate evaluation reports in `reports/`.
5. Copy the best model to `backend/models/` for inference.

## Feature List

| Feature | Description |
|---------|-------------|
| `rssi_dbm` | Wi-Fi signal strength |
| `latency_ms` | Round-trip latency |
| `packet_loss_percent` | % of packets lost |
| `internet_reachable` | WAN reachability (0/1) |
| `dns_available` | DNS resolution success (0/1) |
| `ethernet_connected` | Ethernet link status (0/1) |
| `temperature_c` | Router/device temperature |
| `network_load` | Network utilisation % |

## Target Labels

`normal`, `weak_wifi_signal`, `high_latency`, `packet_loss`, `dns_failure`,
`internet_connectivity_failure`, `ethernet_problem`, `router_overheating`, `network_congestion`
