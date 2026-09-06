import React from 'react';
import styles from './StatusCard.module.css';

/**
 * A simple card component that displays a metric value.
 * Props:
 *   title  — label shown above the value
 *   value  — the metric value (string or number)
 *   unit   — unit suffix (e.g. 'dBm', 'ms', '%')
 *   status — 'ok' | 'warning' | 'danger' | 'unknown' (controls accent colour)
 */
function StatusCard({ title, value, unit = '', status = 'unknown' }) {
  return (
    <div className={`${styles.card} ${styles[status]}`}>
      <span className={styles.title}>{title}</span>
      <span className={styles.value}>
        {value}
        {unit && <span className={styles.unit}> {unit}</span>}
      </span>
    </div>
  );
}

export default StatusCard;
