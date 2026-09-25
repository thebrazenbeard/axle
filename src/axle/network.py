from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Callable


@dataclass(frozen=True)
class Link:
    device: str
    kind: str
    state: str
    connection: str

    @property
    def connected(self) -> bool:
        return self.state == "connected"


@dataclass(frozen=True)
class NetworkSnapshot:
    links: tuple[Link, ...]

    @property
    def has_uplink(self) -> bool:
        return any(link.connected and link.kind in {"wifi", "ethernet", "gsm", "bridge"} for link in self.links)

    @property
    def likely_phone_tether(self) -> bool:
        for link in self.links:
            name = link.connection.lower()
            if link.connected and (
                "hotspot" in name
                or "tether" in name
                or link.kind == "gsm"
                or (link.kind == "ethernet" and link.device.startswith(("usb", "enx")))
            ):
                return True
        return False


def parse_nmcli(text: str) -> NetworkSnapshot:
    links: list[Link] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 3)
        if len(parts) != 4:
            continue
        links.append(Link(*(part.strip() for part in parts)))
    return NetworkSnapshot(tuple(links))


def inspect_network(
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> NetworkSnapshot:
    try:
        result = runner(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return NetworkSnapshot(())

    if result.returncode != 0:
        return NetworkSnapshot(())
    return parse_nmcli(result.stdout)
