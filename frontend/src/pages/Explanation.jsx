import React, { useState } from 'react';
import { explanationApi } from '../services/api';
import { generateTelemetry, FAULT_TYPES } from '../utils/telemetrySimulator';
import useDiagnosis from '../hooks/useDiagnosis';

function Explanation() {
  const { result: diagnosis, loading: diagnosing, diagnose } = useDiagnosis();
  const [explanation, setExplanation]   = useState(null);
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState(null);
  const [selectedFault, setSelectedFault] = useState('dns_failure');

  const run = async () => {
    const t = generateTelemetry(selectedFault);
    const diag = await diagnose(t);
    if (!diag) return;

    setLoading(true);
    setError(null);
    try {
      const res = await explanationApi.explain(diag);
      setExplanation(res.data);
    } catch (e) {
      // explanation service returns placeholder text — show it anyway
      if (e?.response?.data) {
        setExplanation(e.response.data);
      } else {
        setError('Explanation service not yet connected to LLM. This will be implemented in Month 6.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ marginBottom: '0.25rem' }}>AI Explanation</h1>
        <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>
          RAG-powered explanation of detected faults. The LLM retrieves relevant technical evidence and explains the diagnosis in plain language.
        </p>
      </div>

      {/* Status Banner */}
      <div style={{ background: '#1c1917', border: '1px solid #78350f', borderRadius: 8, padding: '0.75rem 1rem', fontSize: '0.8rem', color: '#fbbf24' }}>
        ⚠️ <strong>Implementation Status:</strong> RAG retrieval pipeline is complete (FAISS + sentence-transformers).
        LLM generator (Ollama/OpenAI) is planned for Month 6. Explanation structure shown below is the target output format.
      </div>

      {/* Controls */}
      <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <select
          value={selectedFault}
          onChange={e => setSelectedFault(e.target.value)}
          style={{ background: 'var(--color-bg)', color: 'var(--color-text)', border: '1px solid var(--color-border)', borderRadius: 6, padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
        >
          {FAULT_TYPES.map(f => <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>)}
        </select>

        <button
          onClick={run}
          disabled={diagnosing || loading}
          style={{ background: '#7c3aed', color: '#fff', border: 'none', borderRadius: 6, padding: '0.45rem 1.25rem', fontWeight: 700, cursor: 'pointer' }}
        >
          {diagnosing || loading ? '⏳ Processing...' : '🤖 Generate Explanation'}
        </button>
      </div>

      {/* Diagnosis used */}
      {diagnosis && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1rem', display: 'flex', gap: '2rem' }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>FAULT</div>
            <div style={{ fontWeight: 700, marginTop: '0.2rem' }}>{diagnosis.fault_label.replace(/_/g, ' ').toUpperCase()}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>CONFIDENCE</div>
            <div style={{ fontWeight: 700, color: 'var(--color-primary)', marginTop: '0.2rem' }}>{(diagnosis.confidence * 100).toFixed(1)}%</div>
          </div>
        </div>
      )}

      {error && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.5rem' }}>
          <div style={{ color: '#facc15', marginBottom: '1rem', fontWeight: 600 }}>📋 LLM Not Connected — Target Output Format:</div>
          <ExplanationTemplate fault={selectedFault} diagnosis={diagnosis} />
        </div>
      )}

      {explanation && (
        <div style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 8, padding: '1.5rem' }}>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', color: 'var(--color-text)', fontFamily: 'monospace' }}>
            {JSON.stringify(explanation, null, 2)}
          </pre>
        </div>
      )}

      {!diagnosis && !loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
          Select a fault scenario and click "Generate Explanation" to see the AI explanation pipeline.
        </div>
      )}
    </div>
  );
}

function ExplanationTemplate({ fault, diagnosis }) {
  const template = {
    diagnosis: `${(fault || 'unknown').replace(/_/g, ' ')} detected with ${diagnosis ? (diagnosis.confidence * 100).toFixed(1) : '--'}% confidence`,
    evidence: [
      'Telemetry values exceed normal thresholds for this fault class',
      'Random Forest model trained on 2050 labelled network samples',
      'RAG knowledge base retrieved relevant documentation chunks',
    ],
    recommended_action: 'See Recovery Recommendation page for ranked actions',
    reason: 'Top-ranked action has highest predicted success probability based on fault signature',
    alternatives: ['Secondary recovery action', 'Manual diagnostic procedure'],
    risks: ['Possible brief service interruption during recovery', 'Action effectiveness depends on root cause'],
    requires_approval: true,
    note: 'LLM explanation generator (Ollama/OpenAI) will be integrated in Month 6 of the project timeline.',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
      {Object.entries(template).map(([key, val]) => (
        <div key={key} style={{ display: 'flex', gap: '1rem' }}>
          <span style={{ width: 180, color: 'var(--color-primary)', fontWeight: 600, flexShrink: 0 }}>{key}</span>
          <span style={{ color: 'var(--color-muted)' }}>
            {Array.isArray(val) ? val.map((v, i) => <div key={i}>• {v}</div>) : String(val)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default Explanation;
