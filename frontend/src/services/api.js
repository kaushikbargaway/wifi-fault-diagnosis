/**
 * Centralised API client.
 * All fetch calls go through this module so that the base URL and
 * default headers are set in one place.
 */

import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10_000,
});

export default apiClient;

// ---------------------------------------------------------------------------
// Endpoint helpers
// ---------------------------------------------------------------------------

export const healthApi = {
  check: () => apiClient.get('/health'),
};

export const telemetryApi = {
  ingest: (payload) => apiClient.post('/telemetry/', payload),
  getLatest: ()       => apiClient.get('/telemetry/latest'),
};

export const diagnosisApi = {
  diagnose: (payload) => apiClient.post('/diagnosis/', payload),
  getHistory: ()       => apiClient.get('/diagnosis/history'),
};

export const recoveryApi = {
  recommend: (payload) => apiClient.post('/recovery/recommend', payload),
};

export const digitalTwinApi = {
  getState:   ()        => apiClient.get('/digital-twin/state'),
  simulate:   (payload) => apiClient.post('/digital-twin/simulate', payload),
};

export const explanationApi = {
  explain: (payload) => apiClient.post('/explanation/', payload),
};
