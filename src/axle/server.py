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
from axle.policy import MotionState, policy_for


class AxleApp:
    def __init__(self, config: AxleConfig) -> None:
        self.config = config
        self.llm = LocalLlmClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            timeout_seconds=config.llm_timeout_seconds,
        )

    @property
    def policy(self):
        return policy_for(MotionState.parse(self.config.motion_state))

    def status(self) -> dict:
        network = inspect_network()
        policy = self.policy
        return {
            "name": "AXLE",
            "version": "0.1.0",
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

        def do_GET(self):
            if urlparse(self.path).path == "/api/status":
                self._json(HTTPStatus.OK, app.status())
                return
            return super().do_GET()

        def do_POST(self):
            if urlparse(self.path).path != "/api/assistant":
                self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16_384:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                text = str(payload.get("text", ""))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
                return

            status, response = app.assistant(text)
            self._json(status, response)

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
