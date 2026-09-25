import tempfile
import unittest
from pathlib import Path

from axle.voice import LocalVoiceBackend, VoiceBusy, VoiceRuntime, VoiceState, render_command


class FakeBackend:
    def __init__(self, transcript="turn the music down"):
        self.transcript = transcript
        self.events = []
        self.capture_path = None

    def start_capture(self, wav_path: Path) -> None:
        self.capture_path = wav_path
        self.events.append(("start", wav_path.name))

    def stop_capture(self) -> None:
        self.events.append(("stop", None))

    def cancel_capture(self) -> None:
        self.events.append(("cancel", None))

    def transcribe(self, wav_path: Path) -> str:
        self.events.append(("transcribe", wav_path.name))
        return self.transcript
    def synthesize(self, text: str, wav_path: Path) -> None:
        self.events.append(("synthesize", text))
        wav_path.write_bytes(b"RIFFfake")

    def play(self, wav_path: Path) -> None:
        self.events.append(("play", wav_path.name))


class VoiceRuntimeTests(unittest.TestCase):
    def test_local_turn_runs_capture_stt_model_tts_playback(self):
        backend = FakeBackend()
        with tempfile.TemporaryDirectory() as td:
            runtime = VoiceRuntime(backend, lambda text: f"heard: {text}", Path(td))
            runtime.start()
            self.assertEqual(runtime.state, VoiceState.LISTENING)
            turn = runtime.stop_and_respond()

        self.assertEqual(turn.transcript, "turn the music down")
        self.assertEqual(turn.answer, "heard: turn the music down")
        self.assertEqual(runtime.state, VoiceState.IDLE)
        self.assertEqual([event[0] for event in backend.events],
                         ["start", "stop", "transcribe", "synthesize", "play"])

    def test_second_start_is_rejected_while_listening(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = VoiceRuntime(FakeBackend(), lambda text: text, Path(td))
            runtime.start()
            with self.assertRaises(VoiceBusy):
                runtime.start()
            runtime.cancel()
    def test_empty_transcript_does_not_call_model(self):
        calls = []
        with tempfile.TemporaryDirectory() as td:
            runtime = VoiceRuntime(
                FakeBackend(transcript="   "),
                lambda text: calls.append(text) or text,
                Path(td),
            )
            runtime.start()
            turn = runtime.stop_and_respond()

        self.assertEqual(turn.transcript, "")
        self.assertEqual(turn.answer, "")
        self.assertEqual(calls, [])
        self.assertEqual(runtime.state, VoiceState.IDLE)

    def test_command_templates_are_rendered_without_shell_parsing(self):
        rendered = render_command(
            ("whisper-cli", "-m", "{model}", "-f", "{wav}", "-of", "{out}"),
            model="/models/base.en.bin",
            wav="/tmp/in.wav",
            out="/tmp/transcript",
        )
        self.assertEqual(
            rendered,
            ["whisper-cli", "-m", "/models/base.en.bin", "-f", "/tmp/in.wav",
             "-of", "/tmp/transcript"],
        )


class FakeProcess:
    def __init__(self, command):
        self.command = command
        self.terminated = False

    def terminate(self):
        self.terminated = True

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self.terminated = True


class LocalVoiceBackendTests(unittest.TestCase):
    def test_subprocess_backend_uses_explicit_argument_vectors(self):
        commands = []
        process_holder = {}

        def popen_factory(command, **kwargs):
            commands.append(command)
            process_holder["process"] = FakeProcess(command)
            return process_holder["process"]
        def runner(command, **kwargs):
            commands.append(command)
            if command[0] == "whisper-cli":
                out = Path(command[command.index("-of") + 1] + ".txt")
                out.write_text("hello axle\n", encoding="utf-8")
            elif command[0] == "piper":
                wav = Path(command[command.index("-f") + 1])
                wav.write_bytes(b"RIFFreply")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            backend = LocalVoiceBackend(
                capture_command=("pw-record", "--rate=16000", "--channels=1", "{wav}"),
                stt_command=("whisper-cli", "-m", "{model}", "-f", "{wav}", "-otxt", "-of", "{out}"),
                tts_command=("piper", "-m", "{model}", "-f", "{wav}", "--", "{text}"),
                playback_command=("pw-play", "{wav}"),
                stt_model="/models/base.en.bin",
                tts_model="en_US-lessac-medium",
                popen_factory=popen_factory,
                runner=runner,
            )
            input_wav = root / "input.wav"
            reply_wav = root / "reply.wav"
            backend.start_capture(input_wav)
            backend.stop_capture()
            transcript = backend.transcribe(input_wav)
            backend.synthesize("hello back", reply_wav)
            backend.play(reply_wav)

        self.assertEqual(transcript, "hello axle")
        self.assertTrue(process_holder["process"].terminated)
        self.assertEqual(commands[0][-1], str(input_wav))
        self.assertEqual(commands[1][0], "whisper-cli")
        self.assertEqual(commands[2][-1], "hello back")
        self.assertEqual(commands[3], ["pw-play", str(reply_wav)])
        self.assertTrue(all(isinstance(command, list) for command in commands))


if __name__ == "__main__":
    unittest.main()
