from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from axle.config import AxleConfig
from axle.llm import LocalLlmClient, LocalModelUnavailable
from axle.network import inspect_network
from axle.policy import (
    MotionState,
    VoiceTrigger,
    policy_for,
    voice_trigger_allowed,
)
from axle.voice import (
    LocalVoiceBackend,
    VoiceBackendError,
    VoiceBusy,
    VoiceRuntime,
)


class AxleApp:
    def __init__(self, config: AxleConfig, voice_runtime=None) -> None:
        self.config = config
        self.llm = LocalLlmClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            timeout_seconds=config.llm_timeout_seconds,
        )
        if voice_runtime is not None:
            self.voice = voice_runtime
        elif config.voice_enabled:
            self.voice = self._build_voice_runtime()
        else:
            self.voice = None
    def _build_voice_runtime(self) -> VoiceRuntime:
        backend = LocalVoiceBackend(
            capture_command=self.config.voice_capture_command,
            stt_command=self.config.voice_stt_command,
            tts_command=self.config.voice_tts_command,
            playback_command=self.config.voice_playback_command,
            stt_model=self.config.voice_stt_model,
            tts_model=self.config.voice_tts_model,
            command_timeout_seconds=self.config.voice_command_timeout_seconds,
        )
        return VoiceRuntime(
            backend=backend,
            responder=self.llm.chat,
            work_root=Path(self.config.voice_work_dir),
        )

    @property
    def policy(self):
        return policy_for(MotionState.parse(self.config.motion_state))

    def _voice_status(self) -> dict:
        return {
            "enabled": self.config.voice_enabled,
            "configured": bool(
                self.config.voice_stt_model and self.config.voice_tts_model
            ),
            "state": self.voice.state.value if self.voice is not None else "disabled",
        }

    def status(self) -> dict:
        network = inspect_network()
        policy = self.policy
        return {
            "name": "AXLE",
            "version": "0.2.0",
            "motion": policy.motion.value,
            "policy": {
                "manual_text_enabled": policy.manual_text_enabled,
                "rich_visual_interaction_enabled": policy.rich_visual_interaction_enabled,
                "voice_interaction_enabled": policy.voice_interaction_enabled,
                "vehicle_write_enabled": policy.vehicle_write_enabled,
                "reason": policy.reason,
            },
            "local_ai": {
                "base_url": self.config.llm_base_url,
                "healthy": self.llm.health(),
                "cloud_fallback_enabled": self.config.allow_cloud_fallback,
            },
            "voice": self._voice_status(),
            "network": {
                "uplink": network.has_uplink,
                "likely_phone_tether": network.likely_phone_tether,
                "links": [
                    {
                        "device": link.device,
                        "type": link.kind,
                        "state": link.state,
                        "connection": link.connection,
                    }
                    for link in network.links
                ],
            },
        }

    def assistant(self, text: str) -> tuple[int, dict]:
        policy = self.policy
        if not policy.manual_text_enabled:
            return HTTPStatus.LOCKED, {
                "error": "manual_interaction_locked",
                "message": policy.reason,
            }

        cleaned = text.strip()
        if not cleaned:
            return HTTPStatus.BAD_REQUEST, {"error": "empty_text"}

        try:
            answer = self.llm.chat(cleaned)
        except LocalModelUnavailable as exc:
            return HTTPStatus.SERVICE_UNAVAILABLE, {
                "error": "local_ai_unavailable",
                "message": "The local model is unavailable. AXLE will not silently route this request to a cloud model.",
                "detail": str(exc),
            }

        return HTTPStatus.OK, {"answer": answer, "source": "local_model"}
    def voice_start(self, trigger_value: str) -> tuple[int, dict]:
        if not self.config.voice_enabled or self.voice is None:
            return HTTPStatus.SERVICE_UNAVAILABLE, {"error": "voice_disabled"}

        try:
            trigger = VoiceTrigger(trigger_value)
        except ValueError:
            return HTTPStatus.BAD_REQUEST, {"error": "invalid_voice_trigger"}

        if not voice_trigger_allowed(self.policy, trigger):
            return HTTPStatus.LOCKED, {
                "error": "voice_trigger_locked",
                "message": "Touch-triggered voice is parked-only; use wake word or hardware button while moving.",
            }

        if not self.config.voice_stt_model or not self.config.voice_tts_model:
            return HTTPStatus.SERVICE_UNAVAILABLE, {
                "error": "voice_models_unconfigured"
            }

        try:
            self.voice.start()
        except VoiceBusy as exc:
            return HTTPStatus.CONFLICT, {
                "error": "voice_busy",
                "detail": str(exc),
            }
        return HTTPStatus.ACCEPTED, {"state": self.voice.state.value}

    def voice_stop(self) -> tuple[int, dict]:
        if not self.config.voice_enabled or self.voice is None:
            return HTTPStatus.SERVICE_UNAVAILABLE, {"error": "voice_disabled"}

        try:
            turn = self.voice.stop_and_respond()
        except VoiceBusy as exc:
            return HTTPStatus.CONFLICT, {"error": "voice_busy", "detail": str(exc)}
        except LocalModelUnavailable as exc:
            return HTTPStatus.SERVICE_UNAVAILABLE, {
                "error": "local_ai_unavailable",
                "detail": str(exc),
            }
        except VoiceBackendError as exc:
            return HTTPStatus.BAD_GATEWAY, {
                "error": "voice_backend_failure",
                "detail": str(exc),
            }
        return HTTPStatus.OK, {
            "state": self.voice.state.value,
            "transcript": turn.transcript,
            "answer": turn.answer,
        }
    def voice_cancel(self) -> tuple[int, dict]:
        if not self.config.voice_enabled or self.voice is None:
            return HTTPStatus.SERVICE_UNAVAILABLE, {"error": "voice_disabled"}
        self.voice.cancel()
        return HTTPStatus.OK, {"state": self.voice.state.value}


def make_handler(app: AxleApp, ui_dir: str):
    root = str(Path(ui_dir).resolve())

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root, **kwargs)

        def _json(self, status: int, payload: dict) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16_384:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            return payload

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/status":
                self._json(HTTPStatus.OK, app.status())
                return
            if path == "/api/voice/status":
                self._json(HTTPStatus.OK, app._voice_status())
                return
            return super().do_GET()
        def do_POST(self):
            path = urlparse(self.path).path

            if path == "/api/assistant":
                try:
                    payload = self._read_json()
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
                    return
                status, response = app.assistant(str(payload.get("text", "")))
                self._json(status, response)
                return

            if path == "/api/voice/start":
                try:
                    payload = self._read_json()
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
                    return
                status, response = app.voice_start(str(payload.get("trigger", "")))
                self._json(status, response)
                return

            if path == "/api/voice/stop":
                status, response = app.voice_stop()
                self._json(status, response)
                return

            if path == "/api/voice/cancel":
                status, response = app.voice_cancel()
                self._json(status, response)
                return

            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def log_message(self, format: str, *args) -> None:
            print(f"[axle] {self.address_string()} - {format % args}")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AXLE Core")
    parser.add_argument("--config", default="config/axle.example.toml")
    args = parser.parse_args()

    config = AxleConfig.from_toml(args.config)
    app = AxleApp(config)
    server = ThreadingHTTPServer((config.host, config.port), make_handler(app, config.ui_dir))
    print(f"AXLE listening on http://{config.host}:{config.port}")
    print(f"Motion policy: {app.policy.motion.value} — {app.policy.reason}")
    server.serve_forever()


if __name__ == "__main__":
    main()
