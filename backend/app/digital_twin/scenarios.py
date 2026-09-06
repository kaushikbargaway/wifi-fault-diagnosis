"""Pre-defined network fault scenarios for the Digital Twin (placeholder).

Each scenario describes the network conditions that correspond to a
specific fault category. Scenarios are used to:
1. Simulate faults for testing.
2. Validate the ML model against known conditions.
3. Test recovery actions before real deployment.
"""

from typing import Any, Dict, List

# Maps fault_label -> list of tc/netem parameters to apply
SCENARIOS: Dict[str, List[Dict[str, Any]]] = {
    "weak_wifi_signal": [],       # TODO: reduce TX power on virtual wifi
    "high_latency":     [{"delay": "200ms", "jitter": "20ms"}],
    "packet_loss":      [{"loss": "10%"}],
    "dns_failure":      [],       # TODO: block port 53 via iptables
    "internet_connectivity_failure": [],  # TODO: block default route
    "ethernet_problem": [],       # TODO: simulate link down via ip link
    "router_overheating": [],     # out-of-band; temperature sensor only
    "network_congestion": [{"rate": "1mbit"}],
    "normal": [],
}
