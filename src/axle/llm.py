from __future__ import annotations

from dataclasses import dataclass
import json
from urllib import error, request


SYSTEM_PROMPT = """You are AXLE, a local in-vehicle assistant.
Keep spoken-style responses concise and useful.
Never claim control of the vehicle.
Do not imply that model output authorizes any vehicle-bus write.
When driving context is uncertain, prefer low-distraction interaction.
"""


class LocalModelUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class LocalLlmClient:
    base_url: str
    model: str
    timeout_seconds: float = 30.0

    def health(self) -> bool:
        for suffix in ("/health", "/v1/health"):
            try:
                with request.urlopen(self.base_url + suffix, timeout=1.5) as response:
                    if response.status == 200:
                        return True
            except (error.URLError, TimeoutError, OSError):
                continue
        return False

    def chat(self, user_text: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.4,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url + "/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise LocalModelUnavailable(str(exc)) from exc

        try:
            return str(raw["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LocalModelUnavailable("Local model returned an unexpected response shape") from exc
