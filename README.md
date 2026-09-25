> **License:** Source-visible, not open source. Original AXLE material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# AXLE

**Automotive eXperience & Local Edge**

AXLE is a local-first, AI-native vehicle computer: a touchscreen head unit with on-vehicle inference, vehicle-audio integration, optional read-only vehicle telemetry, and internet access through the user's bridged cellular device.

The central rule is simple: **the phone is an uplink, not the brain**. Core interaction should continue when the vehicle has no cellular connection.

## Product idea

AXLE turns a Linux edge computer mounted in the vehicle into a private, offline-capable copilot and media head unit. The reference stack is designed around:

- a 7–10 inch capacitive touchscreen running a kiosk UI;
- local wake-word detection, speech-to-text, language-model inference, and text-to-speech;
- PipeWire-based mixing/ducking into the vehicle audio path;
- USB or Wi-Fi phone tethering managed as an optional WAN connection;
- read-only vehicle telemetry through a separately isolated gateway;
- a motion-aware interaction policy that disables high-distraction manual interaction when motion is moving or unknown;
- an effect broker architecture where model output is never vehicle-control authority.

## Reference AI stack

AXLE intentionally treats inference engines as replaceable sidecars.

| Function | Reference implementation | Network required |
| --- | --- | --- |
| Wake word | openWakeWord | No |
| Speech-to-text | whisper.cpp | No |
| LLM/VLM | llama.cpp | No |
| Text-to-speech | Piper (OHF-Voice/piper1-gpl) | No |
| Audio graph | PipeWire/WirePlumber | No |
| Vehicle telemetry | Linux SocketCAN | No |
| Tether management | NetworkManager | Only for WAN |

The runnable v0 core in this repository currently integrates the OpenAI-compatible local endpoint exposed by `llama.cpp`. Voice and vehicle adapters are specified but intentionally remain separate from the first core so that unsafe actuation does not accidentally appear as a side effect of infotainment work.

## Quick start

Requirements: Python 3.11+.

```bash
cp config/axle.example.toml config/axle.local.toml
PYTHONPATH=src python -m axle.server --config config/axle.local.toml
```

Then open `http://127.0.0.1:8787`.

For a real local model, start `llama-server` on the configured endpoint first. The example expects an OpenAI-compatible endpoint at `http://127.0.0.1:8080/v1/chat/completions`.

Run verification with:

```bash
make test
```

## Repository map

- `src/axle/` — core service, policy engine, local-LLM adapter, and tether status.
- `ui/` — low-distraction touchscreen UI served locally by AXLE Core.
- `config/` — source-controlled example configuration.
- `docs/ARCHITECTURE.md` — subsystem boundaries and data flow.
- `docs/HARDWARE.md` — reference compute, power, display, microphone, audio, and telemetry design.
- `docs/SAFETY.md` — motion policy and vehicle-control boundary.
- `docs/THREAT_MODEL.md` — trust boundaries and attack surfaces.
- `docs/ROADMAP.md` — staged implementation plan.
- `docs/RESEARCH_NOTES.md` — source-backed design choices.
- `deploy/systemd/` — Linux service template.

## Status

This branch is an architecture + executable-core bootstrap, not a production automotive head unit. The NVIDIA developer kit described in the hardware notes is prototype hardware, not an automotive-qualified ECU. Production installation requires appropriate power conditioning, thermal design, vibration resistance, enclosure design, EMC work, audio isolation, and vehicle-specific validation.

AXLE's v1 vehicle boundary is **read only**. No AI response, plugin, web request, or UI action is permitted to transmit vehicle-bus commands.
