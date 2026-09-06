"""LLM-based explanation generator (placeholder)."""

from typing import List
from app.schemas.diagnosis import DiagnosisResult
from app.core.config import settings


def generate_explanation(diagnosis: DiagnosisResult, context_chunks: List[str]) -> str:
    """Generate a human-readable explanation for the diagnosed fault.

    Uses retrieved context chunks and the LLM to explain:
    - What fault was detected
    - Why it was detected (which telemetry values triggered it)
    - Recommended recovery actions
    - Expected outcome of each action

    TODO: Build the prompt, call the configured LLM, and return the response.
    """
    # Placeholder — return a templated string until the LLM is connected.
    return (
        f"[PLACEHOLDER EXPLANATION]\n"
        f"Detected fault: {diagnosis.fault_label}\n"
        f"Confidence: {diagnosis.confidence:.0%}\n"
        f"LLM explanation will be generated here once the RAG pipeline is implemented."
    )
