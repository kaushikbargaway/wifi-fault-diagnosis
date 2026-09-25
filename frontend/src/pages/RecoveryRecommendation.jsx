import React, { useState } from 'react';
import useDiagnosis from '../hooks/useDiagnosis';
import { recoveryApi } from '../services/api';
import { generateTelemetry, FAULT_TYPES } from '../utils/telemetrySimulator';

const RISK_COLORS = { low: '#4ade80', medium: '#facc15', high: '#f87171' };
const PRIORITY_LABELS = { 1: '🔴 HIGH', 2: '🟡 MEDIUM', 3: '🟢 LOW' };

function RecoveryRecommendation() {
  const { result: diagnosis, loading: diagnosing, diagnose } = useDiagnosis();
  const [recovery, setRecovery]     = useState(null);
  const [loadingRec, setLoadingRec] = useState(false);
  const [selectedFault, setSelectedFault] = useState('weak_wifi_signal');
  const [approved, setApproved]     = useState({});

  const runFull = async () => {
    const t = generateTelemetry(selectedFault);
    const diag = await diagnose(t);
    if (!diag) return;

    setLoadingRec(true);
    try {
      const res = await recoveryApi.recommend({ diagnosis: diag });
      setRecovery(res.data);
      setApproved({});
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingRec(false);
    }
  };

  const toggleApprove = (idx) => {
    setApproved(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ marginBottom: '0.25rem' }}>Recovery Recommendation</h1>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
          AI-ranked recovery actions for the detected fault. Administrator approval required before execution.
        </p>
      </div>

      {/* Controls */}
      <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <select
          value={selectedFault}
          onChange={e => setSelectedFault(e.target.value)}
          style={{ background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
        >
          {FAULT_TYPES.map(f => <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>)}
        </select>

        <button
          onClick={runFull}
          disabled={diagnosing || loadingRec}
          style={{ background: 'var(--color-primary)', color: '#0f172a', border: 'none', borderRadius: 6, padding: '0.45rem 1.25rem', fontWeight: 700, cursor: 'pointer' }}
        >
          {diagnosing || loadingRec ? '⏳ Loading...' : '▶ Get Recommendations'}
        </button>
      </div>

      {/* Diagnosis Summary */}
      {diagnosis && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderLeft: `4px solid ${diagnosis.fault_label === 'normal' ? '#4ade80' : '#f87171'}`, borderRadius: 8, padding: '1rem 1.25rem', display: 'flex', gap: '2rem' }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>DIAGNOSED FAULT</div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem', marginTop: '0.2rem' }}>{diagnosis.fault_label.replace(/_/g, ' ').toUpperCase()}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>CONFIDENCE</div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--color-primary)', marginTop: '0.2rem' }}>{(diagnosis.confidence * 100).toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Recovery Actions */}
      {recovery && (
        <div>
          <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>
            RECOMMENDED ACTIONS — {recovery.fault_label.replace(/_/g, ' ').toUpperCase()}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recovery.actions.map((action, idx) => (
              <div key={idx} style={{
                background: 'var(--color-surface)',
                border: `1px solid ${approved[idx] ? '#4ade80' : 'var(--color-border)'}`,
                borderRadius: 8, padding: '1.1rem',
                transition: 'border-color 0.3s',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem' }}>
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--color-muted)' }}>
                      {PRIORITY_LABELS[action.priority] || `P${action.priority}`}
                    </span>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{action.action}</span>
                  </div>
                  <button
                    onClick={() => toggleApprove(idx)}
                    style={{
                      background: approved[idx] ? '#166534' : 'transparent',
                      border: `1px solid ${approved[idx] ? '#4ade80' : 'var(--color-border)'}`,
                      color: approved[idx] ? '#4ade80' : 'var(--color-muted)',
                      borderRadius: 6, padding: '0.3rem 0.8rem',
                      fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600,
                    }}
                  >
                    {approved[idx] ? '✓ Approved' : 'Approve'}
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
                  <div>
                    <span style={{ color: 'var(--color-muted)' }}>Reason: </span>
                    <span>{action.reason}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-muted)' }}>Expected: </span>
                    <span style={{ color: 'var(--color-success)' }}>{action.expected_result}</span>
                  </div>
                </div>

                {approved[idx] && (
                  <div style={{ marginTop: '0.75rem', background: '#052e16', border: '1px solid #166534', borderRadius: 6, padding: '0.5rem 0.75rem', fontSize: '0.8rem', color: '#4ade80' }}>
                    ⚠️ Administrator approved — ready for manual execution. This system does not execute actions automatically.
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!recovery && !diagnosing && !loadingRec && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
          Select a fault scenario and click "Get Recommendations" to see recovery actions.
        </div>
      )}
    </div>
  );
}

export default RecoveryRecommendation;
