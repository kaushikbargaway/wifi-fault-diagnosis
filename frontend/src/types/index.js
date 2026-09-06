/**
 * Shared type documentation / JSDoc typedefs.
 *
 * These are used for editor IntelliSense. Switch to TypeScript
 * in a later phase if desired.
 */

/**
 * @typedef {Object} Telemetry
 * @property {string}  device_id
 * @property {string}  timestamp
 * @property {number}  rssi_dbm
 * @property {number}  latency_ms
 * @property {number}  packet_loss_percent
 * @property {boolean} internet_reachable
 * @property {boolean} dns_available
 * @property {boolean} ethernet_connected
 * @property {number}  temperature_c
 * @property {number}  network_load
 */

/**
 * @typedef {Object} DiagnosisResult
 * @property {string}          fault_label
 * @property {number}          confidence
 * @property {Object.<string,number>} probabilities
 */

/**
 * @typedef {Object} RecoveryAction
 * @property {string} action
 * @property {string} reason
 * @property {string} expected_result
 * @property {number} priority
 */
