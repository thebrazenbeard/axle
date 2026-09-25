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

    @classmethod
    def from_toml(cls, path: str | Path) -> "AxleConfig":
        with open(path, "rb") as handle:
            raw = tomllib.load(handle)

        server = raw.get("server", {})
        ai = raw.get("ai", {})
        safety = raw.get("safety", {})

        return cls(
            host=str(server.get("host", cls.host)),
            port=int(server.get("port", cls.port)),
            ui_dir=str(server.get("ui_dir", cls.ui_dir)),
            llm_base_url=str(ai.get("llm_base_url", cls.llm_base_url)).rstrip("/"),
            llm_model=str(ai.get("llm_model", cls.llm_model)),
            llm_timeout_seconds=float(ai.get("llm_timeout_seconds", cls.llm_timeout_seconds)),
            motion_state=str(safety.get("motion_state", cls.motion_state)).lower(),
            allow_cloud_fallback=bool(ai.get("allow_cloud_fallback", cls.allow_cloud_fallback)),
        )
