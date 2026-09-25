# AXLE Reference Hardware

## Prototype compute

The first reference target is the **NVIDIA Jetson Orin Nano Super Developer Kit**: 67 INT8 TOPS advertised AI performance, 8 GB LPDDR5, NVMe support, and 7 W / 15 W / 25 W power modes. NVIDIA describes local LLM use including roughly the 8B class.

That makes it a useful development target, not a guarantee of latency for every model/context and not an automotive qualification.

A permanent vehicle product needs ruggedized compute/carrier hardware, automotive power conditioning, validated thermal and vibration behavior, EMC work, and an enclosure designed for cabin temperature extremes.

## Display

Prototype target: 7–10 inch capacitive touchscreen, at least 1280x800, USB touch, and high brightness. The Orin Nano developer kit exposes DisplayPort, so DisplayPort-native input is preferred; HDMI-only panels require a validated active DP-to-HDMI adapter. Mounting must not obstruct driver sightlines, required controls, or air bags.

## Audio

Preferred prototype path:

```text
AXLE USB audio interface / DAC
 -> line-level output
 -> vehicle AUX / aftermarket amp / vehicle-specific integration interface
 -> speakers
```

A USB audio interface gives Linux a stable ALSA/PipeWire endpoint. For vehicles without a suitable analog path, use a vehicle-specific integration module rather than injecting arbitrary traffic into factory digital buses.

Preserve a fail-safe path for critical factory chimes/audio.

## Microphones

Prototype reference: Seeed Studio ReSpeaker XVF3800 USB 4-Mic Array, which provides a current USB four-microphone platform with onboard AEC, AGC, beamforming, VAD, noise suppression, direction-of-arrival, and dereverberation. Road, HVAC, and tire noise remain first-order constraints and must be measured in the actual cabin.

## Phone bridge

Support USB tethering and Wi-Fi hotspot. USB is preferred when practical because it is explicit, stable, and can charge the phone. Bluetooth remains available for calls/media but is not the preferred WAN path.

## Vehicle telemetry

Use a Linux/SocketCAN-supported interface only when vehicle-specific work requires it. PEAK PCAN-USB FD is the current bench reference. Because generic adapters can transmit, production v1 also requires controller/gateway listen-only enforcement and an independent no-TX qualification test. Do not assume OBD-II exposes every desired signal or that undocumented CAN IDs are portable between vehicles.

## Power

Never feed raw vehicle battery voltage directly into a development board.

Use fused inputs, automotive-rated DC/DC conversion, reverse-polarity/transient protection, ignition sensing, graceful shutdown hold-up/controller logic, and quiescent-current control. Vehicle supply conditions include cranking dips, noise, and load-dump transients.

## Thermal qualification

Measure cold start, hot soak, sustained inference, full display brightness, and simultaneous tether/charging load before calling hardware installation-ready.


## Contract and build documents

Detailed, tested hardware state is maintained in:

- `hardware/requirements.json`
- `hardware/reference_bom.json`
- `hardware/power_budget.json`
- `docs/HARDWARE_REQUIREMENTS.md`
- `docs/HARDWARE_BUILD.md`
- `docs/HARDWARE_QUALIFICATION.md`
