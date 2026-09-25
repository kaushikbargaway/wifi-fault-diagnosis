import React, { useState } from 'react';
import useDiagnosis from '../hooks/useDiagnosis';
import { generateTelemetry, FAULT_TYPES } from '../utils/telemetrySimulator';

const FIELDS = [
  { key: 'rssi_dbm',            label: 'RSSI (dBm)',          type: 'number', min: -100, max: -20  },
  { key: 'latency_ms',          label: 'Latency (ms)',         type: 'number', min: 0,    max: 5000 },
  { key: 'packet_loss_percent', label: 'Packet Loss (%)',      type: 'number', min: 0,    max: 100  },
  { key: 'temperature_c',       label: 'Temperature (°C)',     type: 'number', min: 0,    max: 120  },
  { key: 'network_load',        label: 'Network Load (%)',     type: 'number', min: 0,    max: 100  },
  { key: 'internet_reachable',  label: 'Internet Reachable',  type: 'bool' },
  { key: 'dns_available',       label: 'DNS Available',        type: 'bool' },
  { key: 'ethernet_connected',  label: 'Ethernet Connected',   type: 'bool' },
];

const DEFAULT_TELEMETRY = {
  device_id: 'manual-input-001',
  rssi_dbm: -60,
  latency_ms: 25,
  packet_loss_percent: 0.5,
  temperature_c: 45,
  network_load: 35,
  internet_reachable: true,
  dns_available: true,
  ethernet_connected: true,
};

function FaultDiagnosis() {
  const { result, loading, error, history, diagnose } = useDiagnosis();
  const [form, setForm] = useState(DEFAULT_TELEMETRY);
  const [preset, setPreset] = useState('normal');

  const loadPreset = (faultType) => {
    setPreset(faultType);
    const t = generateTelemetry(faultType);
    setForm(prev => ({ ...prev, ...t }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    diagnose(form);
  };

  const handleChange = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ marginBottom: '0.25rem' }}>Fault Diagnosis</h1>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
          Submit telemetry data to run AI-based fault classification.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Input Form */}
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.25rem' }}>
          <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '1rem' }}>
            TELEMETRY INPUT
          </h2>

          {/* Presets */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={labelStyle}>Load Preset Scenario</label>
            <select
              value={preset}
              onChange={e => loadPreset(e.target.value)}
              style={selectStyle}
            >
              {FAULT_TYPES.map(f => (
                <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {FIELDS.map(({ key, label, type, min, max }) => (
                <div key={key}>
                  <label style={labelStyle}>{label}</label>
                  {type === 'bool' ? (
                    <select
                      value={form[key] ? 'true' : 'false'}
                      onChange={e => handleChange(key, e.target.value === 'true')}
                      style={selectStyle}
                    >
                      <option value="true">Yes</option>
                      <option value="false">No</option>
                    </select>
                  ) : (
                    <input
                      type="number"
                      value={form[key]}
                      min={min}
                      max={max}
                      step="0.1"
                      onChange={e => handleChange(key, parseFloat(e.target.value))}
                      style={inputStyle}
                    />
                  )}
                </div>
              ))}
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: '1.25rem', width: '100%',
                background: 'var(--color-primary)', color: '#0f172a',
                border: 'none', borderRadius: 6, padding: '0.6rem',
                fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer',
              }}
            >
              {loading ? '⏳ Running Diagnosis...' : '🔍 Run Diagnosis'}
            </button>
          </form>
        </div>

        {/* Result Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {error && (
            <div style={{ background: '#450a0a', border: '1px solid #f87171', borderRadius: 8, padding: '1rem', color: '#f87171' }}>
              ❌ {error}
            </div>
          )}

          {result && (
            <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.25rem' }}>
              <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '1rem' }}>
                DIAGNOSIS RESULT
              </h2>

              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>DETECTED FAULT</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: result.fault_label === 'normal' ? 'var(--color-success)' : 'var(--color-danger)', marginTop: '0.25rem' }}>
                  {result.fault_label.replace(/_/g, ' ').toUpperCase()}
                </div>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--color-muted)' }}>Confidence</span>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div style={{ background: '#334155', borderRadius: 4, height: 8 }}>
                  <div style={{
                    width: `${result.confidence * 100}%`, height: '100%', borderRadius: 4,
                    background: result.confidence > 0.7 ? 'var(--color-success)' : 'var(--color-warning)',
                  }} />
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.5rem' }}>ALL PROBABILITIES</div>
                {Object.entries(result.probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .map(([label, prob]) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                      <span style={{ width: 200, fontSize: '0.75rem', color: label === result.fault_label ? 'var(--color-primary)' : 'var(--color-muted)' }}>
                        {label === result.fault_label ? '▶ ' : '  '}{label.replace(/_/g, ' ')}
                      </span>
                      <div style={{ flex: 1, background: '#334155', borderRadius: 3, height: 6 }}>
                        <div style={{ width: `${prob * 100}%`, height: '100%', borderRadius: 3, background: label === result.fault_label ? 'var(--color-primary)' : '#475569' }} />
                      </div>
                      <span style={{ width: 42, textAlign: 'right', fontSize: '0.75rem', color: 'var(--color-muted)' }}>
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* History */}
          {history.length > 0 && (
            <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.25rem' }}>
              <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>RECENT HISTORY</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {history.slice(0, 8).map((h, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', padding: '0.35rem 0', borderBottom: '1px solid var(--color-border)' }}>
                    <span style={{ color: h.fault_label === 'normal' ? 'var(--color-success)' : 'var(--color-warning)' }}>
                      {h.fault_label.replace(/_/g, ' ')}
                    </span>
                    <span style={{ color: 'var(--color-muted)' }}>{(h.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const labelStyle = { display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.25rem' };
const inputStyle  = { width: '100%', background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.4rem 0.6rem', fontSize: '0.85rem' };
const selectStyle = { ...inputStyle, cursor: 'pointer' };

export default FaultDiagnosis;
