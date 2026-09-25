# AXLE Local Voice Runtime

## Implemented frontier

AXLE v0.2 adds an executable local push-to-talk voice turn:

```text
trigger
  -> pw-record (16 kHz / mono / s16 WAV)
  -> whisper.cpp whisper-cli
  -> AXLE Core policy/context
  -> local llama.cpp endpoint
  -> Piper WAV synthesis
  -> pw-play / PipeWire
```

The implementation lives in `src/axle/voice.py`. It uses explicit subprocess argument vectors; configured command arrays are never joined into shell strings.

## Trigger policy

Voice content and voice initiation are distinct.

- `touch`: allowed only when motion is `parked`.
- `wake_word`: allowed when voice interaction is enabled, including moving mode.
- `hardware_button`: allowed when voice interaction is enabled, including moving mode.

This prevents “voice is allowed” from accidentally making a touchscreen task permissible while driving.

The current UI implements the `touch` trigger. Wake-word and physical-button adapters plug into the same Core seam.
## Runtime states

`IDLE -> LISTENING -> PROCESSING -> SPEAKING -> IDLE`

A second start while non-idle is rejected. Backend failure moves the runtime to `ERROR`; cancel/reset returns it to `IDLE`.

An empty transcript does not call the LLM or TTS backend.

## Configuration

Use `config/axle.jetson.example.toml` as the target example.

Required voice fields:

- `stt_model`: path to a whisper.cpp GGML model.
- `tts_model`: Piper voice name/model.
- `capture_command`: command template containing `{wav}`.
- `stt_command`: supports `{model}`, `{wav}`, and `{out}`.
- `tts_command`: supports `{model}`, `{wav}`, and `{text}`.
- `playback_command`: supports `{wav}`.

The source-controlled default config keeps voice disabled and motion unknown.

## Current external interfaces

PipeWire `pw-record` supports explicit rate, channels, and sample format. whisper.cpp's CLI accepts WAV and the reference path produces a text file with `-otxt -of`. Current Piper supports `python -m piper -m <voice> -f <wav> -- <text>`.

AXLE does not vendor those projects or voice/model weights.
## Remaining Stage 1 work

1. Add an openWakeWord sidecar that emits only a bounded `wake_word` trigger.
2. Add a physical-button input adapter.
3. Add barge-in: incoming speech cancels current TTS/playback.
4. Measure end-of-speech -> transcript -> first spoken reply latency on Jetson.
5. Tune microphone AEC/noise suppression inside an actual moving vehicle.
6. Replace per-turn Piper process startup with a persistent service if measurements justify it.
7. Add audio ducking policy around speech rather than relying on default PipeWire mixing.

No wake-word implementation is claimed by the current code merely because the trigger type exists.
