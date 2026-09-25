# AXLE Hardware Qualification Plan

Qualification is evidence for a specific hardware/software/install subject. A successful bench prototype is not vehicle-install qualification.

## Q0 — inventory and provenance

Record exact:

- compute module/carrier and firmware;
- NVMe make/model/firmware;
- display and active adapters;
- microphone firmware mode/version;
- USB audio interface;
- power converter/controller;
- CAN interface and driver/kernel version;
- enclosure/fans;
- AXLE commit and model digests.

PASS: every installed item maps to the BOM or an explicitly approved substitution.

## Q1 — offline compute

Disconnect WAN and boot AXLE.

Run repeated local voice turns and a 60-minute mixed STT/LLM/TTS load.

Record temperature, throttling flags, memory pressure, model latency, and unexpected resets.

PASS: no WAN dependency, no crash/reset, and no thermal behavior that makes the interaction unusable.
## Q2 — cabin voice/audio

Test at minimum:

- engine off / quiet cabin;
- engine idle;
- HVAC low/high;
- road/tire noise at representative speeds;
- cabin audio playing while speaking;
- driver and passenger speech;
- TTS interruption/cancel behavior.

Measure word-error/command-success rate and end-of-speech-to-reply latency rather than relying on subjective impressions.

PASS criteria are established from measured prototype data; this document does not invent thresholds before measurements exist.

## Q3 — power

Bench-simulate the selected power subsystem's specified input envelope and ignition transitions.

Verify:

- clean boot;
- ignition-on restart policy;
- graceful ignition-off shutdown/sleep;
- repeated rapid ignition transitions;
- filesystem integrity;
- converter and enclosure temperatures;
- parked quiescent draw;
- no undervoltage loop/reboot storm.

Do not perform transient tests directly on the vehicle as a substitute for a controlled bench source/test setup.
## Q4 — audio integration

With final vehicle-specific audio interface:

- verify normal music/media;
- verify AXLE prompt ducking;
- verify phone-call priority;
- check alternator/ground-loop noise;
- power AXLE off unexpectedly.

PASS: factory safety-relevant chimes/functions remain available and AXLE failure does not leave the cabin audio path latched or unusable.

## Q5 — receive-only CAN

Use an independent bus monitor.

1. Bring up the telemetry interface in the intended listen-only state.
2. Capture known traffic.
3. Attempt transmission from the telemetry service.
4. Attempt transmission from a separate unprivileged test process.
5. Exercise a compromised-process simulation within the AXLE software permission boundary.
6. Observe the bus independently.

PASS: zero AXLE-originated frames reach the vehicle bus.

If the reference adapter cannot provide a sufficiently strong no-TX boundary, the production design must change hardware rather than weaken the requirement.
## Q6 — network failure

During active local voice/media:

- attach/detach USB tether;
- enable/disable Wi-Fi hotspot;
- remove WAN entirely;
- reconnect with a different user phone.

PASS: local voice continues and vehicle permissions do not change with network availability.

## Q7 — mechanical and thermal installation

In final mounting orientation:

- inspect harness strain relief;
- inspect air-bag/sightline/control clearance;
- hot-soak under inference;
- check fan blockage and recirculation;
- inspect fasteners after representative vibration/road use;
- re-run touch mapping and microphone tests.

## Result vocabulary

- `BENCH_ASSEMBLED` — parts are connected and boot.
- `VOICE_PATH_VERIFIED` — local audio turn works on exact hardware.
- `POWER_PATH_VERIFIED` — exact power design passed its bench sequence.
- `CAN_RECEIVE_ONLY_VERIFIED` — exact telemetry hardware passed independent no-TX test.
- `VEHICLE_INSTALL_VERIFIED` — exact installed subject passed applicable gates.
- `NOT_ESTABLISHED` — use when evidence is missing.

Do not collapse these states.
