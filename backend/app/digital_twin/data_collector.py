"""
Data Collector — runs full fault injection experiments.

Workflow for each experiment:
  1. Inject fault on VM1 (tc/netem via SSH)
  2. Wait for conditions to stabilise
  3. Ping VM1 from host to measure real latency/loss
  4. Collect VM1 metrics via SSH
  5. Run ML diagnosis on the real telemetry
  6. Save labelled record to database
  7. Clear fault conditions (restore normal)

This generates a REAL labelled dataset from actual network degradation.
"""

import logging
import time
from datetime import datetime, timezone

import requests

from app.digital_twin.fault_injector import FaultInjector
from app.digital_twin.vm_monitor import VMMonitor, measure_vm_from_host

logger = logging.getLogger(__name__)

BACKEND_URL     = "http://localhost:8000/api/v1"
STABILISE_SECS  = 4   # wait after injection before measuring
PING_ROUNDS     = 3   # how many measurement rounds per experiment


class DataCollector:
    """
    Runs automated fault injection experiments and collects real labelled data.
    """

    def __init__(self, vm_name: str = "vm1", vm_password: str = "ubuntu123") -> None:
        self.vm_name    = vm_name
        self.injector   = FaultInjector(vm_name, vm_password)
        self.monitor    = VMMonitor(vm_name, vm_password)

    def run_experiment(self, fault_type: str) -> dict:
        """
        Full experiment cycle for one fault type.
        Returns a summary dict with telemetry, diagnosis, and save status.
        """
        logger.info("=" * 55)
        logger.info("Experiment: fault_type=%s  vm=%s", fault_type, self.vm_name)
        logger.info("=" * 55)

        # ── Step 1: Inject fault ───────────────────────────────────────────
        logger.info("Step 1: Injecting fault '%s'...", fault_type)
        inject_result = self.injector.inject(fault_type)
        if not inject_result["ok"]:
            logger.error("Injection failed: %s", inject_result.get("error"))
            return {"ok": False, "fault_type": fault_type, "error": inject_result.get("error")}

        # ── Step 2: Wait for conditions to stabilise ──────────────────────
        logger.info("Step 2: Waiting %ds for conditions to stabilise...", STABILISE_SECS)
        time.sleep(STABILISE_SECS)

        # ── Step 3: Measure from host (ping VM1) ──────────────────────────
        logger.info("Step 3: Measuring network conditions from host...")
        host_measurements = []
        for i in range(PING_ROUNDS):
            m = measure_vm_from_host(self.vm_name)
            host_measurements.append(m)
            logger.info(
                "  Round %d: latency=%.1fms loss=%.1f%%",
                i + 1, m.get("latency_ms", 999), m.get("packet_loss_pct", 100)
            )
            if i < PING_ROUNDS - 1:
                time.sleep(2)

        # Average the measurements
        avg_latency = sum(m.get("latency_ms", 999) for m in host_measurements) / PING_ROUNDS
        avg_loss    = sum(m.get("packet_loss_pct", 100) for m in host_measurements) / PING_ROUNDS

        # ── Step 4: Collect VM metrics ────────────────────────────────────
        logger.info("Step 4: Collecting VM metrics via SSH...")
        vm_metrics = self.monitor.collect()

        # ── Step 5: Build telemetry payload ───────────────────────────────
        telemetry = {
            "device_id":            f"experiment-{self.vm_name}",
            "timestamp":            datetime.now(timezone.utc).isoformat(),
            "latency_ms":           round(avg_latency, 2),
            "packet_loss_percent":  round(avg_loss,    2),
            "internet_reachable":   avg_loss < 90,
            "dns_available":        fault_type not in ("dns_failure",),
            "ethernet_connected":   vm_metrics.get("link_state") == "up",
            "network_load":         vm_metrics.get("cpu_percent", 30.0) or 30.0,
            "temperature_c":        50.0,   # placeholder (Ubuntu VM doesn't expose temp)
            "rssi_dbm":             -60.0,  # not applicable for wired VM
        }

        logger.info(
            "Telemetry: latency=%.1fms loss=%.1f%% internet=%s dns=%s",
            telemetry["latency_ms"], telemetry["packet_loss_percent"],
            telemetry["internet_reachable"], telemetry["dns_available"],
        )

        # ── Step 6: Run diagnosis directly (in-process — avoids HTTP deadlock) ──
        logger.info("Step 5: Running ML diagnosis...")
        diagnosis_result = None

        try:
            from app.ml.predict import predict_fault
            from app.schemas.telemetry import TelemetryCreate
            from app.database.connection import SessionLocal
            from app.database.repositories import TelemetryRepository, DiagnosisRepository

            t_obj = TelemetryCreate(**{k: v for k, v in telemetry.items()
                                       if k != "timestamp"})

            # Run ML prediction
            result = predict_fault(t_obj)
            diagnosis_result = result.model_dump()
            diagnosis_result["timestamp"] = str(diagnosis_result.get("timestamp", ""))

            # Save telemetry + diagnosis to DB
            db = SessionLocal()
            try:
                t_repo = TelemetryRepository(db)
                d_repo = DiagnosisRepository(db)

                saved_t = t_repo.save(telemetry)
                d_repo.save({
                    "fault_label":   result.fault_label,
                    "confidence":    result.confidence,
                    "probabilities": result.probabilities,
                    "telemetry_id":  saved_t.id,
                })
                t_repo.update_fault_label(saved_t.id, result.fault_label)
                logger.info(
                    "  Saved → telemetry_id=%d fault=%s confidence=%.2f",
                    saved_t.id, result.fault_label, result.confidence,
                )
            finally:
                db.close()

        except Exception as e:
            logger.error("Diagnosis/save error: %s", e)

        # ── Step 7: Clear fault conditions ────────────────────────────────
        logger.info("Step 6: Clearing fault conditions (restoring normal)...")
        clear_result = self.injector.clear()
        logger.info("  Cleared: %s", "ok" if clear_result["ok"] else "failed")

        return {
            "ok":             True,
            "fault_type":     fault_type,
            "vm":             self.vm_name,
            "telemetry":      telemetry,
            "diagnosis":      diagnosis_result,
            "prediction_correct": (
                diagnosis_result.get("fault_label") == fault_type
                if diagnosis_result else None
            ),
            "avg_latency_ms": avg_latency,
            "avg_loss_pct":   avg_loss,
            "vm_metrics":     vm_metrics,
            "injection":      inject_result,
            "cleared":        clear_result["ok"],
        }

    def run_all_experiments(self, fault_types: list[str] | None = None, delay_between: int = 10) -> list[dict]:
        """
        Run experiments for all (or specified) fault types sequentially.
        Returns a list of experiment results.
        """
        from app.digital_twin.fault_injector import FAULT_COMMANDS
        types = fault_types or list(FAULT_COMMANDS.keys())
        results = []

        logger.info("Starting full experiment suite: %d fault types", len(types))

        for fault_type in types:
            result = self.run_experiment(fault_type)
            results.append(result)

            if fault_type != types[-1]:
                logger.info("Waiting %ds before next experiment...", delay_between)
                time.sleep(delay_between)

        # Summary
        correct  = sum(1 for r in results if r.get("prediction_correct"))
        total    = len([r for r in results if r.get("prediction_correct") is not None])
        logger.info("=" * 55)
        logger.info("Experiment suite complete: %d/%d correct predictions", correct, total)
        logger.info("=" * 55)

        return results
