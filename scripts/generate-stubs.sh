#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/src/game_solver"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TEMP_DIR}"' EXIT

cd "${ROOT_DIR}"

# uv sync builds the editable extension before stubgen imports it.
uv sync --dev --reinstall-package game-solver-practice

uv run --no-sync pybind11-stubgen \
    game_solver._core \
    --output-dir "${TEMP_DIR}"

install -m 0644 \
    "${TEMP_DIR}/game_solver/_core.pyi" \
    "${OUTPUT_DIR}/_core.pyi"

echo "Generated: ${OUTPUT_DIR}/_core.pyi"
