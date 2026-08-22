#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"

cd "${ROOT_DIR}"

uv sync --dev

PYBIND11_DIR="$(uv run --no-sync python -m pybind11 --cmakedir)"

uv run --no-sync cmake \
    -S "${ROOT_DIR}" \
    -B "${BUILD_DIR}" \
    -Dpybind11_DIR="${PYBIND11_DIR}" \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

echo "Generated: ${BUILD_DIR}/compile_commands.json"
echo "clangd will read it through .clangd (CompilationDatabase: build)."
