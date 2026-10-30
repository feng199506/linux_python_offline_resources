#!/usr/bin/env bash
# Append signal-processing wheels onto original 03_signal_audio_image_py310 venv.
set -euo pipefail
SUPP="$(cd "$(dirname "$0")" && pwd)"
ORIG_WH="${1:-$SUPP/../../environments/03_signal_audio_image_py310/wheelhouse}"
STATS_WH="${2:-$SUPP/../../environments/13_stats_timeseries_py310/wheelhouse}"
VENV_PY="${VENV_PY:-$SUPP/../../environments/03_signal_audio_image_py310/.venv/bin/python}"
if [ ! -x "$VENV_PY" ]; then echo "venv python not found: $VENV_PY" >&2; exit 1; fi
FIND=(--find-links "$SUPP/packages_wheel")
if [ -d "$ORIG_WH" ]; then FIND+=(--find-links "$ORIG_WH"); fi
if [ -d "$STATS_WH" ]; then FIND+=(--find-links "$STATS_WH"); fi
"$VENV_PY" -m pip install --no-index "${FIND[@]}" -r "$SUPP/requirements_supplement_en.txt"
echo "sdist in packages_sdist_unbuilt is NOT installed (unbuilt)."
