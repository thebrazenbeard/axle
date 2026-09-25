> **License:** Source-visible, not open source. Original AXLE material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# AXLE

**Automotive eXperience & Local Edge**

AXLE is a local-first, AI-native vehicle computer: a touchscreen head unit with on-vehicle inference, vehicle-audio integration, optional read-only vehicle telemetry, and internet access through the user's bridged cellular device.

The central rule is simple: **the phone is an uplink, not the brain**. Core interaction should continue when the vehicle has no cellular connection.

## Product idea

AXLE turns a Linux edge computer mounted in the vehicle into a private, offline-capable copilot and media head unit. The reference design combines:

- a 7–10 inch capacitive touchscreen running a local kiosk UI;
- local wake-word detection, speech-to-text, language-model inference, and text-to-speech;
- PipeWire-based mixing/ducking into the vehicle audio path;
- USB or Wi-Fi phone tethering as optional WAN;
- read-only vehicle telemetry through an isolated gateway;
- a motion-aware policy that disables high-distraction manual interaction when motion is moving or unknown;
- an effect-broker architecture where model output is never vehicle-control authority.

## Reference stack

| Function | Reference implementation | WAN required |
| --- | --- | --- |
| Wake word | openWakeWord | No |
| Speech-to-text | whisper.cpp | No |
| LLM/VLM | llama.cpp | No |
| Text-to-speech | Piper (OHF-Voice/piper1-gpl) | No |
| Audio graph | PipeWire/WirePlumber | No |
| Vehicle telemetry | Linux SocketCAN | No |
| Tether management | NetworkManager | Only for WAN |

The runnable v0.2 core integrates the OpenAI-compatible local endpoint exposed by `llama.cpp` and an executable local push-to-talk path through PipeWire, whisper.cpp, Piper, and PipeWire playback. Wake-word and physical-button trigger types are policy-bound seams; the wake-word detector itself is still a remaining Stage 1 item.

## Quick start

Requirements: Python 3.11+.

```bash
cp config/axle.example.toml config/axle.local.toml
PYTHONPATH=src python -m axle.server --config config/axle.local.toml
```

Then open `http://127.0.0.1:8787`.

The example config fails closed with motion state `unknown`, so manual text is locked. **For a stationary bench/demo only**, edit `config/axle.local.toml` and set:

```toml
[safety]
motion_state = "parked"
```

For a real local model, start `llama-server` on the configured endpoint first. The example expects `http://127.0.0.1:8080/v1/chat/completions`.

Run verification with:

```bash
make test
```

## Repository map

- `src/axle/` — Core, local-LLM adapter, voice runtime, policy, and tether status.
- `ui/` — low-distraction touchscreen UI with parked-only touch push-to-talk.
- `config/` — safe defaults plus a Jetson voice example.
- `hardware/` — tested hardware requirements, reference BOM, and power budget.
- `docs/ARCHITECTURE.md` — subsystem boundaries and data flow.
- `docs/VOICE_RUNTIME.md` — executable local voice path and remaining Stage 1 work.
- `docs/HARDWARE_REQUIREMENTS.md` — human-readable hardware contract.
- `docs/HARDWARE_BUILD.md` — bench-first prototype build sequence.
- `docs/HARDWARE_QUALIFICATION.md` — qualification gates.
- `docs/HARDWARE.md` — high-level hardware design.
- `docs/SAFETY.md` — motion policy and vehicle-control boundary.
- `docs/THREAT_MODEL.md` — trust boundaries and attack surfaces.
- `docs/ROADMAP.md` — staged implementation plan.
- `docs/RESEARCH_NOTES.md` — source-backed design choices.
- `deploy/systemd/` — Linux service template.

## Status

This is an architecture + executable-core + hardware-contract prototype, not a production automotive head unit. The NVIDIA developer kit is deliberately classified as prototype-only; the vehicle power stage and production receive-only telemetry gateway remain unselected until qualification evidence exists.

AXLE's v1 vehicle boundary is **read only**. No AI response, plugin, web request, or UI action is permitted to transmit vehicle-bus commands.
