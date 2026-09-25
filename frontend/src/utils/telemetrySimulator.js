/**
 * Telemetry simulator — generates realistic synthetic telemetry for each fault type.
 * Used for development/demo when ESP32 is not available.
 */

const FAULT_PROFILES = {
  normal: {
    rssi_dbm: () => rand(-55, -45),
    latency_ms: () => rand(15, 30),
    packet_loss_percent: () => rand(0, 0.5),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: true,
    temperature_c: () => rand(40, 50),
    network_load: () => rand(20, 40),
  },
  weak_wifi_signal: {
    rssi_dbm: () => rand(-90, -78),
    latency_ms: () => rand(60, 120),
    packet_loss_percent: () => rand(5, 15),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: false,
    temperature_c: () => rand(44, 52),
    network_load: () => rand(30, 55),
  },
  high_latency: {
    rssi_dbm: () => rand(-65, -55),
    latency_ms: () => rand(280, 500),
    packet_loss_percent: () => rand(1, 4),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: true,
    temperature_c: () => rand(48, 58),
    network_load: () => rand(70, 90),
  },
  packet_loss: {
    rssi_dbm: () => rand(-72, -60),
    latency_ms: () => rand(40, 80),
    packet_loss_percent: () => rand(18, 35),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: false,
    temperature_c: () => rand(45, 52),
    network_load: () => rand(45, 70),
  },
  dns_failure: {
    rssi_dbm: () => rand(-60, -50),
    latency_ms: () => rand(18, 30),
    packet_loss_percent: () => rand(0, 1),
    internet_reachable: false,
    dns_available: false,
    ethernet_connected: true,
    temperature_c: () => rand(44, 50),
    network_load: () => rand(25, 40),
  },
  internet_connectivity_failure: {
    rssi_dbm: () => rand(-62, -52),
    latency_ms: () => rand(14, 22),
    packet_loss_percent: () => rand(0, 1.5),
    internet_reachable: false,
    dns_available: false,
    ethernet_connected: true,
    temperature_c: () => rand(44, 50),
    network_load: () => rand(10, 25),
  },
  ethernet_problem: {
    rssi_dbm: () => rand(-78, -65),
    latency_ms: () => rand(70, 130),
    packet_loss_percent: () => rand(8, 18),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: false,
    temperature_c: () => rand(46, 54),
    network_load: () => rand(40, 65),
  },
  router_overheating: {
    rssi_dbm: () => rand(-68, -58),
    latency_ms: () => rand(120, 250),
    packet_loss_percent: () => rand(10, 20),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: true,
    temperature_c: () => rand(80, 95),
    network_load: () => rand(55, 75),
  },
  network_congestion: {
    rssi_dbm: () => rand(-62, -52),
    latency_ms: () => rand(220, 400),
    packet_loss_percent: () => rand(12, 22),
    internet_reachable: true,
    dns_available: true,
    ethernet_connected: true,
    temperature_c: () => rand(50, 60),
    network_load: () => rand(88, 99),
  },
};

function rand(min, max) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(2));
}

export function generateTelemetry(faultType = 'normal') {
  const profile = FAULT_PROFILES[faultType] || FAULT_PROFILES.normal;
  const result = { device_id: 'simulator-001' };
  for (const [key, val] of Object.entries(profile)) {
    result[key] = typeof val === 'function' ? val() : val;
  }
  return result;
}

export const FAULT_TYPES = Object.keys(FAULT_PROFILES);
