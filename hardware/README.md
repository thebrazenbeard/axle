# AXLE Hardware Package

This directory is the machine-readable hardware contract for AXLE.

- `requirements.json` — requirement IDs, priorities, statements, and verification methods.
- `reference_bom.json` — prototype reference parts/classes and their deployment ceilings.
- `power_budget.json` — conservative design allocation used to size the prototype power stage.

The JSON files are tested by `tests/test_hardware_contract.py`. They deliberately distinguish:

- **prototype reference** — useful to build and measure now;
- **class requirement** — a component category still requiring exact selection;
- **vehicle-install required** — safety/reliability-sensitive hardware that is not accepted until evidence closes its requirements.

A public product page or a successful bench test is not automotive qualification.
