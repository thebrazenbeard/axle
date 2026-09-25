# Research Notes — 2026-09-25

These are design inputs, not bundled dependencies.

- NVIDIA Jetson Orin Nano Super: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/
- NVIDIA Jetson generative-AI notes: https://developer.nvidia.com/blog/jetson-orin-nano-super-developer-kit-generative-ai/
- llama.cpp: https://github.com/ggml-org/llama.cpp
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- openWakeWord: https://github.com/dscripka/openWakeWord
- Piper current Open Home Foundation line: https://github.com/OHF-Voice/piper1-gpl
- Linux SocketCAN: https://docs.kernel.org/networking/can.html
- NHTSA visual-manual distraction guidance: https://www.nhtsa.gov/document/visual-manual-nhtsa-driver-distraction-guidelines-vehicle-electronic-devices

Notes:

1. The original `rhasspy/piper` repository is archived; AXLE references `OHF-Voice/piper1-gpl` instead.
2. openWakeWord code and distributed model assets can carry different licenses. Deployment must review exact model rights.
3. NHTSA guidance informs the fail-closed motion policy, but AXLE makes no compliance claim at this stage.
