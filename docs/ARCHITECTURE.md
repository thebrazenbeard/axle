# AXLE Architecture

AXLE is an edge computer that happens to live in a vehicle. It is not a cloud thin client and it is not a vehicle ECU.

The architecture separates inference, interaction permission, network access, audio routing, and vehicle effects. In v1, vehicle effects are not implemented.

```text
Touchscreen / voice
        |
        v
+------------------------------+
| AXLE Core                    |
| session | policy | context   |
| deterministic capability gate|
+--------+------------+--------+
         |            |
   +-----v----+  +----v----------------+
   | Local AI |  | Audio / Connectivity |
   | sidecars |  | PipeWire / NM        |
   +----------+  +----------------------+
         |
+--------v-------------------------------+
| Read-only vehicle telemetry gateway    |
| SocketCAN receive -> normalized facts   |
| NO TRANSMIT PATH IN V1                 |
+-----------------------------------------+
```

## Voice path

```text
microphone -> wake word -> VAD/noise suppression -> whisper.cpp
-> AXLE Core policy/context -> llama.cpp -> capability broker
-> Piper -> PipeWire duck/mix -> vehicle audio
```

The assistant remains functional without WAN. Phone tethering enriches remote-data features later; it does not host cognition required for ordinary use.

## Core safety boundary

When motion is `moving` or `unknown`, the core rejects manual text requests even if a stale or malicious UI attempts to send them. Hiding controls in the UI is not the safety boundary.

Model output is data, not authority. The model endpoint receives no shell, filesystem, package-manager, or CAN capability.

## Connectivity

NetworkManager remains the OS source of truth for links. AXLE observes link state and classifies likely phone tethering. Internet loss must degrade remote features only.

A reasonable deployment preference is USB phone tether, then known Wi-Fi hotspot, then optional embedded modem, then none.

## Audio

PipeWire/WirePlumber is the target audio graph. Independent nodes should cover media, navigation prompts, AXLE speech, calls, and microphone capture. AXLE speech requests ducking; it does not globally seize the device.

## Vehicle telemetry

Telemetry runs separately with the smallest device privilege possible. It may expose normalized speed, gear, ignition, battery voltage, temperatures, or other vehicle-specific facts with provenance and freshness.

The first production rule is absolute: **read-only SocketCAN interface, no transmit capability**.

## Failure behavior

- Local model unavailable -> explicit failure; no silent cloud fallback.
- Tether unavailable -> local features continue.
- Telemetry unavailable/stale -> motion becomes `unknown`.
- CAN adapter missing -> vehicle context disappears; assistant/media continue.
- UI failure -> sidecars remain isolated.
- Audio graph failure -> preserve factory/physical bypass where the installation supports it.
