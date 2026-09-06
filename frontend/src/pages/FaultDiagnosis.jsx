import React from 'react';

/**
 * Fault Diagnosis page.
 * Will display: detected fault, confidence, supporting telemetry, history.
 * TODO: Wire up to GET /api/v1/diagnosis/history and POST /api/v1/diagnosis/
 */
function FaultDiagnosis() {
  return (
    <div>
      <h1>Fault Diagnosis</h1>
      <p style={{ color: 'var(--color-muted)', marginTop: '0.5rem' }}>
        Displays diagnosed faults, confidence scores, and supporting telemetry.
        (Placeholder — implementation pending)
      </p>
    </div>
  );
}

export default FaultDiagnosis;
