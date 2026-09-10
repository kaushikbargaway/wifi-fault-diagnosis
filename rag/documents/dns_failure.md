# DNS Failure

## Description
DNS failure occurs when a device cannot successfully resolve domain names to IP addresses even though other forms of network connectivity may still be available.

## Common Symptoms
- Websites or services fail by hostname but may be reachable by IP address.
- DNS lookup requests time out or return errors.
- Internet reachability may appear available at the IP layer while name resolution fails.

## Possible Causes
- Incorrect DNS server configuration.
- Unreachable or unavailable DNS resolver.
- Router or local DNS forwarding problem.
- Temporary upstream DNS service failure.
- Network filtering or firewall rules affecting DNS traffic.

## Diagnostic Indicators
A DNS fault is more strongly supported when DNS checks fail while lower-level connectivity remains available. The diagnosis should distinguish DNS failure from complete Internet connectivity failure.

## Recommended Recovery Actions
1. Verify the configured DNS server address.
2. Test DNS resolution repeatedly to confirm that the failure is persistent.
3. Check whether the device can reach the configured DNS server.
4. If permitted by the network administrator, test an alternative trusted DNS resolver.
5. Check router DNS forwarding or local resolver configuration.

## Verification
Repeat DNS queries after the configuration or connectivity issue is corrected. Confirm both successful resolution and normal Internet access.

## Expected Outcome
Reliable domain-name resolution and restoration of applications that depend on DNS.

## Safety Note
DNS configuration changes should follow the organization's network policy.
