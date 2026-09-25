# Research Notes — 2026-09-25

These are design inputs, not bundled dependencies.

- NVIDIA Jetson Orin Nano Super: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/
- NVIDIA Jetson generative-AI notes: https://developer.nvidia.com/blog/jetson-orin-nano-super-developer-kit-generative-ai/
- NVIDIA Orin Nano developer-kit hardware/user guide: https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/hardware_layout.html
- NVIDIA Jetson FAQ (developer kits are not production systems): https://developer.nvidia.com/embedded/faq
- llama.cpp: https://github.com/ggml-org/llama.cpp
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- openWakeWord: https://github.com/dscripka/openWakeWord
- Piper current Open Home Foundation line: https://github.com/OHF-Voice/piper1-gpl
- PipeWire pw-record/pw-play: https://pipewire.pages.freedesktop.org/pipewire/page_man_pw-cat_1.html
- ReSpeaker XVF3800 USB 4-Mic Array: https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/
- PEAK-System Linux CAN driver support: https://www.peak-system.com/fileadmin/media/linux/index.php
- Linux SocketCAN: https://docs.kernel.org/networking/can.html
- NHTSA visual-manual distraction guidance: https://www.nhtsa.gov/document/visual-manual-nhtsa-driver-distraction-guidelines-vehicle-electronic-devices

Notes:

1. The original `rhasspy/piper` repository is archived; AXLE references `OHF-Voice/piper1-gpl` instead.
2. openWakeWord code and distributed model assets can carry different licenses. Deployment must review exact model rights.
3. NHTSA guidance informs the fail-closed motion policy, but AXLE makes no compliance claim at this stage.
4. The current Orin Nano developer kit uses DisplayPort and a 19 V supply; do not copy older Jetson Nano I/O/power assumptions into AXLE.
5. The XVF3800 is the current microphone-array prototype reference; older ReSpeaker USB array generations are not the default for a new AXLE build.
6. PCAN-USB FD is a bench telemetry reference, not proof of the production receive-only invariant because the adapter is capable of transmitting.
