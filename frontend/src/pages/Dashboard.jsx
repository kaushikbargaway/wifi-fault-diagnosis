import React from 'react';
import StatusCard from '../components/StatusCard';
import useHealth from '../hooks/useHealth';

function Dashboard() {
  const { data: health, loading, error } = useHealth();

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard</h1>

      {loading && <p>Loading system status...</p>}
      {error   && <p style={{ color: 'var(--color-danger)' }}>Backend unreachable</p>}

      {/* Status cards — data will be wired up in the next phase */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        <StatusCard title="Network Status"   value="--"  unit="" />
        <StatusCard title="Fault Status"      value="--"  unit="" />
        <StatusCard title="RSSI"              value="--"  unit="dBm" />
        <StatusCard title="Latency"           value="--"  unit="ms" />
        <StatusCard title="Packet Loss"       value="--"  unit="%" />
        <StatusCard title="Internet"          value="--"  unit="" />
        <StatusCard title="DNS"               value="--"  unit="" />
        <StatusCard title="Ethernet"          value="--"  unit="" />
        <StatusCard title="Temperature"       value="--"  unit="°C" />
        <StatusCard title="Network Load"      value="--"  unit="%" />
      </div>
    </div>
  );
}

export default Dashboard;
