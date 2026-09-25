# AXLE Reference Hardware

## Prototype compute

The first reference target is the **NVIDIA Jetson Orin Nano Super Developer Kit**: 67 INT8 TOPS advertised AI performance, 8 GB LPDDR5, NVMe support, and 7 W / 15 W / 25 W power modes. NVIDIA describes local LLM use including roughly the 8B class.

That makes it a useful development target, not a guarantee of latency for every model/context and not an automotive qualification.

A permanent vehicle product needs ruggedized compute/carrier hardware, automotive power conditioning, validated thermal and vibration behavior, EMC work, and an enclosure designed for cabin temperature extremes.

## Display

Prototype target: 7–10 inch capacitive touchscreen, HDMI/DP plus USB touch, high brightness preferred. Mounting must not obstruct driver sightlines, required controls, or air bags.

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

Use a directional cabin microphone or small array near the driver with echo/noise processing. Road, HVAC, and tire noise are first-order constraints.

## Phone bridge

Support USB tethering and Wi-Fi hotspot. USB is preferred when practical because it is explicit, stable, and can charge the phone. Bluetooth remains available for calls/media but is not the preferred WAN path.

## Vehicle telemetry

Use a Linux-supported USB-to-CAN interface only when vehicle-specific work requires it. SocketCAN exposes adapters as Linux network interfaces. Do not assume OBD-II exposes every desired signal or that undocumented CAN IDs are portable between vehicles.

## Power

Never feed raw vehicle battery voltage directly into a development board.

Use fused inputs, automotive-rated DC/DC conversion, reverse-polarity/transient protection, ignition sensing, graceful shutdown hold-up/controller logic, and quiescent-current control. Vehicle supply conditions include cranking dips, noise, and load-dump transients.

## Thermal qualification

Measure cold start, hot soak, sustained inference, full display brightness, and simultaneous tether/charging load before calling hardware installation-ready.
