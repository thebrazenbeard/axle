# AXLE Continuation Checkpoint V2

Status date: 2026-09-28

## Canonical source

Repository: thebrazenbeard/axle

Canonical source before this repair pass:

main@395673bd658322e1844dd60027f2f80f358ecfba

The Stage 1A local-voice/hardware package from the historical V1 checkpoint is
already integrated into canonical main. V1 remains provenance; it must not be
read as saying that its old pull request is still pending.

## Current implementation

The executable core includes:

- local OpenAI-compatible llama.cpp model integration;
- local push-to-talk capture -> whisper.cpp -> policy -> model -> Piper -> playback;
- bounded voice-backend failure handling;
- motion-aware manual/touch policy;
- browser trigger provenance protection;
- network/tether classification;
- hardware requirement, reference BOM, and power-budget contracts;
- Linux systemd service template;
- touchscreen UI.

The vehicle-bus contract remains receive-only. No source state in this
checkpoint authorizes CAN transmit, vehicle actuation, deployment, or vehicle
installation.

## Fresh repair qualification

On Windows/Lappy against the canonical source cut:

- Python source/tests compile: PASS;
- unit tests: 30/30 PASS;
- UI JavaScript parse with Node: PASS;
- hardware JSON parse: PASS;
- repository diff check: PASS.

The repair adds a stdlib Python repository validator so the Python/hardware
qualification no longer depends on GNU make being installed on the developer
machine. The existing Makefile remains the POSIX convenience surface.

## Remaining frontier

Stage 1B remains the next product frontier:

1. trusted local trigger ingress not assertable by the browser;
2. openWakeWord sidecar;
3. physical-button adapter;
4. barge-in and explicit PipeWire ducking;
5. latency/recognition instrumentation on the target Jetson bench.

Physical hardware qualification remains separate from source qualification.
