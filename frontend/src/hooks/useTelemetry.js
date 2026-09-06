/**
 * useTelemetry — placeholder hook for fetching the latest telemetry.
 * TODO: Add polling or WebSocket subscription once the backend supports it.
 */

import { useState, useEffect } from 'react';
import { telemetryApi } from '../services/api';

function useTelemetry() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchLatest() {
      try {
        const response = await telemetryApi.getLatest();
        if (!cancelled) setData(response.data);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchLatest();
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}

export default useTelemetry;
