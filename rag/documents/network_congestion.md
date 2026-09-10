# Network Congestion

## Description
Network congestion occurs when offered traffic approaches or exceeds the capacity of a network link or device, causing queues, increased latency, packet loss, or reduced throughput.

## Common Symptoms
- High network load.
- Increasing latency during periods of heavy traffic.
- Packet loss or retransmissions under load.
- Reduced throughput for applications sharing the congested link.

## Possible Causes
- Multiple high-bandwidth clients using the same link.
- Large downloads or uploads.
- Streaming or backup traffic.
- Insufficient link capacity for the workload.
- Poor traffic prioritization.

## Diagnostic Indicators
Congestion is more strongly supported when latency and/or packet loss increase as network load increases and improve when the load is reduced. This relationship is useful for distinguishing congestion from a persistent physical link fault.

## Recommended Recovery Actions
1. Identify high-bandwidth processes or clients.
2. Reduce or schedule non-critical traffic.
3. Use Quality of Service (QoS) where supported and appropriate.
4. Prioritize latency-sensitive traffic according to the network policy.
5. Re-measure latency, packet loss, and network load after the intervention.

## Verification
A successful recovery should reduce queueing delay and packet loss while improving the performance of priority traffic.

## Expected Outcome
Lower latency, lower packet loss, and more predictable network performance under load.
