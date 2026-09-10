# Internet Connectivity Failure

## Description
Internet connectivity failure occurs when the local device may remain connected to the Wi-Fi or LAN, but communication with an external Internet endpoint is unavailable.

## Common Symptoms
- Local Wi-Fi association remains active.
- Internet reachability checks fail.
- External services cannot be reached.
- DNS may also fail as a consequence, so DNS status must be interpreted carefully.

## Possible Causes
- WAN or ISP outage.
- Router WAN configuration problem.
- Modem or upstream connection problem.
- Incorrect gateway configuration.
- Upstream routing failure.

## Diagnostic Indicators
Compare local connectivity with external reachability. If the client can communicate with the local network but cannot reach external endpoints, the problem is more likely beyond the local Wi-Fi link.

## Recommended Recovery Actions
1. Check whether other devices have the same Internet reachability problem.
2. Check the router's WAN or upstream connection status.
3. Verify gateway and WAN configuration.
4. Test reachability to an appropriate external endpoint.
5. If the failure is upstream, follow the network or ISP incident procedure.
6. Restart network equipment only when appropriate and permitted by the deployment.

## Verification
Confirm that external connectivity is restored and remains stable across repeated checks.

## Expected Outcome
Restored Internet reachability with stable local network connectivity.
