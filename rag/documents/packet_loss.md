# Packet Loss

## Description
Packet loss occurs when transmitted packets fail to reach their destination. Persistent packet loss can cause retransmissions, unstable connections, poor throughput, and degraded application performance.

## Common Symptoms
- Intermittent connectivity.
- Application timeouts or retries.
- Voice or video interruptions.
- Reduced throughput.
- Increased latency when retransmissions occur.

## Possible Causes
- Weak or unstable Wi-Fi signal.
- Wireless interference.
- Network congestion.
- Faulty cables, connectors, or interfaces.
- Problems along the network path.
- Unstable network equipment.

## Diagnostic Indicators
Packet loss should be measured over repeated probes rather than inferred from a single failed packet. Compare packet loss with RSSI, latency, network load, and connectivity status to distinguish between wireless degradation, congestion, and broader path problems.

## Recommended Recovery Actions
1. Check Wi-Fi signal quality and interference.
2. Check network load for congestion.
3. Inspect physical Ethernet connections when Ethernet is involved.
4. Compare loss to a local endpoint and an external endpoint to isolate the affected segment.
5. Repeat measurements after each corrective action.

## Verification
A successful recovery should reduce packet loss toward the project's normal baseline while maintaining connectivity.

## Expected Outcome
More stable communication, fewer retransmissions, and improved application performance.
