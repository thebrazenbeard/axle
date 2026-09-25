# AXLE Prototype Hardware Build

## Build objective

Create a removable, bench-first AXLE prototype that can be moved into a vehicle for measurement without pretending it is a released automotive ECU.

```text
12 V vehicle system
      |
      v
[ fused protected power / ignition controller ]
      |
      +---- regulated compute rail ---> Jetson Orin Nano Super Dev Kit
      |                                  |-- NVMe SSD
      |                                  |-- USB XVF3800 mic array
      |                                  |-- USB audio interface
      |                                  |-- USB phone tether
      |                                  |-- USB CAN bench adapter (optional)
      |                                  `-- USB HID physical PTT
      |
      +---- display rail --------------> 7-10" touch display
                                             |
Jetson DisplayPort --------------------------+
USB touch -----------------------------------+

USB audio line out --> vehicle-specific AUX / integration interface --> factory/aftermarket amplifier
```

Do not include the speaker amplifier in the AXLE compute power converter budget unless the installation intentionally replaces the vehicle amplifier.
## Prototype bill of materials

| Subsystem | Reference | Status |
| --- | --- | --- |
| Compute | Jetson Orin Nano Super Developer Kit | selected prototype reference |
| Storage | >=512 GB M.2 2280 NVMe | select for endurance/thermal margin |
| Display | 7-10" >=1280x800 capacitive touch, high brightness | exact panel open |
| Microphone | ReSpeaker XVF3800 USB 4-Mic Array | selected prototype reference |
| Audio | Linux UAC USB stereo line interface | exact interface open |
| WAN | user phone USB tether + Wi-Fi hotspot | architectural requirement |
| Power | protected automotive DC/DC + ignition/shutdown controller | **not yet selected** |
| CAN | PEAK PCAN-USB FD or equivalent SocketCAN bench interface | conditional, telemetry only |
| Voice control | USB HID / isolated GPIO momentary button | exact control open |
| Enclosure | ventilated restrained prototype enclosure | vehicle-specific |

Machine-readable details live in `hardware/reference_bom.json`.
## Bring-up order

1. Build the entire system on the bench from the vendor 19 V supply. Do not begin with vehicle battery power.
2. Install NVMe and Jetson software; run AXLE Core with no WAN.
3. Attach the touchscreen and verify edge-to-edge touch mapping.
4. Attach XVF3800 and confirm PipeWire sees the capture device.
5. Record a 16 kHz mono s16 WAV with the exact AXLE capture command.
6. Install/build whisper.cpp and verify the chosen model transcribes the test WAV.
7. Install Piper and verify the selected voice creates a reply WAV.
8. Attach the USB audio interface and verify `pw-play` without vehicle connection.
9. Connect to a non-critical external amplifier/speaker and tune levels/AEC.
10. Add the physical voice button and verify the Core receives only the bounded trigger event.
11. Add CAN only after the telemetry gateway is configured and independently verified receive-only.
12. Characterize total power draw before selecting the vehicle DC/DC stage.
13. Only then build the protected vehicle power/harness layer.
## Vehicle power frontier

Do not select the final converter from wattage alone.

The chosen power subsystem must close these evidence gaps:

- input/transient behavior appropriate to the target vehicle electrical system;
- cranking/restart behavior;
- reverse-polarity protection;
- converter thermal derating at the mounting location;
- ignition sense and delayed clean shutdown;
- low-voltage/battery-drain policy;
- quiescent current;
- fuse location and conductor sizing;
- 19 V compatibility for the dev kit or the actual rail required by the production carrier.

Until those are verified, the repo intentionally records `BOM-POWER-001.selection = not_selected`.

## Vehicle bus frontier

The bench CAN reference is useful for discovery and capture, but a production v1 AXLE telemetry device needs a stronger receive-only boundary. A writable generic USB CAN adapter is not enough simply because application code promises not to call `send()`.

The release gate is evidence that a compromised UI/model process cannot put a frame on the vehicle bus.
