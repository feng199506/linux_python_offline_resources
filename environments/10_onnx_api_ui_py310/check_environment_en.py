#!/usr/bin/env python3
"""Static/runtime checks to run on the *target* Linux after offline install."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = "3.10"
IMPORTS = ['onnx', 'onnxruntime', 'fastapi', 'uvicorn', 'pydantic', 'gradio', 'streamlit']
REPORT = Path(__file__).resolve().parent / "check_report_en.json"


def glibc() -> str:
    try:
        return os.confstr("CS_GNU_LIBC_VERSION")
    except Exception:
        return "unknown"


def main() -> int:
    info = {
        "environment": "10_onnx_api_ui_py310",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "executable": sys.executable,
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "is_64bit": sys.maxsize > 2**32,
        "glibc": glibc(),
        "imports": {},
        "pip_check": None,
        "notes": [],
        "passed": True,
    }
    if sys.version_info[:2] != tuple(int(x) for x in EXPECTED.split(".")):
        info["passed"] = False
        info["notes"].append(f"Python {EXPECTED} required")
    if platform.machine() not in ("x86_64", "AMD64"):
        info["passed"] = False
        info["notes"].append("x86-64 required")
    try:
        pip_check = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            check=False,
        )
        info["pip_check"] = {
            "returncode": pip_check.returncode,
            "stdout": pip_check.stdout.strip(),
            "stderr": pip_check.stderr.strip(),
        }
        if pip_check.returncode != 0:
            info["passed"] = False
    except Exception as exc:
        info["pip_check"] = {"error": str(exc)}
        info["passed"] = False

    for name in IMPORTS:
        try:
            mod = __import__(name)
            info["imports"][name] = getattr(mod, "__version__", "imported")
        except Exception as exc:
            info["imports"][name] = f"FAIL: {exc}"
            info["passed"] = False

    try:
        import numpy as np
        x = np.arange(9, dtype=np.float64).reshape(3, 3)
        info["numpy_dot"] = float(x.dot(x).sum())
    except Exception as exc:
        info["numpy_dot"] = f"FAIL: {exc}"
        info["passed"] = False

    if "torch" in IMPORTS:
        try:
            import torch
            info["torch_cuda_available"] = bool(torch.cuda.is_available())
            t = torch.ones((2, 2))
            info["torch_cpu_matmul"] = float(t.matmul(t).sum())
            if torch.cuda.is_available():
                info["notes"].append("CUDA is visible; this environment was prepared as CPU-only.")
        except Exception as exc:
            info["torch"] = f"FAIL: {exc}"
            info["passed"] = False

    if "tensorflow" in IMPORTS:
        try:
            import tensorflow as tf
            info["tf_version"] = tf.__version__
            info["tf_gpus"] = [g.name for g in tf.config.list_physical_devices("GPU")]
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            info["tf_matmul_sum"] = float(tf.reduce_sum(tf.matmul(a, a)).numpy())
        except Exception as exc:
            info["tensorflow"] = f"FAIL: {exc}"
            info["passed"] = False

    REPORT.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return 0 if info["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
