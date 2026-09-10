# High Latency

## Description
High latency occurs when network packets require an unusually long time to complete a round trip. It can degrade interactive applications such as video calls, gaming, remote desktops, and real-time services.

## Common Symptoms
- Increased round-trip time.
- Slow response from network services.
- Noticeable delay in interactive applications.
- Latency that remains elevated across repeated measurements.

## Possible Causes
- Network congestion.
- Poor wireless link quality.
- Long or inefficient network paths.
- Routing or upstream network problems.
- Processing or queueing delays in network equipment.

## Diagnostic Indicators
Latency should be compared with the project's normal baseline. High latency accompanied by high network load can indicate congestion. High latency accompanied by packet loss may indicate link degradation or path problems. High latency with healthy local Wi-Fi may point to an upstream or Internet-path issue.

## Recommended Recovery Actions
1. Check network load and identify heavy traffic.
2. Compare latency to a local endpoint and an external endpoint when possible.
3. Check Wi-Fi signal quality and packet loss.
4. Inspect the network path for abnormal delay.
5. Re-test after reducing congestion or correcting the suspected link/path issue.

## Verification
A successful recovery should produce a sustained reduction in round-trip latency without introducing additional packet loss.

## Expected Outcome
Lower and more stable latency.
