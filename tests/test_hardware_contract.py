import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HardwareContractTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "hardware" / name).read_text(encoding="utf-8"))

    def test_requirements_have_unique_ids_and_verification(self):
        doc = self.load("requirements.json")
        requirements = doc["requirements"]
        ids = [item["id"] for item in requirements]
        self.assertEqual(len(ids), len(set(ids)))
        for item in requirements:
            self.assertIn(item["priority"], {"MUST", "SHOULD", "TARGET"})
            self.assertTrue(item["subsystem"])
            self.assertTrue(item["statement"])
            self.assertTrue(item["verification"])

    def test_vehicle_bus_contract_is_receive_only(self):
        doc = self.load("requirements.json")
        vehicle = [r for r in doc["requirements"] if r["subsystem"] == "vehicle_bus"]
        self.assertTrue(vehicle)
        self.assertTrue(any(r.get("mode") == "receive_only" for r in vehicle))
        self.assertFalse(any(r.get("transmit_enabled") is True for r in vehicle))
    def test_reference_bom_covers_core_subsystems(self):
        bom = self.load("reference_bom.json")
        subsystems = {item["subsystem"] for item in bom["items"]}
        required = {
            "compute", "storage", "display", "microphone", "audio",
            "network", "power", "vehicle_bus", "controls", "enclosure",
        }
        self.assertTrue(required.issubset(subsystems))

    def test_developer_kit_is_explicitly_prototype_only(self):
        bom = self.load("reference_bom.json")
        compute = next(item for item in bom["items"] if item["id"] == "BOM-COMPUTE-001")
        self.assertEqual(compute["deployment_class"], "prototype_only")
        self.assertFalse(compute["automotive_qualified"])

    def test_power_target_has_at_least_25_percent_headroom(self):
        budget = self.load("power_budget.json")
        loads = budget["design_loads_w"]
        base_load = sum(loads.values())
        self.assertGreaterEqual(budget["target_dc_dc_capacity_w"], base_load * 1.25)


if __name__ == "__main__":
    unittest.main()
