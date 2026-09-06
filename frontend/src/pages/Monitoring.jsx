import React from 'react';

/**
 * Monitoring page.
 * Will display: time-series telemetry charts, fault history, system events.
 * TODO: Wire up to telemetry and diagnosis history endpoints
 */
function Monitoring() {
  return (
    <div>
      <h1>Monitoring</h1>
      <p style={{ color: 'var(--color-muted)', marginTop: '0.5rem' }}>
        Time-series telemetry, fault history, and system event log.
        (Placeholder — implementation pending)
      </p>
    </div>
  );
}

export default Monitoring;
