/**
 * useDiagnosis — runs fault diagnosis and stores the latest result.
 */
import { useState, useCallback } from 'react';
import { diagnosisApi } from '../services/api';

function useDiagnosis() {
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [history, setHistory] = useState([]);

  const diagnose = useCallback(async (telemetry) => {
    setLoading(true);
    setError(null);
    try {
      const res = await diagnosisApi.diagnose({ telemetry });
      setResult(res.data);
      setHistory(prev => [res.data, ...prev].slice(0, 20));
      return res.data;
    } catch (err) {
      setError(err?.response?.data?.detail || 'Diagnosis failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, history, diagnose };
}

export default useDiagnosis;
