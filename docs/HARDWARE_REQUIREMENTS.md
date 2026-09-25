# AXLE Hardware Requirements V1

The authoritative requirement list is `hardware/requirements.json`. This document explains the engineering intent.

## Compute

Prototype reference: NVIDIA Jetson Orin Nano Super Developer Kit.

Current NVIDIA material describes the Orin Nano series at up to 67 TOPS with 7 W, 15 W, and 25 W power options. The developer kit exposes DisplayPort, four USB 3.2 Type-A ports, Gigabit Ethernet, M.2 Key-M 2280 storage, M.2 2230 slots, and a 19 V DC input.

NVIDIA explicitly states Jetson developer kits are not for production use. AXLE therefore treats the developer kit as a measurement/development platform only. A vehicle-installed product must move to a production module/carrier implementation and re-qualify power, thermals, storage, and I/O.

## Storage

Prototype target: 512 GB or larger NVMe M.2 2280.

The design prefers NVMe over microSD because models, offline media, logs, updates, and swap/write load are sustained workloads. Release acceptance requires at least 20% free capacity; actual endurance and temperature requirements depend on the final enclosure and write profile.

## Display

- 7–10 inch capacitive touch.
- At least 1280x800 logical resolution.
- Daylight-readable target: rated >=800 nit or equivalent installed readability.
- USB HID touch preferred.
- DisplayPort-native input preferred for the Orin Nano dev kit; validate any active DP-to-HDMI conversion separately.
## Voice capture

Prototype reference: Seeed Studio ReSpeaker XVF3800 USB 4-Mic Array.

The current XVF3800 line provides four microphones and onboard AEC, AGC, direction-of-arrival, beamforming, VAD, noise suppression, and dereverberation. Those are useful cabin-prototype features, not proof of moving-vehicle recognition quality.

AXLE's software reference capture is 16 kHz mono s16 WAV because that is directly consumable by the current whisper.cpp CLI path.

## Audio output

AXLE needs a Linux-visible stereo output that can feed a vehicle-specific line/AUX/amplifier integration path. The prototype may use a USB UAC audio interface.

The system must preserve critical factory chimes/audio if AXLE loses power. A ground-loop/noise strategy is part of the installed audio design.

## Network

- USB phone tether: primary optional WAN path.
- Wi-Fi phone hotspot: secondary optional WAN path.
- WAN is never required for Core startup or local voice.
- Bluetooth remains available for media/call work but is not AXLE's required WAN transport.
## Vehicle telemetry

Linux SocketCAN is the software abstraction, but SocketCAN itself supports both receive and transmit.

AXLE v1 therefore requires more than an application promise:

1. AI/UI processes receive no writable CAN capability.
2. The telemetry gateway uses controller listen-only mode when supported.
3. Production should inhibit TX below that process boundary, preferably at gateway/controller or transceiver level.
4. Qualification includes an attempted-transmit test with an independent bus monitor.

PEAK PCAN-USB FD is a current Linux/SocketCAN-capable bench reference. Because it can transmit, it does not by itself satisfy the production receive-only invariant.

## Power

The prototype budget reserves 100 W of protected DC/DC capacity for compute, carrier/NVMe, display, microphone/audio I/O, tether/peripherals, telemetry/controls, and cooling. The speaker amplifier is excluded.

This is a sizing target. Final power hardware must be selected from measured worst-case load plus thermal derating and vehicle-input transient requirements.

Raw vehicle battery voltage must never be fed directly to the development kit.
## Power-control behavior

Vehicle-install power hardware must provide:

- fused battery/ACC inputs appropriate to the installation;
- protected conversion suitable for the vehicle electrical environment;
- ignition-state sensing;
- clean shutdown/sleep sequencing;
- low quiescent draw after shutdown;
- restart behavior that does not corrupt storage;
- separate consideration of display/peripheral rails and compute rail.

The current Orin Nano developer kit expects a 19 V supply. A future production carrier may not, so 19 V is not a universal AXLE rail requirement.

## Physical control

A dedicated physical voice button is strongly preferred for moving operation. It enters AXLE as `VoiceTrigger.HARDWARE_BUTTON`; it does not create a generic GPIO effect channel.

## Mechanical/thermal

The installed enclosure must restrain boards/cables, prevent conductive debris contact, maintain service access, and sustain inference without unstable thermal throttling. Final validation occurs in the actual mounting orientation.
