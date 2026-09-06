import React from 'react';

/**
 * Digital Twin page.
 * Will display: network topology, node status, simulation results.
 * TODO: Wire up to GET /api/v1/digital-twin/state and POST /api/v1/digital-twin/simulate
 */
function DigitalTwin() {
  return (
    <div>
      <h1>Digital Twin</h1>
      <p style={{ color: 'var(--color-muted)', marginTop: '0.5rem' }}>
        Displays current Digital Twin state, network components, and simulation outcomes.
        (Placeholder — implementation pending)
      </p>
    </div>
  );
}

export default DigitalTwin;
