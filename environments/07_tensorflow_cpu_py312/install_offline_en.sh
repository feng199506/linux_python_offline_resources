#!/usr/bin/env bash
set -euo pipefail

# Offline installer for 07_tensorflow_cpu_py312.
# Does not use sudo, does not modify system Python, does not fall back to PyPI.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELHOUSE="${ROOT}/wheelhouse"
LOCK="${ROOT}/requirements_lock_en.txt"
VENV_DIR="${VENV_DIR:-${ROOT}/venv}"
PYTHON_BIN="${PYTHON_BIN:-}"

if [[ ! -d "${WHEELHOUSE}" ]]; then
  echo "ERROR: wheelhouse missing: ${WHEELHOUSE}" >&2
  exit 1
fi
if [[ ! -s "${LOCK}" ]]; then
  echo "ERROR: lock file missing: ${LOCK}" >&2
  exit 1
fi
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "ERROR: set PYTHON_BIN to a CPython 3.12 x86-64 interpreter." >&2
  echo "Extract python-build-standalone first, for example:" >&2
  echo "  tar -xzf ../../runtimes/python_build_standalone/cpython-3.12*-x86_64-unknown-linux-gnu-install_only.tar.gz -C /tmp" >&2
  echo "  export PYTHON_BIN=/tmp/python/bin/python3" >&2
  exit 1
fi
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: PYTHON_BIN is not executable: ${PYTHON_BIN}" >&2
  exit 1
fi

"${PYTHON_BIN}" - <<'PY'
import platform, sys
maj, minr = 3, 12
if sys.version_info[:2] != (maj, minr):
    raise SystemExit(f"Need CPython {maj}.{minr}, got {sys.version}")
if sys.maxsize <= 2**32:
    raise SystemExit("Need 64-bit Python")
if platform.machine() not in ("x86_64", "AMD64"):
    raise SystemExit(f"Need x86-64, got {platform.machine()}")
PY

export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_FIND_LINKS="${WHEELHOUSE}"

if ! "${PYTHON_BIN}" -m venv "${VENV_DIR}"; then
  echo "venv with pip failed; retrying --without-pip" >&2
  "${PYTHON_BIN}" -m venv --without-pip "${VENV_DIR}"
fi
VPY="${VENV_DIR}/bin/python"
if [[ ! -x "${VPY}" ]]; then
  echo "ERROR: venv python missing" >&2
  exit 1
fi

bootstrap_pip() {
  local pip_whl
  pip_whl="$(ls -1 "${WHEELHOUSE}"/pip-*.whl 2>/dev/null | head -n 1 || true)"
  if [[ -z "${pip_whl}" ]]; then
    echo "ERROR: no pip wheel in wheelhouse and venv has no pip" >&2
    exit 1
  fi
  "${VPY}" - "${pip_whl}" "${WHEELHOUSE}" <<'PY'
import runpy, sys
whl, find_links = sys.argv[1], sys.argv[2]
sys.path.insert(0, whl)
sys.argv = ["pip", "install", "--no-index", "--find-links", find_links, "pip", "setuptools", "wheel"]
runpy.run_module("pip", run_name="__main__")
PY
}

if ! "${VPY}" -m pip --version >/dev/null 2>&1; then
  bootstrap_pip
fi

"${VPY}" -m pip install --no-index --find-links "${WHEELHOUSE}" --upgrade pip setuptools wheel
"${VPY}" -m pip install --no-index --find-links "${WHEELHOUSE}" --no-warn-script-location -r "${LOCK}"
"${VPY}" -m pip check
echo "Offline install finished: ${VENV_DIR}"
echo "Next: ${VPY} ${ROOT}/check_environment_en.py"
