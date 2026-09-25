import React, { useState, useEffect, useCallback } from 'react';
import StatusCard from '../components/StatusCard';
import useHealth from '../hooks/useHealth';
import useDiagnosis from '../hooks/useDiagnosis';
import { generateTelemetry, FAULT_TYPES } from '../utils/telemetrySimulator';
import { telemetryApi } from '../services/api';

const FAULT_COLORS = {
  normal: 'ok',
  weak_wifi_signal: 'warning',
  high_latency: 'warning',
  packet_loss: 'warning',
  dns_failure: 'danger',
  internet_connectivity_failure: 'danger',
  ethernet_problem: 'danger',
  router_overheating: 'danger',
  network_congestion: 'warning',
};

function Dashboard() {
  const { data: health, error: healthError } = useHealth();
  const { result: diagnosis, loading: diagnosing, diagnose } = useDiagnosis();

  const [telemetry, setTelemetry]     = useState(null);
  const [selectedFault, setSelectedFault] = useState('normal');
  const [autoRefresh, setAutoRefresh] = useState(false);

  const runSimulation = useCallback(async () => {
    const t = generateTelemetry(selectedFault);
    setTelemetry(t);
    await telemetryApi.ingest(t).catch(() => {});
    await diagnose(t);
  }, [selectedFault, diagnose]);

  // Auto-refresh every 10 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(runSimulation, 10_000);
    return () => clearInterval(id);
  }, [autoRefresh, runSimulation]);

  const t = telemetry;
  const d = diagnosis;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ marginBottom: '0.25rem' }}>TwinNet Dashboard</h1>
          <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
            AI-Powered Network Fault Diagnosis & Recovery System
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            width: 10, height: 10, borderRadius: '50%',
            background: healthError ? 'var(--color-danger)' : 'var(--color-success)',
            display: 'inline-block',
          }} />
          <span style={{ fontSize: '0.8rem', color: 'var(--color-muted)' }}>
            {healthError ? 'Backend offline' : 'Backend online'}
          </span>
        </div>
      </div>

      {/* Simulator Controls */}
      <div style={{
        background: 'var(--color-surface)', border: '1px solid var(--color-border)',
        borderRadius: 8, padding: '1rem', display: 'flex', gap: '1rem',
        alignItems: 'center', flexWrap: 'wrap',
      }}>
        <span style={{ color: 'var(--color-muted)', fontSize: '0.85rem', fontWeight: 600 }}>
          🔬 SIMULATOR
        </span>
        <select
          value={selectedFault}
          onChange={e => setSelectedFault(e.target.value)}
          style={{
            background: 'var(--color-bg)', color: 'var(--color-text)',
            border: '1px solid var(--color-border)', borderRadius: 6,
            padding: '0.4rem 0.75rem', fontSize: '0.85rem', cursor: 'pointer',
          }}
        >
          {FAULT_TYPES.map(f => (
            <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>
          ))}
        </select>

        <button onClick={runSimulation} disabled={diagnosing} style={btnStyle('#38bdf8')}>
          {diagnosing ? '⏳ Running...' : '▶ Run Diagnosis'}
        </button>

        <button
          onClick={() => setAutoRefresh(a => !a)}
          style={btnStyle(autoRefresh ? '#f87171' : '#4ade80')}
        >
          {autoRefresh ? '⏹ Stop Auto' : '🔄 Auto Refresh'}
        </button>
      </div>

      {/* Fault Banner */}
      {d && (
        <div style={{
          background: 'var(--color-surface)', border: `1px solid var(--color-border)`,
          borderLeft: `4px solid ${d.fault_label === 'normal' ? '#4ade80' : '#f87171'}`,
          borderRadius: 8, padding: '1rem 1.25rem',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexWrap: 'wrap', gap: '0.5rem',
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.2rem' }}>
              DETECTED FAULT
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}>
              {d.fault_label.replace(/_/g, ' ')}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.2rem' }}>
              CONFIDENCE
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary)' }}>
              {(d.confidence * 100).toFixed(1)}%
            </div>
          </div>
          {/* Confidence bar */}
          <div style={{ width: '100%', background: '#334155', borderRadius: 4, height: 6 }}>
            <div style={{
              width: `${d.confidence * 100}%`,
              height: '100%', borderRadius: 4,
              background: d.fault_label === 'normal' ? '#4ade80' : '#f87171',
              transition: 'width 0.5s ease',
            }} />
          </div>
        </div>
      )}

      {/* Telemetry Status Cards */}
      <div>
        <h2 style={{ fontSize: '1rem', marginBottom: '0.75rem', color: 'var(--color-muted)' }}>
          NETWORK TELEMETRY
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '0.75rem' }}>
          <StatusCard title="RSSI"          value={t ? t.rssi_dbm.toFixed(1)              : '--'} unit="dBm" status={t ? rssiStatus(t.rssi_dbm)             : 'unknown'} />
          <StatusCard title="Latency"       value={t ? t.latency_ms.toFixed(1)            : '--'} unit="ms"  status={t ? latencyStatus(t.latency_ms)        : 'unknown'} />
          <StatusCard title="Packet Loss"   value={t ? t.packet_loss_percent.toFixed(1)   : '--'} unit="%"   status={t ? lossStatus(t.packet_loss_percent)  : 'unknown'} />
          <StatusCard title="Temperature"   value={t ? t.temperature_c.toFixed(1)         : '--'} unit="°C"  status={t ? tempStatus(t.temperature_c)        : 'unknown'} />
          <StatusCard title="Network Load"  value={t ? t.network_load.toFixed(1)          : '--'} unit="%"   status={t ? loadStatus(t.network_load)         : 'unknown'} />
          <StatusCard title="Internet"      value={t ? (t.internet_reachable ? 'UP' : 'DOWN') : '--'} unit="" status={t ? (t.internet_reachable ? 'ok' : 'danger') : 'unknown'} />
          <StatusCard title="DNS"           value={t ? (t.dns_available      ? 'OK' : 'FAIL') : '--'} unit="" status={t ? (t.dns_available ? 'ok' : 'danger')       : 'unknown'} />
          <StatusCard title="Ethernet"      value={t ? (t.ethernet_connected ? 'UP' : 'DOWN') : '--'} unit="" status={t ? (t.ethernet_connected ? 'ok' : 'warning') : 'unknown'} />
        </div>
      </div>

      {/* Probability Breakdown */}
      {d && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem' }}>
          <h2 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--color-muted)' }}>
            FAULT PROBABILITY BREAKDOWN
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {Object.entries(d.probabilities)
              .sort(([, a], [, b]) => b - a)
              .map(([label, prob]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ width: 220, fontSize: '0.8rem', color: label === d.fault_label ? 'var(--color-primary)' : 'var(--color-muted)' }}>
                    {label === d.fault_label ? '▶ ' : '  '}{label.replace(/_/g, ' ')}
                  </span>
                  <div style={{ flex: 1, background: '#334155', borderRadius: 4, height: 8 }}>
                    <div style={{
                      width: `${prob * 100}%`, height: '100%', borderRadius: 4,
                      background: label === d.fault_label ? 'var(--color-primary)' : '#475569',
                      transition: 'width 0.4s ease',
                    }} />
                  </div>
                  <span style={{ width: 50, textAlign: 'right', fontSize: '0.8rem', color: 'var(--color-muted)' }}>
                    {(prob * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

    </div>
  );
}

// Status helpers
const rssiStatus    = v => v >= -65 ? 'ok' : v >= -75 ? 'warning' : 'danger';
const latencyStatus = v => v <= 50  ? 'ok' : v <= 150  ? 'warning' : 'danger';
const lossStatus    = v => v <= 1   ? 'ok' : v <= 10   ? 'warning' : 'danger';
const tempStatus    = v => v <= 60  ? 'ok' : v <= 75   ? 'warning' : 'danger';
const loadStatus    = v => v <= 60  ? 'ok' : v <= 80   ? 'warning' : 'danger';

const btnStyle = color => ({
  background: 'transparent', border: `1px solid ${color}`,
  color, borderRadius: 6, padding: '0.4rem 1rem',
  fontSize: '0.85rem', cursor: 'pointer', fontWeight: 600,
});

export default Dashboard;
