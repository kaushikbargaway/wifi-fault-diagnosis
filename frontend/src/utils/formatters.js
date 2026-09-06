/**
 * Display formatting utilities.
 */

/**
 * Format RSSI in dBm with a signal quality label.
 * @param {number} rssi
 * @returns {{ label: string, quality: string }}
 */
export function formatRssi(rssi) {
  if (rssi === null || rssi === undefined) return { label: '--', quality: 'unknown' };
  const label = `${rssi} dBm`;
  if (rssi >= -50)  return { label, quality: 'excellent' };
  if (rssi >= -60)  return { label, quality: 'good' };
  if (rssi >= -70)  return { label, quality: 'fair' };
  if (rssi >= -80)  return { label, quality: 'weak' };
  return { label, quality: 'very_weak' };
}

/**
 * Format a fault label into a human-readable string.
 * @param {string} label
 * @returns {string}
 */
export function formatFaultLabel(label) {
  if (!label) return 'Unknown';
  return label
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Format a confidence score as a percentage string.
 * @param {number} confidence  0-1
 * @returns {string}
 */
export function formatConfidence(confidence) {
  if (confidence === null || confidence === undefined) return '--';
  return `${(confidence * 100).toFixed(1)}%`;
}
