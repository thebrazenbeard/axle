import unittest
from axle.policy import MotionState, policy_for

class PolicyTests(unittest.TestCase):
    def test_parked_allows_manual_but_never_vehicle_write(self):
        policy=policy_for(MotionState.PARKED)
        self.assertTrue(policy.manual_text_enabled)
        self.assertTrue(policy.voice_interaction_enabled)
        self.assertFalse(policy.vehicle_write_enabled)

    def test_moving_disables_manual(self):
        policy=policy_for(MotionState.MOVING)
        self.assertFalse(policy.manual_text_enabled)
        self.assertFalse(policy.rich_visual_interaction_enabled)
        self.assertTrue(policy.voice_interaction_enabled)
        self.assertFalse(policy.vehicle_write_enabled)

    def test_unknown_fails_closed(self):
        policy=policy_for(MotionState.UNKNOWN)
        self.assertFalse(policy.manual_text_enabled)
        self.assertFalse(policy.vehicle_write_enabled)

    def test_invalid_motion_parses_unknown(self):
        self.assertEqual(MotionState.parse("nonsense"),MotionState.UNKNOWN)

if __name__=="__main__":
    unittest.main()
