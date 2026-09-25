# AXLE Continuation Checkpoint V1

Status date: 2026-09-25

## Exact subject

- Repository: `thebrazenbeard/axle`
- Branch: `build/axle-local-edge-v1`
- Pull request: #1
- Verified implementation head before this checkpoint: `2656de553cf79e8a2cbdcf541250bca496e310e8`
- Base: `main`
- Integration state: open PR; not merged.

## Completed frontier

Stage 1A local voice is implemented as a bounded local path:

```text
touch / trusted trigger
-> PipeWire capture
-> whisper.cpp
-> AXLE Core policy
-> local llama.cpp
-> Piper
-> PipeWire playback
```

The browser-facing voice endpoint is always classified as touch. It cannot assert wake-word or hardware-button provenance. Touch initiation is parked-only. Internal policy types exist for trusted wake-word and physical-button triggers, but their adapters are not yet implemented.

Per-turn captured audio, transcript, and reply WAV artifacts are ephemeral and removed after completion/cancel/failure. Local subprocess failures are converted into bounded voice-backend errors.

## Hardware package

Source-controlled hardware work now includes:

- `hardware/requirements.json`
- `hardware/reference_bom.json`
- `hardware/power_budget.json`
- `docs/HARDWARE_REQUIREMENTS.md`
- `docs/HARDWARE_BUILD.md`
- `docs/HARDWARE_QUALIFICATION.md`

Prototype references include Jetson Orin Nano Super, >=512 GB NVMe, ReSpeaker XVF3800 USB microphone array, Linux UAC line-level audio, user phone USB/Wi-Fi tether, and conditional SocketCAN bench telemetry.

The vehicle power module remains deliberately unselected pending evidence for transient behavior, ignition/shutdown, thermal derating, quiescent draw, fuse/conductor design, and the final compute-carrier rail.

The production vehicle-bus requirement remains receive-only. A generic writable USB CAN adapter is bench equipment only and does not by itself satisfy the no-transmit invariant.

## Verification

Exact implementation subject `2656de553cf79e8a2cbdcf541250bca496e310e8`:

- fresh remote clone: PASS
- Python compile: PASS
- unit tests: 30/30 PASS
- UI JavaScript parse: PASS
- hardware JSON parse/contract tests: PASS
- browser hardware-trigger spoof regression: PASS (423 Locked)
- GitHub Actions CI run `36122330817`: PASS

## Not established

The following are intentionally not claimed:

- actual Jetson hardware assembly or installation;
- successful microphone/audio inference on target Linux hardware;
- openWakeWord runtime integration;
- physical push-to-talk adapter;
- barge-in or PipeWire ducking;
- measured cabin speech accuracy or latency;
- selected/qualified automotive DC/DC power controller;
- CAN receive-only hardware qualification on a real vehicle;
- production thermal/EMC/vibration qualification;
- vehicle installation qualification.

## Authority ceiling

No merge, deployment, vehicle installation, purchase, CAN actuation, credential change, provider change, or protected release effect is authorized by this checkpoint.

## Next executable frontier

Stage 1B:

1. implement a trusted local trigger ingress that is not browser-assertable;
2. add the openWakeWord sidecar against that ingress;
3. add a physical-button adapter against the same ingress;
4. add barge-in and explicit PipeWire ducking;
5. add latency/recognition instrumentation for Jetson bench qualification.

After Stage 1B is source-verified, move to the physical Jetson bench build and close hardware qualification gates with measured evidence.
