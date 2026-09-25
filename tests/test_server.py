import unittest
from http import HTTPStatus

from axle.config import AxleConfig
from axle.server import AxleApp
from axle.voice import VoiceState, VoiceTurn


class FakeVoiceRuntime:
    def __init__(self):
        self.state = VoiceState.IDLE
        self.started = 0

    def start(self):
        self.started += 1
        self.state = VoiceState.LISTENING

    def stop_and_respond(self):
        self.state = VoiceState.IDLE
        return VoiceTurn("where are we", "Local answer")

    def cancel(self):
        self.state = VoiceState.IDLE


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

    def test_touch_voice_start_is_locked_while_moving(self):
        voice = FakeVoiceRuntime()
        app = AxleApp(AxleConfig(
            motion_state="moving",
            voice_enabled=True,
            voice_stt_model="/models/whisper.bin",
            voice_tts_model="voice",
        ), voice_runtime=voice)
        status, body = app.voice_start("touch")
        self.assertEqual(status, HTTPStatus.LOCKED)
        self.assertEqual(body["error"], "voice_trigger_locked")
        self.assertEqual(voice.started, 0)

    def test_hardware_button_voice_start_is_allowed_while_moving(self):
        voice = FakeVoiceRuntime()
        app = AxleApp(AxleConfig(
            motion_state="moving",
            voice_enabled=True,
            voice_stt_model="/models/whisper.bin",
            voice_tts_model="voice",
        ), voice_runtime=voice)
        status, body = app.voice_start("hardware_button")
        self.assertEqual(status, HTTPStatus.ACCEPTED)
        self.assertEqual(body["state"], "listening")
        self.assertEqual(voice.started, 1)
    def test_voice_stop_returns_transcript_and_answer(self):
        voice = FakeVoiceRuntime()
        app = AxleApp(AxleConfig(
            motion_state="parked",
            voice_enabled=True,
            voice_stt_model="/models/whisper.bin",
            voice_tts_model="voice",
        ), voice_runtime=voice)
        app.voice_start("touch")
        status, body = app.voice_stop()
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(body["transcript"], "where are we")
        self.assertEqual(body["answer"], "Local answer")
        self.assertEqual(body["state"], "idle")


if __name__ == "__main__":
    unittest.main()
