# AXLE Safety Contract

AXLE is infotainment/assistant software, not a safety-critical vehicle controller.

## Motion policy

Motion states are `parked`, `moving`, and `unknown`; `unknown` inherits moving restrictions.

| Capability | Parked | Moving | Unknown |
| --- | --- | --- | --- |
| Manual text entry | Yes | No | No |
| Rich visual interaction | Yes | No | No |
| Voice interaction | Yes | Yes | Yes |
| Vehicle-bus write | No | No | No |

A production motion source must carry freshness. Stale speed/gear data becomes `unknown`, never `parked`.

## Driver distraction

AXLE favors short auditory-vocal interactions while driving. NHTSA publishes guidance and test material aimed at reducing visual-manual distraction from integrated in-vehicle devices. A simplified UI is not, by itself, a compliance claim.

## AI authority

The language model may not directly transmit CAN frames, run arbitrary shell commands, reconfigure networking, install software, alter safety policy, or bypass motion locks.

Future tools must cross deterministic policy outside the model.

## Telemetry

Vehicle data can be stale, spoofed, vehicle-specific, or misdecoded. Normalized values need provenance and freshness. AI explanations are not diagnostic proof.

## Physical installation

Preserve air bag zones, visibility, required controls, warning/chime behavior, fuse protection, and safe vehicle wiring.
