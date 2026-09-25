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

The runnable v0 core currently integrates the OpenAI-compatible local endpoint exposed by `llama.cpp`. Voice/audio and vehicle adapters are specified but deliberately separate from the first core.

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

- `src/axle/` — core service, policy engine, local-LLM adapter, and tether status.
- `ui/` — low-distraction touchscreen UI served locally by AXLE Core.
- `config/` — source-controlled safe-default configuration.
- `docs/ARCHITECTURE.md` — subsystem boundaries and data flow.
- `docs/HARDWARE.md` — compute, power, display, microphone, audio, and telemetry design.
- `docs/SAFETY.md` — motion policy and vehicle-control boundary.
- `docs/THREAT_MODEL.md` — trust boundaries and attack surfaces.
- `docs/ROADMAP.md` — staged implementation plan.
- `docs/RESEARCH_NOTES.md` — source-backed design choices.
- `deploy/systemd/` — Linux service template.

## Status

This is an architecture + executable-core bootstrap, not a production automotive head unit. The NVIDIA developer kit described in the hardware notes is prototype hardware, not an automotive-qualified ECU.

AXLE's v1 vehicle boundary is **read only**. No AI response, plugin, web request, or UI action is permitted to transmit vehicle-bus commands.
