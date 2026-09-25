import unittest
from http import HTTPStatus

from axle.config import AxleConfig
from axle.server import AxleApp


class ServerPolicyTests(unittest.TestCase):
    def test_unknown_motion_blocks_manual_request_before_model_call(self):
        app = AxleApp(AxleConfig(motion_state="unknown"))
        status, body = app.assistant("hello")
        self.assertEqual(status, HTTPStatus.LOCKED)
        self.assertEqual(body["error"], "manual_interaction_locked")

    def test_moving_motion_blocks_manual_request(self):
        app = AxleApp(AxleConfig(motion_state="moving"))
        status, _ = app.assistant("hello")
        self.assertEqual(status, HTTPStatus.LOCKED)

    def test_parked_empty_request_rejected_without_model_call(self):
        app = AxleApp(AxleConfig(motion_state="parked"))
        status, body = app.assistant("   ")
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(body["error"], "empty_text")


if __name__ == "__main__":
    unittest.main()
