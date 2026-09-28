from __future__ import annotations

import compileall
import json
from pathlib import Path
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"


def main() -> int:
    sys.path.insert(0, str(SRC))

    if not compileall.compile_dir(SRC, quiet=1):
        print("AXLE source compile failed")
        return 1
    if not compileall.compile_dir(TESTS, quiet=1):
        print("AXLE test compile failed")
        return 1

    for path in sorted((ROOT / "hardware").glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))

    for path in (
        ROOT / "pyproject.toml",
        ROOT / "config" / "axle.example.toml",
        ROOT / "config" / "axle.jetson.example.toml",
    ):
        with path.open("rb") as stream:
            tomllib.load(stream)

    suite = unittest.defaultTestLoader.discover(str(TESTS))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    print("AXLE repository validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
