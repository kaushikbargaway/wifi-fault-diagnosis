"""Recovery recommendation service."""

import logging
from app.schemas.recovery import RecoveryRequest, RecoveryPlan

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Placeholder rule map — will be replaced by a proper recommendation engine
# ---------------------------------------------------------------------------
_RECOMMENDATIONS: dict[str, list[dict]] = {
    "weak_wifi_signal": [
        {"action": "Move closer to the access point", "reason": "Low RSSI detected", "expected_result": "Stronger signal", "priority": 1},
        {"action": "Reposition or elevate the router", "reason": "Obstacles may be attenuating signal", "expected_result": "Improved coverage", "priority": 2},
    ],
    "high_latency": [
        {"action": "Check for network congestion", "reason": "High latency often caused by congestion", "expected_result": "Lower round-trip time", "priority": 1},
        {"action": "Restart network equipment", "reason": "Device memory or routing table issue", "expected_result": "Reduced latency", "priority": 2},
    ],
    "packet_loss": [
        {"action": "Check physical cable connections", "reason": "Intermittent packet loss may indicate hardware fault", "expected_result": "Zero packet loss", "priority": 1},
    ],
    "dns_failure": [
        {"action": "Verify DNS server configuration", "reason": "DNS queries are failing", "expected_result": "Successful name resolution", "priority": 1},
        {"action": "Switch to a public DNS (e.g. 8.8.8.8)", "reason": "ISP DNS may be down", "expected_result": "Name resolution restored", "priority": 2},
    ],
    "internet_connectivity_failure": [
        {"action": "Check WAN connection on router", "reason": "No internet reachability detected", "expected_result": "Internet restored", "priority": 1},
        {"action": "Restart router and modem", "reason": "Equipment may require a session reset", "expected_result": "Connectivity restored", "priority": 2},
    ],
    "ethernet_problem": [
        {"action": "Reseat Ethernet cables", "reason": "Ethernet link detected as down", "expected_result": "Link restored", "priority": 1},
    ],
    "router_overheating": [
        {"action": "Ensure router has adequate ventilation", "reason": "Temperature above threshold", "expected_result": "Temperature normalised", "priority": 1},
        {"action": "Reduce router load or restart it", "reason": "Heavy load may contribute to overheating", "expected_result": "Temperature drop", "priority": 2},
    ],
    "network_congestion": [
        {"action": "Identify high-bandwidth processes and limit them", "reason": "Network load is high", "expected_result": "Reduced congestion", "priority": 1},
        {"action": "Enable QoS on the router", "reason": "Prioritise critical traffic", "expected_result": "Improved throughput for priority traffic", "priority": 2},
    ],
    "normal": [
        {"action": "No action required", "reason": "Network is operating normally", "expected_result": "Continued normal operation", "priority": 1},
    ],
}


class RecoveryService:
    """Generates recovery recommendations based on the diagnosed fault."""

    async def recommend(self, request: RecoveryRequest) -> RecoveryPlan:
        """Return an ordered RecoveryPlan for the given fault."""
        from app.schemas.recovery import RecoveryAction

        fault = request.diagnosis.fault_label
        raw = _RECOMMENDATIONS.get(fault, _RECOMMENDATIONS["normal"])
        actions = [RecoveryAction(**a) for a in raw]
        logger.info("Recovery plan generated for fault=%s (%d actions)", fault, len(actions))
        return RecoveryPlan(fault_label=fault, actions=actions)
