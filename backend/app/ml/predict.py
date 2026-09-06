"""Fault prediction using the loaded Random Forest model."""

import logging

from app.schemas.diagnosis import DiagnosisResult
from app.schemas.telemetry import TelemetryCreate
from app.ml.preprocessing import telemetry_to_feature_vector
from app.ml.feature_engineering import engineer_features
from app.ml.model_loader import load_model
from app.core.config import settings

logger = logging.getLogger(__name__)


def predict_fault(telemetry: TelemetryCreate) -> DiagnosisResult:
    """Run the ML model and return a DiagnosisResult.

    Falls back to a placeholder result when no trained model is available.
    """
    telemetry_dict = telemetry.model_dump()
    telemetry_dict = engineer_features(telemetry_dict)
    feature_vector = telemetry_to_feature_vector(telemetry_dict)

    model = load_model()

    if model is None:
        # No trained model yet — return a dummy result for development
        logger.warning("No trained model found. Returning placeholder diagnosis.")
        n_labels = len(settings.FAULT_LABELS)
        uniform_prob = 1.0 / n_labels
        return DiagnosisResult(
            fault_label="normal",
            confidence=uniform_prob,
            probabilities={label: uniform_prob for label in settings.FAULT_LABELS},
            telemetry=telemetry,
        )

    probabilities = model.predict_proba([feature_vector])[0]
    predicted_index = probabilities.argmax()
    fault_label = settings.FAULT_LABELS[predicted_index]
    confidence = float(probabilities[predicted_index])
    prob_dict = {label: float(p) for label, p in zip(settings.FAULT_LABELS, probabilities)}

    return DiagnosisResult(
        fault_label=fault_label,
        confidence=confidence,
        probabilities=prob_dict,
        telemetry=telemetry,
    )
