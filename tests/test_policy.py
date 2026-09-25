import unittest
from axle.policy import MotionState, VoiceTrigger, policy_for, voice_trigger_allowed

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

    def test_touch_voice_trigger_is_parked_only(self):
        self.assertTrue(voice_trigger_allowed(policy_for(MotionState.PARKED), VoiceTrigger.TOUCH))
        self.assertFalse(voice_trigger_allowed(policy_for(MotionState.MOVING), VoiceTrigger.TOUCH))
        self.assertFalse(voice_trigger_allowed(policy_for(MotionState.UNKNOWN), VoiceTrigger.TOUCH))

    def test_hands_free_voice_triggers_remain_available(self):
        moving = policy_for(MotionState.MOVING)
        self.assertTrue(voice_trigger_allowed(moving, VoiceTrigger.WAKE_WORD))
        self.assertTrue(voice_trigger_allowed(moving, VoiceTrigger.HARDWARE_BUTTON))

if __name__=="__main__":
    unittest.main()
