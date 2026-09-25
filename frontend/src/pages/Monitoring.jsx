import React, { useState, useEffect, useCallback, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { generateTelemetry, FAULT_TYPES } from '../utils/telemetrySimulator';
import { telemetryApi } from '../services/api';

const MAX_POINTS = 30;

function Monitoring() {
  const [history, setHistory]       = useState([]);
  const [running, setRunning]       = useState(false);
  const [interval_, setInterval_]   = useState(3);
  const [faultMix, setFaultMix]     = useState('normal');
  const intervalRef                 = useRef(null);
  const counter                     = useRef(0);

  const tick = useCallback(async () => {
    const t = generateTelemetry(faultMix);
    await telemetryApi.ingest(t).catch(() => {});
    counter.current += 1;
    const point = {
      t: new Date().toLocaleTimeString(),
      n: counter.current,
      latency: t.latency_ms,
      loss: t.packet_loss_percent,
      load: t.network_load,
      rssi: Math.abs(t.rssi_dbm),   // plot as positive
      temp: t.temperature_c,
    };
    setHistory(prev => [...prev.slice(-(MAX_POINTS - 1)), point]);
  }, [faultMix]);

  const start = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setRunning(true);
    tick(); // immediate first tick
    intervalRef.current = setInterval(tick, interval_ * 1000);
  }, [tick, interval_]);

  const stop = useCallback(() => {
    clearInterval(intervalRef.current);
    setRunning(false);
  }, []);

  useEffect(() => {
    if (running) start();
  }, [faultMix]);

  useEffect(() => () => clearInterval(intervalRef.current), []);

  const latest = history[history.length - 1];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ marginBottom: '0.25rem' }}>Network Monitoring</h1>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
          Live telemetry feed with real-time charts. Uses simulated data — replace with ESP32 when hardware is ready.
        </p>
      </div>

      {/* Controls */}
      <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--color-muted)', display: 'block', marginBottom: '0.2rem' }}>Scenario</label>
          <select
            value={faultMix}
            onChange={e => setFaultMix(e.target.value)}
            style={{ background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
          >
            {FAULT_TYPES.map(f => <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>)}
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--color-muted)', display: 'block', marginBottom: '0.2rem' }}>Interval (s)</label>
          <select
            value={interval_}
            onChange={e => setInterval_(Number(e.target.value))}
            style={{ background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
          >
            {[2, 3, 5, 10].map(v => <option key={v} value={v}>{v}s</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignSelf: 'flex-end' }}>
          {!running ? (
            <button onClick={start} style={{ background: '#4ade80', color: '#052e16', border: 'none', borderRadius: 6, padding: '0.4rem 1.1rem', fontWeight: 700, cursor: 'pointer' }}>
              ▶ Start
            </button>
          ) : (
            <button onClick={stop} style={{ background: '#f87171', color: '#450a0a', border: 'none', borderRadius: 6, padding: '0.4rem 1.1rem', fontWeight: 700, cursor: 'pointer' }}>
              ⏹ Stop
            </button>
          )}
          <button
            onClick={() => setHistory([])}
            style={{ background: 'transparent', border: '1px solid var(--color-border)', color: 'var(--color-muted)', borderRadius: 6, padding: '0.4rem 0.9rem', cursor: 'pointer', fontSize: '0.8rem' }}
          >
            Clear
          </button>
        </div>

        {running && (
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4ade80', display: 'inline-block', animation: 'pulse 1s infinite' }} />
            <span style={{ fontSize: '0.8rem', color: '#4ade80' }}>LIVE — {history.length} readings</span>
          </div>
        )}
      </div>

      {/* Live Metrics */}
      {latest && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' }}>
          {[
            { label: 'Latency',      value: latest.latency.toFixed(1),  unit: 'ms',  warn: 150, danger: 300 },
            { label: 'Packet Loss',  value: latest.loss.toFixed(1),     unit: '%',   warn: 5,   danger: 15  },
            { label: 'Network Load', value: latest.load.toFixed(1),     unit: '%',   warn: 70,  danger: 90  },
            { label: 'RSSI (abs)',   value: latest.rssi.toFixed(1),     unit: 'dBm', warn: 70,  danger: 85  },
            { label: 'Temperature',  value: latest.temp.toFixed(1),     unit: '°C',  warn: 65,  danger: 80  },
          ].map(({ label, value, unit, warn, danger }) => {
            const n = parseFloat(value);
            const color = n >= danger ? '#f87171' : n >= warn ? '#facc15' : '#4ade80';
            return (
              <div key={label} style={{ background: 'var(--color-surface)', border: `1px solid ${color}33`, borderRadius: 8, padding: '0.85rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)', marginBottom: '0.3rem' }}>{label}</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color }}>{value}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>{unit}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Charts */}
      {history.length > 1 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <ChartPanel title="Latency (ms)" data={history} dataKey="latency" color="#38bdf8" domain={[0, 500]} />
          <ChartPanel title="Packet Loss (%)" data={history} dataKey="loss"    color="#f87171" domain={[0, 50]}  />
          <ChartPanel title="Network Load (%)" data={history} dataKey="load"   color="#facc15" domain={[0, 100]} />
        </div>
      )}

      {/* Recent Readings Table */}
      {history.length > 0 && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem', overflowX: 'auto' }}>
          <h2 style={{ fontSize: '0.9rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>RECENT READINGS</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
            <thead>
              <tr style={{ color: 'var(--color-muted)', textAlign: 'left' }}>
                {['#', 'Time', 'Latency (ms)', 'Loss (%)', 'Load (%)', 'RSSI (dBm)', 'Temp (°C)'].map(h => (
                  <th key={h} style={{ padding: '0.4rem 0.6rem', borderBottom: '1px solid var(--color-border)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...history].reverse().slice(0, 15).map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '0.4rem 0.6rem', color: 'var(--color-muted)' }}>{row.n}</td>
                  <td style={{ padding: '0.4rem 0.6rem' }}>{row.t}</td>
                  <td style={{ padding: '0.4rem 0.6rem', color: row.latency > 300 ? '#f87171' : row.latency > 150 ? '#facc15' : '#4ade80' }}>{row.latency.toFixed(1)}</td>
                  <td style={{ padding: '0.4rem 0.6rem', color: row.loss > 15 ? '#f87171' : row.loss > 5 ? '#facc15' : '#4ade80' }}>{row.loss.toFixed(1)}</td>
                  <td style={{ padding: '0.4rem 0.6rem', color: row.load > 90 ? '#f87171' : row.load > 70 ? '#facc15' : '#4ade80' }}>{row.load.toFixed(1)}</td>
                  <td style={{ padding: '0.4rem 0.6rem' }}>{(-row.rssi).toFixed(1)}</td>
                  <td style={{ padding: '0.4rem 0.6rem', color: row.temp > 80 ? '#f87171' : row.temp > 65 ? '#facc15' : '#4ade80' }}>{row.temp.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {history.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-muted)' }}>
          Press ▶ Start to begin collecting telemetry data.
        </div>
      )}
    </div>
  );
}

function ChartPanel({ title, data, dataKey, color, domain }) {
  return (
    <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem' }}>
      <h3 style={{ fontSize: '0.85rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>{title}</h3>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="t" tick={{ fontSize: 10, fill: '#94a3b8' }} interval="preserveStartEnd" />
          <YAxis domain={domain} tick={{ fontSize: 10, fill: '#94a3b8' }} />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 6, fontSize: '0.8rem' }}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Monitoring;
