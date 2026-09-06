"""Explanation service — generates human-readable fault explanations via RAG/LLM."""

import logging
from app.schemas.diagnosis import DiagnosisResult
from app.rag.retriever import retrieve_context
from app.rag.generator import generate_explanation

logger = logging.getLogger(__name__)


class ExplanationService:
    """Coordinates context retrieval and LLM generation."""

    async def explain(self, diagnosis: DiagnosisResult) -> dict:
        """Retrieve relevant knowledge and generate a plain-English explanation."""
        context = retrieve_context(diagnosis.fault_label)
        explanation = generate_explanation(diagnosis, context)
        logger.info("Explanation generated for fault=%s", diagnosis.fault_label)
        return {"fault_label": diagnosis.fault_label, "explanation": explanation}
