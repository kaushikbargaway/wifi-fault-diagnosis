"""Network condition simulator for the Digital Twin (placeholder).

Will use VM1 and VM2 (Ubuntu) to reproduce specific network conditions
(e.g. introduce artificial packet loss, cap bandwidth) for testing
recovery actions before applying them to the real network.
"""


def apply_condition(condition: str, target: str = "vm1") -> bool:
    """Apply a named network condition to the specified VM (placeholder).

    Args:
        condition: e.g. "high_latency", "packet_loss_10pct"
        target:    VM hostname or identifier

    Returns:
        True if condition was applied successfully, False otherwise.

    TODO: Implement using tc (traffic control) or netem on the Ubuntu VMs.
    """
    raise NotImplementedError("VM-based simulation not yet implemented.")


def clear_conditions(target: str = "vm1") -> bool:
    """Remove all artificial network conditions from the target VM (placeholder)."""
    raise NotImplementedError("Not yet implemented.")
