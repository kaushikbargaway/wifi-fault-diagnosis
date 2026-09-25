import React, { useState, useEffect } from 'react';
import { digitalTwinApi } from '../services/api';

const STATUS_COLOR = { up: '#4ade80', down: '#f87171', degraded: '#facc15', unknown: '#94a3b8' };
const STATUS_DOT   = status => (
  <span style={{ width: 10, height: 10, borderRadius: '50%', background: STATUS_COLOR[status] || '#94a3b8', display: 'inline-block', marginRight: 6 }} />
);

const NODE_ICONS = {
  router:     '🌐',
  server:     '🖥️',
  iot_sensor: '📡',
  client:     '💻',
};

function DigitalTwin() {
  const [state, setState]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [simAction, setSimAction]   = useState('restart_dns');

  const RECOVERY_ACTIONS = [
    'restart_dns',
    'restart_network_manager',
    'clear_arp_cache',
    'restart_apache',
    'change_dns_server',
    'reboot_router',
  ];

  const fetchState = async () => {
    setLoading(true);
    try {
      const res = await digitalTwinApi.getState();
      setState(res.data);
      setError(null);
    } catch (e) {
      setError('Failed to load Digital Twin state');
    } finally {
      setLoading(false);
    }
  };

  const simulate = async () => {
    setSimLoading(true);
    setSimResult(null);
    try {
      const res = await digitalTwinApi.simulate({ action: simAction, target_node: 'vm1', parameters: {} });
      setSimResult(res.data);
    } catch (e) {
      setSimResult({ error: 'Simulation failed' });
    } finally {
      setSimLoading(false);
    }
  };

  useEffect(() => { fetchState(); }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ marginBottom: '0.25rem' }}>Digital Twin</h1>
          <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
            Virtual representation of the network topology. Simulates recovery actions before real execution.
          </p>
        </div>
        <button onClick={fetchState} style={{ background: 'transparent', border: '1px solid var(--color-border)', color: 'var(--color-muted)', borderRadius: 6, padding: '0.4rem 0.8rem', cursor: 'pointer', fontSize: '0.8rem' }}>
          🔄 Refresh
        </button>
      </div>

      {loading && <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-muted)' }}>Loading twin state...</div>}
      {error   && <div style={{ background: '#450a0a', border: '1px solid #f87171', borderRadius: 8, padding: '1rem', color: '#f87171' }}>❌ {error}</div>}

      {state && (
        <>
          {/* Overall Health */}
          <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem 1.25rem', display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>OVERALL HEALTH</div>
              <div style={{ display: 'flex', alignItems: 'center', marginTop: '0.25rem' }}>
                {STATUS_DOT(state.overall_health)}
                <span style={{ fontWeight: 700, fontSize: '1.1rem', color: STATUS_COLOR[state.overall_health] }}>
                  {state.overall_health.toUpperCase()}
                </span>
              </div>
            </div>
            {state.fault_label && (
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>MIRRORED FAULT</div>
                <div style={{ fontWeight: 600, color: '#f87171', marginTop: '0.25rem' }}>{state.fault_label}</div>
              </div>
            )}
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>NODES</div>
              <div style={{ fontWeight: 600, marginTop: '0.25rem' }}>{state.nodes.length}</div>
            </div>
            <div style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--color-muted)' }}>
              {state.last_synced ? `Last sync: ${new Date(state.last_synced).toLocaleTimeString()}` : 'Not yet synced with VMs'}
            </div>
          </div>

          {/* Network Topology */}
          <div>
            <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>NETWORK TOPOLOGY</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem' }}>
              {state.nodes.map(node => (
                <div key={node.node_id} style={{
                  background: 'var(--color-surface)', border: `1px solid ${STATUS_COLOR[node.status] || 'var(--color-border)'}`,
                  borderRadius: 8, padding: '1rem',
                }}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                    {NODE_ICONS[node.node_type] || '📦'}
                  </div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{node.node_id}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.5rem' }}>{node.node_type}</div>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    {STATUS_DOT(node.status)}
                    <span style={{ fontSize: '0.8rem', color: STATUS_COLOR[node.status] }}>{node.status}</span>
                  </div>
                  {Object.keys(node.metrics).length > 0 && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--color-muted)' }}>
                      {Object.entries(node.metrics).map(([k, v]) => (
                        <div key={k}>{k}: {String(v)}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recovery Simulation */}
          <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.25rem' }}>
            <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '1rem' }}>
              WHAT-IF RECOVERY SIMULATION
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-muted)', marginBottom: '1rem' }}>
              Simulate a recovery action against the Digital Twin before applying it to the real network.
            </p>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <select
                value={simAction}
                onChange={e => setSimAction(e.target.value)}
                style={{ background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
              >
                {RECOVERY_ACTIONS.map(a => <option key={a} value={a}>{a.replace(/_/g, ' ')}</option>)}
              </select>
              <button
                onClick={simulate}
                disabled={simLoading}
                style={{ background: '#7c3aed', color: '#fff', border: 'none', borderRadius: 6, padding: '0.45rem 1.25rem', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
              >
                {simLoading ? '⏳ Simulating...' : '⚡ Simulate Action'}
              </button>
            </div>

            {simResult && (
              <div style={{ marginTop: '1rem', background: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '1rem', fontSize: '0.85rem' }}>
                {simResult.error ? (
                  <span style={{ color: '#f87171' }}>❌ {simResult.error}</span>
                ) : (
                  <>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <span style={{ color: 'var(--color-muted)' }}>Action: </span>
                      <span style={{ fontWeight: 600 }}>{simResult.action}</span>
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <span style={{ color: 'var(--color-muted)' }}>Improvement Score: </span>
                      <span style={{ color: simResult.improvement_score > 0 ? '#4ade80' : '#94a3b8', fontWeight: 600 }}>
                        {simResult.improvement_score.toFixed(2)}
                      </span>
                    </div>
                    {simResult.notes && (
                      <div style={{ color: 'var(--color-muted)', fontStyle: 'italic' }}>{simResult.notes}</div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default DigitalTwin;
