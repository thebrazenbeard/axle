# AXLE Threat Model

Protected assets include driver attention, the vehicle-control boundary, microphone audio, local conversation data, phone-tether traffic, runtime integrity, telemetry, and update provenance.

## Trust zones

**UI:** may request actions but grants no capability.

**AXLE Core:** owns deterministic policy and binds to loopback by default.

**AI sidecars:** untrusted computation behind narrow local APIs. Prompt injection must not produce shell/CAN authority.

**Vehicle telemetry gateway:** minimal privilege, receive only in v1.

**WAN:** hostile network. Internet availability never widens vehicle permissions.

## Primary controls

- Do not expose Core/model APIs to tether clients unless an authenticated local transport is deliberately added.
- Do not enable generic model-server agent/filesystem/shell modes in vehicle deployments.
- Do not give AI/UI processes writable CAN sockets; enforce receive-only below application policy where practical.
- Pin deployed dependencies and model-file digests; retain license/provenance.
- Production updates should be signed, atomic, and rollback-capable.
- Cloud fallback is disabled by default; remote tools must declare what leaves the device.
