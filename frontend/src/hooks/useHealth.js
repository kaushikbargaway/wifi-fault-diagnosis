/**
 * useHealth — polls the backend health endpoint.
 * Returns { data, loading, error }.
 */

import { useState, useEffect } from 'react';
import { healthApi } from '../services/api';

function useHealth() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchHealth() {
      try {
        const response = await healthApi.check();
        if (!cancelled) setData(response.data);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchHealth();
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}

export default useHealth;
