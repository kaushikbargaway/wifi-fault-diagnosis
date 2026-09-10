# Ethernet Problem

## Description
An Ethernet problem occurs when a monitored wired network interface or physical Ethernet path is unavailable, unstable, or not connected as expected.

## Common Symptoms
- Ethernet link is reported as down.
- Wired connectivity is unavailable.
- Link state repeatedly changes between up and down.
- Packet loss or connectivity problems occur specifically on the wired path.

## Possible Causes
- Loose or damaged Ethernet cable.
- Faulty connector or switch port.
- Disabled network interface.
- Interface configuration problem.
- Hardware failure.

## Diagnostic Indicators
Ethernet status should be interpreted together with packet loss, Internet reachability, and the observed interface state. A reported link-down condition provides stronger evidence than general network slowness alone.

## Recommended Recovery Actions
1. Check that both ends of the Ethernet cable are securely connected.
2. Inspect the cable and connectors for visible damage.
3. Check the interface link state.
4. If appropriate, test another known-good cable or switch port.
5. Verify interface configuration and network status.

## Verification
Confirm that the Ethernet link remains up and that packet loss and connectivity return to the expected baseline.

## Expected Outcome
Stable wired connectivity and normal network performance.
