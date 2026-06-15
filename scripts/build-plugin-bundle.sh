#!/usr/bin/env bash
# Build a self-contained Stash plugin bundle under ./bundle/stash2fs/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUNDLE_DIR="${ROOT}/bundle/stash2fs"

rm -rf "${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}"

uv sync
uv pip install --target "${BUNDLE_DIR}" -e "${ROOT}"

cp "${ROOT}/stash2fs.yml" "${BUNDLE_DIR}/"
cp "${ROOT}/stash2fs_plugin.py" "${BUNDLE_DIR}/"

echo "Plugin bundle written to ${BUNDLE_DIR}"
