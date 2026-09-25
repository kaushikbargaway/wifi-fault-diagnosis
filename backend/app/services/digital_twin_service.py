"""Digital Twin service — orchestrates twin state, fault injection and simulation."""

import logging
from app.schemas.digital_twin import TwinState, SimulationRequest, SimulationResult
from app.digital_twin.vm_monitor import VMMonitor, build_twin_state
from app.digital_twin.fault_injector import FaultInjector, FAULT_COMMANDS
from app.digital_twin.recovery_simulator import simulate_action

logger = logging.getLogger(__name__)

# Module-level injector (persists active fault across requests)
_injector = FaultInjector(vm_name="vm1")


class DigitalTwinService:
    """Orchestration layer between API and Digital Twin modules."""

    # ── State ──────────────────────────────────────────────────────────────

    async def get_state(self) -> TwinState:
        """Return the current Digital Twin state by querying both VMs via SSH."""
        logger.info("Collecting Digital Twin state from VMs...")

        vm1 = VMMonitor("vm1").collect()
        vm2 = VMMonitor("vm2").collect()

        state = build_twin_state(
            vm1_metrics=vm1,
            vm2_metrics=vm2,
            last_fault_label=_injector.get_active_fault(),
        )

        logger.info(
            "Twin state: health=%s vm1=%s vm2=%s",
            state.overall_health,
            vm1.get("status"),
            vm2.get("status"),
        )
        return state

    # ── Fault injection ────────────────────────────────────────────────────

    async def inject_fault(self, fault_type: str, vm_name: str = "vm1") -> dict:
        """Apply a network fault on the specified VM."""
        injector = FaultInjector(vm_name)
        return injector.inject(fault_type)

    async def clear_fault(self, vm_name: str = "vm1") -> dict:
        """Clear all injected fault conditions from the VM."""
        injector = FaultInjector(vm_name)
        return injector.clear()

    async def check_fault_status(self, vm_name: str = "vm1") -> dict:
        """Return current tc/iptables state on the VM."""
        injector = FaultInjector(vm_name)
        return injector.check_status()

    async def list_fault_types(self) -> list[str]:
        """Return all supported fault types."""
        return list(FAULT_COMMANDS.keys())

    # ── Data collection experiment ─────────────────────────────────────────

    async def run_experiment(self, fault_type: str, vm_name: str = "vm1") -> dict:
        """
        Run a full fault injection experiment:
        inject → measure → diagnose → save → clear.
        """
        from app.digital_twin.data_collector import DataCollector
        collector = DataCollector(vm_name)
        return collector.run_experiment(fault_type)

    # ── Recovery simulation ────────────────────────────────────────────────

    async def simulate(self, request: SimulationRequest) -> SimulationResult:
        """Simulate a recovery action and return the predicted outcome."""
        result = simulate_action(request)
        logger.info(
            "Simulation: action=%s improvement=%.2f",
            request.action, result.improvement_score,
        )
        return result
