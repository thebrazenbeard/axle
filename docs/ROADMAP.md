# AXLE Roadmap

## Stage 0 — bootstrap

Current branch: architecture, kiosk UI, local llama.cpp text path, core-enforced motion policy, NetworkManager status, tests and CI.

## Stage 1 — local voice loop

### Stage 1A — executable push-to-talk path

Implemented on the current frontier:

- PipeWire WAV capture;
- whisper.cpp transcription;
- AXLE Core -> local llama.cpp;
- Piper WAV synthesis;
- PipeWire playback;
- parked-only touchscreen trigger;
- moving-capable hardware-button/wake-word trigger policy seams;
- tested runtime state machine and subprocess boundaries.

### Stage 1B — hands-free cabin completion

Remaining:

- openWakeWord sidecar;
- physical-button adapter;
- barge-in/cancel;
- explicit PipeWire ducking;
- echo/noise tuning on current microphone hardware;
- bounded moving-mode spoken responses;
- target-hardware latency and recognition measurements.

## Stage 2 — media/audio head unit

Add PipeWire graph and ducking priorities, local media, Bluetooth calls/media, vehicle-appropriate media-key input, and preservation of critical factory chimes.

## Stage 3 — read-only vehicle context

Add a separate SocketCAN telemetry service, vehicle profile registry, provenance/freshness, speed/gear/ignition policy inputs, and dashboard widgets. No transmit path.

## Stage 4 — tethered remote tools

Add opt-in traffic/weather/search only after local interaction is solid. Each remote capability declares required network, off-device data, motion allowance, timeout behavior, and downstream effect scope.

## Stage 5 — navigation

Offline maps/routing baseline, GPS, tethered traffic enrichment, voice-first destination entry, safe moving-mode visuals.

## Stage 6 — hardened appliance

Immutable/atomic OS image, signed updates, watchdogs, automotive power controller, thermal qualification, threat-model verification, and vehicle-specific installation kits.
