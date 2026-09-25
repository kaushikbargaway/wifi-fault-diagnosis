"""
VM Monitor — collects real network metrics from Ubuntu VMs via SSH.
Used to build the real Digital Twin state (replacing static placeholders).
"""

import logging
import re
import subprocess
import platform
from datetime import datetime, timezone
from typing import Optional

from app.digital_twin.ssh_client import SSHClient, get_vm_client, VM_HOSTS
from app.schemas.digital_twin import NetworkNode, TwinState

logger = logging.getLogger(__name__)

VM_INTERFACE = "enp0s8"


class VMMonitor:
    """Collects metrics from a single Ubuntu VM via SSH."""

    def __init__(self, vm_name: str, password: str = "ubuntu123") -> None:
        self.vm_name = vm_name
        self.client  = get_vm_client(vm_name, password=password)

    def is_reachable(self) -> bool:
        """Quick TCP ping to check if VM SSH port is open."""
        return self.client.ping()

    def collect(self) -> dict:
        """
        Collect all metrics from the VM.
        Returns a dict with all measured values.
        If VM is offline, returns a dict with status='offline'.
        """
        if not self.client.connect():
            return {
                "vm":     self.vm_name,
                "ip":     self.client.host,
                "status": "offline",
                "error":  "VM not reachable",
            }

        metrics = {
            "vm":     self.vm_name,
            "ip":     self.client.host,
            "status": "up",
        }

        # 1. IP address of the host-only interface
        r = self.client.exec(f"ip -4 addr show {VM_INTERFACE} | grep 'inet '")
        if r["ok"] and r["stdout"]:
            ip_match = re.search(r"inet\s+([\d.]+/\d+)", r["stdout"])
            metrics["ip_address"] = ip_match.group(1) if ip_match else "unknown"

        # 2. Interface link status
        r = self.client.exec(f"cat /sys/class/net/{VM_INTERFACE}/operstate 2>/dev/null")
        metrics["link_state"] = r["stdout"].strip() if r["ok"] else "unknown"
        if metrics["link_state"] != "up":
            metrics["status"] = "degraded"

        # 3. CPU usage (1-second sample)
        r = self.client.exec(
            "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        )
        try:
            metrics["cpu_percent"] = float(r["stdout"]) if r["ok"] else None
        except ValueError:
            metrics["cpu_percent"] = None

        # 4. Memory usage
        r = self.client.exec("free | awk '/Mem:/ {printf \"%.1f\", $3/$2*100}'")
        try:
            metrics["mem_percent"] = float(r["stdout"]) if r["ok"] else None
        except ValueError:
            metrics["mem_percent"] = None

        # 5. Current tc/netem rules (detect active faults)
        r = self.client.exec_sudo(f"tc qdisc show dev {VM_INTERFACE}")
        tc_output = r["stdout"] if r["ok"] else ""
        metrics["tc_rules"]       = tc_output
        metrics["has_netem"]      = "netem" in tc_output.lower()

        # Extract netem parameters if active
        if metrics["has_netem"]:
            delay_match = re.search(r"delay\s+([\d.]+)ms", tc_output)
            loss_match  = re.search(r"loss\s+([\d.]+)%",  tc_output)
            metrics["injected_delay_ms"]  = float(delay_match.group(1)) if delay_match else None
            metrics["injected_loss_pct"]  = float(loss_match.group(1))  if loss_match  else None

        # 6. Apache service status
        r = self.client.exec("systemctl is-active apache2 2>/dev/null")
        metrics["apache_status"] = r["stdout"].strip() if r["ok"] else "unknown"

        # 7. Uptime
        r = self.client.exec("uptime -p")
        metrics["uptime"] = r["stdout"] if r["ok"] else "unknown"

        # 8. Disk usage
        r = self.client.exec("df -h / | awk 'NR==2{print $5}'")
        metrics["disk_used_pct"] = r["stdout"].strip() if r["ok"] else "unknown"

        self.client.disconnect()
        logger.debug("VM metrics collected for %s: %s", self.vm_name, metrics)
        return metrics


def _windows_ping(host: str, count: int = 4) -> dict:
    """Ping a host from Windows and return latency/loss."""
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), host],
            capture_output=True, text=True, timeout=15,
        )
        out = result.stdout
        loss_match   = re.search(r"(\d+)%\s+loss", out)
        avg_match    = re.search(r"Average\s*=\s*(\d+)ms", out)
        packet_loss  = float(loss_match.group(1)) if loss_match else 100.0
        latency      = float(avg_match.group(1))  if avg_match  else 999.0
        return {"latency_ms": latency, "packet_loss_pct": packet_loss, "reachable": packet_loss < 100}
    except Exception as e:
        return {"latency_ms": 999.0, "packet_loss_pct": 100.0, "reachable": False, "error": str(e)}


def measure_vm_from_host(vm_name: str) -> dict:
    """
    Ping a VM from the Windows host to measure latency and packet loss.
    This is the HOST-SIDE measurement (what the admin sees).
    """
    host = VM_HOSTS.get(vm_name.lower())
    if not host:
        return {"error": f"Unknown VM: {vm_name}"}
    result = _windows_ping(host)
    result["vm"]   = vm_name
    result["host"] = host
    return result


def build_twin_state(
    vm1_metrics: dict,
    vm2_metrics: dict,
    last_fault_label: Optional[str] = None,
) -> TwinState:
    """
    Build a TwinState from collected VM metrics.
    This replaces the static placeholder in twin_state.py.
    """

    def vm_status(m: dict) -> str:
        if m.get("status") == "offline":
            return "down"
        if m.get("has_netem"):
            return "degraded"
        if m.get("link_state") != "up":
            return "degraded"
        return "up"

    def vm_node(name: str, node_type: str, metrics: dict) -> NetworkNode:
        status = vm_status(metrics)
        node_metrics = {}
        for key in ["cpu_percent", "mem_percent", "disk_used_pct",
                    "apache_status", "injected_delay_ms", "injected_loss_pct"]:
            if metrics.get(key) is not None:
                node_metrics[key] = metrics[key]
        return NetworkNode(node_id=name, node_type=node_type, status=status, metrics=node_metrics)

    nodes = [
        vm_node("vm1", "server", vm1_metrics),
        vm_node("vm2", "server", vm2_metrics),
        NetworkNode(node_id="router",  node_type="router",     status="up",      metrics={}),
        NetworkNode(node_id="esp32",   node_type="iot_sensor", status="unknown", metrics={}),
    ]

    # Overall health = worst node status
    statuses = [n.status for n in nodes]
    if "down"     in statuses: overall = "down"
    elif "degraded" in statuses: overall = "degraded"
    elif "unknown"  in statuses: overall = "unknown"
    else:                        overall = "up"

    return TwinState(
        nodes=nodes,
        overall_health=overall,
        last_synced=datetime.now(timezone.utc).isoformat(),
        fault_label=last_fault_label,
    )
