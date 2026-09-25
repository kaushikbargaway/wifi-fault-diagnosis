"""Digital Twin state, fault injection, and simulation endpoints."""

from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.digital_twin import TwinState, SimulationRequest, SimulationResult
from app.services.digital_twin_service import DigitalTwinService
from app.api.dependencies import get_digital_twin_service

router = APIRouter(prefix="/digital-twin")


@router.get("/state", response_model=TwinState)
async def get_state(
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> TwinState:
    """Return current Digital Twin state by querying both VMs via SSH."""
    return await svc.get_state()


@router.get("/fault-types")
async def list_fault_types(
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> dict:
    """List all injectable fault types."""
    return {"fault_types": await svc.list_fault_types()}


@router.post("/inject")
async def inject_fault(
    fault_type: str,
    vm_name: str = "vm1",
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> dict:
    """
    Inject a network fault on a VM using tc/netem.

    - **fault_type**: e.g. high_latency, packet_loss, dns_failure
    - **vm_name**: vm1 or vm2 (default: vm1)

    ⚠️ VM must be running and reachable at its configured IP.
    """
    return await svc.inject_fault(fault_type, vm_name)


@router.post("/clear")
async def clear_fault(
    vm_name: str = "vm1",
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> dict:
    """Remove all injected fault conditions from the VM (restore normal)."""
    return await svc.clear_fault(vm_name)


@router.get("/fault-status")
async def fault_status(
    vm_name: str = "vm1",
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> dict:
    """Return current tc/iptables state on the VM (diagnostic)."""
    return await svc.check_fault_status(vm_name)


@router.post("/experiment")
async def run_experiment(
    fault_type: str,
    vm_name: str = "vm1",
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> dict:
    """
    Run a full fault injection experiment:
    inject → stabilise → measure → diagnose → save to DB → clear.

    ⚠️ Takes ~20–30 seconds. VM must be running.
    Results are saved to the database automatically.
    """
    return await svc.run_experiment(fault_type, vm_name)


@router.post("/simulate", response_model=SimulationResult)
async def simulate_recovery(
    request: SimulationRequest,
    svc: DigitalTwinService = Depends(get_digital_twin_service),
) -> SimulationResult:
    """Simulate a recovery action and return the predicted outcome."""
    return await svc.simulate(request)
