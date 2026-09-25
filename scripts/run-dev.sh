#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
exec env PYTHONPATH=src python3 -m axle.server --config config/axle.example.toml
