from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Protocol
import shutil
import subprocess
import tempfile


class VoiceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class VoiceBusy(RuntimeError):
    pass


class VoiceBackendError(RuntimeError):
    pass


@dataclass(frozen=True)
class VoiceTurn:
    transcript: str
    answer: str


class VoiceBackend(Protocol):
    def start_capture(self, wav_path: Path) -> None: ...
    def stop_capture(self) -> None: ...
    def cancel_capture(self) -> None: ...
    def transcribe(self, wav_path: Path) -> str: ...
    def synthesize(self, text: str, wav_path: Path) -> None: ...
    def play(self, wav_path: Path) -> None: ...


def render_command(template: tuple[str, ...], **values: str) -> list[str]:
    return [part.format_map(values) for part in template]


class VoiceRuntime:
    def __init__(
        self,
        backend: VoiceBackend,
        responder: Callable[[str], str],
        work_root: Path,
    ) -> None:
        self.backend = backend
        self.responder = responder
        self.work_root = work_root
        self.state = VoiceState.IDLE
        self._session_dir: Path | None = None
        self._input_wav: Path | None = None
        self._output_wav: Path | None = None

    def start(self) -> None:
        if self.state is not VoiceState.IDLE:
            raise VoiceBusy(f"voice runtime is {self.state.value}")

        self.work_root.mkdir(parents=True, exist_ok=True)
        session = Path(tempfile.mkdtemp(prefix="turn-", dir=self.work_root))
        self._session_dir = session
        self._input_wav = session / "input.wav"
        self._output_wav = session / "reply.wav"
        try:
            self.backend.start_capture(self._input_wav)
        except Exception:
            self._cleanup_session()
            raise
        self.state = VoiceState.LISTENING

    def _cleanup_session(self) -> None:
        if self._session_dir is not None:
            shutil.rmtree(self._session_dir, ignore_errors=True)
        self._session_dir = None
        self._input_wav = None
        self._output_wav = None

    def cancel(self) -> None:
        try:
            if self.state is VoiceState.LISTENING:
                self.backend.cancel_capture()
        finally:
            self._cleanup_session()
            self.state = VoiceState.IDLE

    def stop_and_respond(self) -> VoiceTurn:
        if self.state is not VoiceState.LISTENING:
            raise VoiceBusy(f"voice runtime is {self.state.value}")
        assert self._input_wav is not None
        assert self._output_wav is not None

        try:
            self.backend.stop_capture()
            self.state = VoiceState.PROCESSING
            transcript = self.backend.transcribe(self._input_wav).strip()
            if not transcript:
                self.state = VoiceState.IDLE
                return VoiceTurn(transcript="", answer="")
            answer = self.responder(transcript).strip()
            if not answer:
                self.state = VoiceState.IDLE
                return VoiceTurn(transcript=transcript, answer="")

            self.state = VoiceState.SPEAKING
            self.backend.synthesize(answer, self._output_wav)
            self.backend.play(self._output_wav)
            self.state = VoiceState.IDLE
            return VoiceTurn(transcript=transcript, answer=answer)
        except Exception:
            self.state = VoiceState.ERROR
            raise
        finally:
            self._cleanup_session()


class LocalVoiceBackend:
    def __init__(
        self,
        capture_command: tuple[str, ...],
        stt_command: tuple[str, ...],
        tts_command: tuple[str, ...],
        playback_command: tuple[str, ...],
        stt_model: str,
        tts_model: str,
        popen_factory=subprocess.Popen,
        runner=subprocess.run,
        command_timeout_seconds: float = 120.0,
    ) -> None:
        self.capture_command = capture_command
        self.stt_command = stt_command
        self.tts_command = tts_command
        self.playback_command = playback_command
        self.stt_model = stt_model
        self.tts_model = tts_model
        self.popen_factory = popen_factory
        self.runner = runner
        self.command_timeout_seconds = command_timeout_seconds
        self._capture = None

    def _run(self, command: list[str], **kwargs):
        try:
            return self.runner(command, **kwargs)
        except (OSError, subprocess.SubprocessError) as exc:
            executable = command[0] if command else "<empty>"
            raise VoiceBackendError(
                f"voice backend command failed: {executable}"
            ) from exc

    def start_capture(self, wav_path: Path) -> None:
        if self._capture is not None:
            raise VoiceBusy("capture is already active")
        command = render_command(
            self.capture_command,
            wav=str(wav_path),
            model=self.stt_model,
            out=str(wav_path.with_suffix("")),
            text="",
        )
        try:
            self._capture = self.popen_factory(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            executable = command[0] if command else "<empty>"
            raise VoiceBackendError(
                f"voice capture command failed: {executable}"
            ) from exc
    def _stop_capture_process(self) -> None:
        if self._capture is None:
            raise VoiceBackendError("capture is not active")
        process = self._capture
        self._capture = None
        try:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        except (OSError, subprocess.SubprocessError) as exc:
            raise VoiceBackendError("voice capture process stop failed") from exc

    def stop_capture(self) -> None:
        self._stop_capture_process()

    def cancel_capture(self) -> None:
        if self._capture is None:
            return
        self._stop_capture_process()

    def transcribe(self, wav_path: Path) -> str:
        output_base = wav_path.parent / "transcript"
        command = render_command(
            self.stt_command,
            wav=str(wav_path),
            model=self.stt_model,
            out=str(output_base),
            text="",
        )
        self._run(
            command,
            check=True,
            timeout=self.command_timeout_seconds,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        transcript_path = Path(str(output_base) + ".txt")
        if not transcript_path.is_file():
            raise VoiceBackendError("whisper.cpp did not produce transcript text")
        return transcript_path.read_text(encoding="utf-8").strip()
    def synthesize(self, text: str, wav_path: Path) -> None:
        command = render_command(
            self.tts_command,
            wav=str(wav_path),
            model=self.tts_model,
            out=str(wav_path.with_suffix("")),
            text=text,
        )
        self._run(
            command,
            check=True,
            timeout=self.command_timeout_seconds,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not wav_path.is_file():
            raise VoiceBackendError("Piper did not produce reply audio")

    def play(self, wav_path: Path) -> None:
        command = render_command(
            self.playback_command,
            wav=str(wav_path),
            model=self.tts_model,
            out=str(wav_path.with_suffix("")),
            text="",
        )
        self._run(
            command,
            check=True,
            timeout=self.command_timeout_seconds,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
