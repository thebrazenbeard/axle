from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class AxleConfig:
    host: str = "127.0.0.1"
    port: int = 8787
    ui_dir: str = "ui"
    llm_base_url: str = "http://127.0.0.1:8080"
    llm_model: str = "local"
    llm_timeout_seconds: float = 30.0
    motion_state: str = "unknown"
    allow_cloud_fallback: bool = False

    voice_enabled: bool = False
    voice_work_dir: str = "/var/lib/axle/voice"
    voice_stt_model: str = ""
    voice_tts_model: str = ""
    voice_command_timeout_seconds: float = 120.0
    voice_capture_command: tuple[str, ...] = (
        "pw-record", "--rate=16000", "--channels=1", "--format=s16", "{wav}",
    )
    voice_stt_command: tuple[str, ...] = (
        "whisper-cli", "-m", "{model}", "-f", "{wav}", "-otxt", "-of", "{out}", "-nt",
    )
    voice_tts_command: tuple[str, ...] = (
        "python3", "-m", "piper", "-m", "{model}", "-f", "{wav}", "--", "{text}",
    )
    voice_playback_command: tuple[str, ...] = ("pw-play", "{wav}")

    @staticmethod
    def _command(section: dict, key: str, default: tuple[str, ...]) -> tuple[str, ...]:
        raw = section.get(key, default)
        if not isinstance(raw, list | tuple) or not all(isinstance(item, str) for item in raw):
            raise ValueError(f"{key} must be an array of strings")
        return tuple(raw)

    @classmethod
    def from_toml(cls, path: str | Path) -> "AxleConfig":
        with open(path, "rb") as handle:
            raw = tomllib.load(handle)

        server = raw.get("server", {})
        ai = raw.get("ai", {})
        safety = raw.get("safety", {})
        voice = raw.get("voice", {})

        return cls(
            host=str(server.get("host", cls.host)),
            port=int(server.get("port", cls.port)),
            ui_dir=str(server.get("ui_dir", cls.ui_dir)),
            llm_base_url=str(ai.get("llm_base_url", cls.llm_base_url)).rstrip("/"),
            llm_model=str(ai.get("llm_model", cls.llm_model)),
            llm_timeout_seconds=float(ai.get("llm_timeout_seconds", cls.llm_timeout_seconds)),
            motion_state=str(safety.get("motion_state", cls.motion_state)).lower(),
            allow_cloud_fallback=bool(ai.get("allow_cloud_fallback", cls.allow_cloud_fallback)),
            voice_enabled=bool(voice.get("enabled", cls.voice_enabled)),
            voice_work_dir=str(voice.get("work_dir", cls.voice_work_dir)),
            voice_stt_model=str(voice.get("stt_model", cls.voice_stt_model)),
            voice_tts_model=str(voice.get("tts_model", cls.voice_tts_model)),
            voice_command_timeout_seconds=float(
                voice.get("command_timeout_seconds", cls.voice_command_timeout_seconds)
            ),
            voice_capture_command=cls._command(
                voice, "capture_command", cls.voice_capture_command
            ),
            voice_stt_command=cls._command(voice, "stt_command", cls.voice_stt_command),
            voice_tts_command=cls._command(voice, "tts_command", cls.voice_tts_command),
            voice_playback_command=cls._command(
                voice, "playback_command", cls.voice_playback_command
            ),
        )
