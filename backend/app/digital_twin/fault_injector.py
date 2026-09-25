"""
Fault Injector — applies tc/netem and iptables rules on VMs via SSH
to simulate specific network fault conditions.

Each fault type maps to one or more shell commands that are run on the target VM.
The 'clear' operation removes all injected conditions.

IMPORTANT: These commands affect the VM's virtual network, NOT your real laptop.
The changes are isolated inside VirtualBox — safe to experiment with.
"""

import logging
from typing import Optional
from app.digital_twin.ssh_client import SSHClient, get_vm_client

logger = logging.getLogger(__name__)

# Network interface on the VMs (host-only adapter — the one we control)
VM_INTERFACE = "enp0s8"

# ─────────────────────────────────────────────────────────────────────────────
# tc/netem and iptables command definitions per fault type
# ─────────────────────────────────────────────────────────────────────────────

# Each entry is a list of shell commands to run (in order) on the VM.
# All tc commands need sudo.
FAULT_COMMANDS: dict[str, list[str]] = {

    "normal": [
        # Remove all traffic shaping rules
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Remove any iptables rules we added
        "iptables -D OUTPUT -p udp --dport 53 -j DROP 2>/dev/null || true",
        "iptables -D OUTPUT -p tcp --dport 53 -j DROP 2>/dev/null || true",
        "iptables -D OUTPUT -p tcp --dport 80  -j DROP 2>/dev/null || true",
        "iptables -D OUTPUT -p tcp --dport 443 -j DROP 2>/dev/null || true",
    ],

    "high_latency": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # 300ms delay with ±30ms jitter (realistic high latency)
        f"tc qdisc add dev {VM_INTERFACE} root netem delay 300ms 30ms distribution normal",
    ],

    "packet_loss": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # 20% packet loss — Gilbert model for burst loss
        f"tc qdisc add dev {VM_INTERFACE} root netem loss 20% 25%",
    ],

    "network_congestion": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # High latency + significant packet loss + rate limit = congestion
        f"tc qdisc add dev {VM_INTERFACE} root netem delay 250ms 40ms loss 15% rate 512kbit",
    ],

    "weak_wifi_signal": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Moderate delay + noticeable packet loss (simulates weak RF)
        f"tc qdisc add dev {VM_INTERFACE} root netem delay 80ms 25ms loss 8% corrupt 1%",
    ],

    "router_overheating": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Thermal throttling: high latency + burst packet loss
        f"tc qdisc add dev {VM_INTERFACE} root netem delay 200ms 50ms loss 12% 20%",
    ],

    "dns_failure": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Block all DNS traffic (UDP and TCP port 53)
        "iptables -I OUTPUT -p udp --dport 53 -j DROP",
        "iptables -I OUTPUT -p tcp --dport 53 -j DROP",
    ],

    "internet_connectivity_failure": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Block HTTP and HTTPS outbound — simulates WAN down
        "iptables -I OUTPUT -p tcp --dport 80  -j DROP",
        "iptables -I OUTPUT -p tcp --dport 443 -j DROP",
    ],

    "ethernet_problem": [
        f"tc qdisc del dev {VM_INTERFACE} root 2>/dev/null || true",
        # Heavy corruption + loss — simulates bad cable/port
        f"tc qdisc add dev {VM_INTERFACE} root netem loss 35% corrupt 5% delay 60ms 20ms",
    ],
}

# Commands to verify the current tc state (for diagnostics)
CHECK_TC_CMD   = f"tc qdisc show dev {VM_INTERFACE}"
CHECK_IP_RULES = "iptables -L OUTPUT --line-numbers -n 2>/dev/null | head -20"


# ─────────────────────────────────────────────────────────────────────────────
# FaultInjector class
# ─────────────────────────────────────────────────────────────────────────────

class FaultInjector:
    """Applies and clears network fault conditions on a VM via SSH."""

    def __init__(self, vm_name: str = "vm1", vm_password: str = "ubuntu123") -> None:
        self.vm_name   = vm_name
        self.client    = get_vm_client(vm_name, password=vm_password)
        self._active_fault: Optional[str] = None

    def inject(self, fault_type: str) -> dict:
        """
        Apply the specified fault on the VM.

        Returns:
            { "ok": bool, "fault_type": str, "vm": str, "details": list[dict] }
        """
        if fault_type not in FAULT_COMMANDS:
            return {
                "ok": False,
                "fault_type": fault_type,
                "vm": self.vm_name,
                "error": f"Unknown fault type: {fault_type!r}. "
                         f"Valid: {list(FAULT_COMMANDS.keys())}",
            }

        logger.info("Injecting fault '%s' on %s", fault_type, self.vm_name)

        if not self.client.connect():
            return {
                "ok": False,
                "fault_type": fault_type,
                "vm": self.vm_name,
                "error": f"Cannot SSH into {self.vm_name} ({self.client.host}). "
                         "Is the VM running?",
            }

        commands = FAULT_COMMANDS[fault_type]
        results  = []
        all_ok   = True

        for cmd in commands:
            result = self.client.exec_sudo(cmd)
            results.append({"cmd": cmd, **result})
            if not result["ok"] and "2>/dev/null" not in cmd:
                # Only fail hard if it's not a "best effort" cleanup command
                logger.warning("Command failed: %s → %s", cmd, result["stderr"])
                all_ok = False

        if all_ok:
            self._active_fault = fault_type
            logger.info("Fault '%s' injected successfully on %s", fault_type, self.vm_name)
        else:
            logger.error("Some commands failed injecting '%s' on %s", fault_type, self.vm_name)

        self.client.disconnect()
        return {
            "ok":          all_ok,
            "fault_type":  fault_type,
            "vm":          self.vm_name,
            "vm_ip":       self.client.host,
            "commands_run": len(commands),
            "details":     results,
        }

    def clear(self) -> dict:
        """Remove all injected fault conditions (reset VM to normal)."""
        return self.inject("normal")

    def get_active_fault(self) -> Optional[str]:
        """Return the last injected fault type (in-memory only)."""
        return self._active_fault

    def check_status(self) -> dict:
        """Return current tc and iptables state on the VM (diagnostic)."""
        if not self.client.connect():
            return {"ok": False, "error": f"Cannot reach {self.vm_name}"}

        tc_result  = self.client.exec_sudo(CHECK_TC_CMD)
        ipt_result = self.client.exec_sudo(CHECK_IP_RULES)
        self.client.disconnect()

        return {
            "ok":        True,
            "vm":        self.vm_name,
            "vm_ip":     self.client.host,
            "tc_rules":  tc_result["stdout"],
            "iptables":  ipt_result["stdout"],
            "active_fault": self._active_fault,
        }

    @property
    def fault_types(self) -> list[str]:
        """List all injectable fault types."""
        return list(FAULT_COMMANDS.keys())
