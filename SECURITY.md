# Security Policy

Do not disclose exploitable security issues through a public issue when they involve credentials, private user data, remote code execution, or a plausible vehicle-control boundary bypass.

For security reports, contact the repository owner privately through an available GitHub security-reporting channel when enabled. Include the affected commit/version, reproduction conditions, expected impact, and whether the issue crosses AXLE's UI, Core, AI-sidecar, network, audio, or vehicle-telemetry trust boundary.

AXLE v1 explicitly treats any path that can transmit vehicle-bus commands as out of scope and prohibited. A finding that creates such a path is security-critical even if the current UI does not expose it.
