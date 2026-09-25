# AXLE

**Automotive eXperience & Local Edge**

AXLE is a local-first, AI-native vehicle-computer project: a touchscreen head unit with an on-vehicle AI runtime, audio-system integration, and optional internet connectivity through the user's bridged cellular device.

## Current status

`main` is the bootstrap surface. It currently contains the project definition rather than a runnable production vehicle stack.

Architecture or prototype work on other branches should be treated as branch-local until it is reconciled into `main` and independently verified.

## Design direction

AXLE is intended to keep core vehicle interaction useful without requiring permanent cloud connectivity. Any later implementation should make safety-critical vehicle controls, infotainment functions, AI functions, network access, and user authority explicit rather than merging them into one trust boundary.

## Evidence boundary

A repository design, build artifact, bench prototype, installed head unit, and road-qualified system are different evidence stages.
