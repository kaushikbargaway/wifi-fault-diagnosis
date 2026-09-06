# Digital Twin Component

This directory contains configuration, scenario definitions, and automation scripts for the Ubuntu-VM-based Digital Twin.

## Architecture

Two Ubuntu VMs are used:

| VM | Role |
|----|------|
| VM1 (192.168.56.101) | Primary network node — simulates a client-side device |
| VM2 (192.168.56.102) | Secondary network node — simulates a server or router peer |

Network conditions (latency, packet loss, bandwidth limits) are applied using **Linux Traffic Control (`tc`)** and **NetEm**.

## Structure

```
digital-twin/
├── vm1/          VM1-specific configuration and scripts
├── vm2/          VM2-specific configuration and scripts
├── configs/      Shared network configuration files
├── scenarios/    Pre-defined fault scenario definitions (YAML / JSON)
├── scripts/      Automation scripts (apply/clear conditions, SSH helpers)
└── README.md
```

## Setup

1. Import the two Ubuntu VMs into VirtualBox / VMware.
2. Configure host-only networking so both VMs can communicate.
3. Set up SSH key-based access: copy your public key to both VMs.
4. Update `.env` with the VM IPs and SSH key path.
5. Test connectivity: `ssh ubuntu@192.168.56.101`

## Applying a Scenario (Example)

```bash
# On VM1 — introduce 200 ms delay with 10% packet loss
sudo tc qdisc add dev eth0 root netem delay 200ms loss 10%

# Clear conditions
sudo tc qdisc del dev eth0 root
```

Automated scenario application will be implemented in `scripts/apply_scenario.sh`.
