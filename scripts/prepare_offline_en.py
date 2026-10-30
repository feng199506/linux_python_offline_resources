#!/usr/bin/env python3
"""Prepare Linux x86-64 glibc scientific Python offline environments.

This helper only downloads artifacts and inspects wheel/deb metadata.
It does not install packages, execute downloaded runtimes or source trees,
train, deploy, or modify the host system Python.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from email.parser import Parser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PIP_PYZ = SCRIPTS / "pip.pyz"
ENV_ROOT = ROOT / "environments"
STATE_DIR = ROOT / "state"
CACHE_DIR = STATE_DIR / "pip_cache"
LOG_DIR = STATE_DIR / "logs"
INDEX_DIR = ROOT / "system_dependencies" / "_indexes"
PENDING = ROOT / "pending_not_in_default"
RUNTIME_STANDALONE = ROOT / "runtimes" / "python_build_standalone"
RUNTIME_SOURCE = ROOT / "runtimes" / "cpython_official_source"

PYPI = "https://pypi.org/simple"
TORCH_CPU = "https://download.pytorch.org/whl/cpu"
USER_AGENT = "linux-python-offline-resources/1.0"

# Ubuntu 22.04 glibc is 2.35. Do not fetch wheels that need a newer glibc.
MAX_DEFAULT_GLIBC = (2, 35)
PLATFORMS = [
    "manylinux2014_x86_64",
    "manylinux_2_17_x86_64",
    "manylinux_2_24_x86_64",
    "manylinux_2_27_x86_64",
    "manylinux_2_28_x86_64",
    "manylinux_2_31_x86_64",
    "manylinux_2_34_x86_64",
    "manylinux_2_35_x86_64",
    "linux_x86_64",
    "any",
]
MANYLINUX_GLIBC = {
    "manylinux1": (2, 5),
    "manylinux2010": (2, 12),
    "manylinux2014": (2, 17),
}

BOOTSTRAP = ["pip", "setuptools", "wheel", "packaging"]

# Seed runtime libraries and tools. Closures are resolved per Ubuntu suite.
DEB_SEEDS_RUNTIME = [
    "libgomp1",
    "libgfortran5",
    "libquadmath0",
    "libsndfile1",
    "libasound2",
    "libgl1",
    "libglib2.0-0",
    "libsm6",
    "libxext6",
    "libxrender1",
    "libgomp1",
    "fonts-dejavu-core",
    "graphviz",
    "ffmpeg",
]
DEB_SEEDS_BUILD = [
    "build-essential",
    "pkg-config",
    "libssl-dev",
    "zlib1g-dev",
    "libffi-dev",
    "libbz2-dev",
    "libreadline-dev",
    "libsqlite3-dev",
    "liblzma-dev",
    "libncursesw5-dev",
    "uuid-dev",
    "tk-dev",
    "libgdbm-dev",
    "libgdbm-compat-dev",
]
ASSUMED_PRESENT = {
    "libc6",
    "libgcc-s1",
    "libstdc++6",
    "base-files",
    "base-passwd",
    "bash",
    "dash",
    "coreutils",
    "dpkg",
    "tar",
    "gzip",
    "sed",
    "grep",
    "gawk",
    "findutils",
    "hostname",
    "ncurses-base",
    "libtinfo6",
    "zlib1g",
    "liblzma5",
    "libmd0",
    "libattr1",
    "libacl1",
    "libselinux1",
    "libpcre2-8-0",
    "libpcre3",
    "libcap2",
    "libaudit1",
    "libpam0g",
    "libcrypt1",
    "libzstd1",
    "libbz2-1.0",
    "libgpg-error0",
    "libgcrypt20",
    "libsystemd0",
    "liblz4-1",
    "libcap-ng0",
    "libdebconfclient0",
    "debianutils",
    "init-system-helpers",
    "lsb-base",
    "sensible-utils",
    "ca-certificates",
    "openssl",
    "debconf",
    "perl-base",
    "libdb5.3",
    "libuuid1",
    "libffi8",
    "libffi7",
    "libnsl2",
    "libtirpc3",
    "libtirpc-common",
    "libgssapi-krb5-2",
    "libkrb5-3",
    "libk5crypto3",
    "libkrb5support0",
    "libkeyutils1",
    "libcom-err2",
    "libssl3",
    "libssl3t64",
    "gcc-12-base",
    "gcc-13-base",
    "gcc-14-base",
    "gcc-11-base",
}

UBUNTU_SUITES = {
    "ubuntu_22.04": {
        "codename": "jammy",
        "glibc": "2.35",
        "components": ["main", "universe"],
        "pockets": ["jammy", "jammy-updates", "jammy-security"],
        "seed_runtime": DEB_SEEDS_RUNTIME
        + ["libasound2", "libglib2.0-0", "libssl3", "libncursesw5-dev"],
        "seed_build": DEB_SEEDS_BUILD,
    },
    "ubuntu_24.04": {
        "codename": "noble",
        "glibc": "2.39",
        "components": ["main", "universe"],
        "pockets": ["noble", "noble-updates", "noble-security"],
        "seed_runtime": [
            "libgomp1",
            "libgfortran5",
            "libquadmath0",
            "libsndfile1",
            "libasound2t64",
            "libgl1",
            "libglib2.0-0t64",
            "libsm6",
            "libxext6",
            "libxrender1",
            "fonts-dejavu-core",
            "graphviz",
            "ffmpeg",
        ],
        "seed_build": [
            "build-essential",
            "pkg-config",
            "libssl-dev",
            "zlib1g-dev",
            "libffi-dev",
            "libbz2-dev",
            "libreadline-dev",
            "libsqlite3-dev",
            "liblzma-dev",
            "libncurses-dev",
            "uuid-dev",
            "tk-dev",
            "libgdbm-dev",
            "libgdbm-compat-dev",
        ],
    },
}


def env_spec(
    env_id: str,
    title_cn: str,
    python: str,
    packages: list[str],
    imports: list[str],
    notes_cn: str,
    needs_torch_cpu: bool = False,
    extra_pip: list[str] | None = None,
) -> dict:
    return {
        "id": env_id,
        "title_cn": title_cn,
        "python": python,
        "packages": BOOTSTRAP + packages,
        "imports": imports,
        "notes_cn": notes_cn,
        "needs_torch_cpu": needs_torch_cpu,
        "extra_pip": extra_pip or [],
    }


ENVIRONMENTS = [
    env_spec(
        "01_scientific_notebook_py310",
        "科学计算与 Notebook",
        "3.10",
        [
            "numpy",
            "scipy",
            "pandas",
            "sympy",
            "matplotlib",
            "seaborn",
            "plotly",
            "jupyterlab",
            "ipykernel",
            "ipywidgets",
            "openpyxl",
            "pyarrow",
            "h5py",
            "netCDF4",
            "xarray",
            "pyyaml",
            "requests",
            "httpx",
            "tqdm",
            "joblib",
            "psutil",
            "pytest",
        ],
        ["numpy", "scipy", "pandas", "matplotlib", "jupyterlab", "pyarrow", "h5py", "xarray"],
        "通用数组、表格、绘图与 Notebook。不含深度学习框架。",
    ),
    env_spec(
        "01_scientific_notebook_py312",
        "科学计算与 Notebook（新 Python）",
        "3.12",
        [
            "numpy",
            "scipy",
            "pandas",
            "sympy",
            "matplotlib",
            "seaborn",
            "plotly",
            "jupyterlab",
            "ipykernel",
            "ipywidgets",
            "openpyxl",
            "pyarrow",
            "h5py",
            "netCDF4",
            "xarray",
            "pyyaml",
            "requests",
            "httpx",
            "tqdm",
            "joblib",
            "psutil",
            "pytest",
        ],
        ["numpy", "scipy", "pandas", "matplotlib", "jupyterlab", "pyarrow", "h5py", "xarray"],
        "面向仍受支持的 CPython 3.12 新项目，不与 3.10 环境混装。",
    ),
    env_spec(
        "02_ml_stats_timeseries_em_py310",
        "传统机器学习、统计、时间序列及 EM",
        "3.10",
        [
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "statsmodels",
            "xgboost",
            "lightgbm",
            "catboost",
            "hmmlearn",
            "matplotlib",
            "joblib",
            "threadpoolctl",
        ],
        ["sklearn", "statsmodels", "xgboost", "lightgbm", "catboost", "hmmlearn"],
        "CPU 树模型、统计与隐马尔可夫。不含 PyTorch/TensorFlow。",
    ),
    env_spec(
        "02_ml_stats_timeseries_em_py312",
        "传统机器学习、统计、时间序列及 EM（新 Python）",
        "3.12",
        [
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "statsmodels",
            "xgboost",
            "lightgbm",
            "catboost",
            "hmmlearn",
            "matplotlib",
            "joblib",
            "threadpoolctl",
        ],
        ["sklearn", "statsmodels", "xgboost", "lightgbm", "catboost", "hmmlearn"],
        "CPython 3.12 对应组合。若某包无 3.12 wheel，将记入兼容性问题。",
    ),
    env_spec(
        "03_signal_audio_image_py310",
        "信号、音频与图像处理",
        "3.10",
        [
            "numpy",
            "scipy",
            "pandas",
            "Pillow",
            "opencv-python-headless",
            "scikit-image",
            "albumentations",
            "PyWavelets",
            "librosa",
            "soundfile",
            "mne",
            "wfdb",
            "imageio",
            "tifffile",
        ],
        ["PIL", "cv2", "skimage", "librosa", "soundfile", "mne", "wfdb", "pywt"],
        "默认使用 opencv-python-headless，避免与 GUI OpenCV 冲突。完整音频解码仍可能需要系统 FFmpeg。",
    ),
    env_spec(
        "03_signal_audio_image_py312",
        "信号、音频与图像处理（新 Python）",
        "3.12",
        [
            "numpy",
            "scipy",
            "pandas",
            "Pillow",
            "opencv-python-headless",
            "scikit-image",
            "albumentations",
            "PyWavelets",
            "librosa",
            "soundfile",
            "mne",
            "wfdb",
            "imageio",
            "tifffile",
        ],
        ["PIL", "cv2", "skimage", "librosa", "soundfile", "mne", "wfdb", "pywt"],
        "CPython 3.12 对应组合。",
    ),
    env_spec(
        "04_pytorch_cpu_py310",
        "PyTorch CPU",
        "3.10",
        ["numpy", "torch", "torchvision", "torchaudio"],
        ["torch", "torchvision", "torchaudio", "numpy"],
        "仅 CPU 轮子，来源为 PyTorch 官方 CPU 索引，不含 CUDA。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "04_pytorch_cpu_py312",
        "PyTorch CPU（新 Python）",
        "3.12",
        ["numpy", "torch", "torchvision", "torchaudio"],
        ["torch", "torchvision", "torchaudio", "numpy"],
        "CPython 3.12 + PyTorch CPU。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "05_gpr_bayesopt_py310",
        "GPR 与贝叶斯优化（PyTorch 路线）",
        "3.10",
        ["numpy", "scipy", "pandas", "torch", "gpytorch", "linear_operator", "botorch"],
        ["torch", "gpytorch", "linear_operator", "botorch"],
        "GPyTorch / BoTorch CPU。与 TensorFlow/GPflow 环境分开。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "05_gpr_bayesopt_py312",
        "GPR 与贝叶斯优化（PyTorch 路线，新 Python）",
        "3.12",
        ["numpy", "scipy", "pandas", "torch", "gpytorch", "linear_operator", "botorch"],
        ["torch", "gpytorch", "linear_operator", "botorch"],
        "CPython 3.12 + GPyTorch / BoTorch CPU。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "06_bayesian_mcmc_py310",
        "贝叶斯计算与 Monte Carlo",
        "3.10",
        ["numpy", "scipy", "pandas", "pymc", "arviz", "emcee", "cmdstanpy", "xarray", "matplotlib"],
        ["pymc", "arviz", "emcee", "cmdstanpy", "xarray"],
        "cmdstanpy 仅为 Python 包。CmdStan 编译器/工具链需另装，不在默认 wheel 集合中。",
    ),
    env_spec(
        "06_bayesian_mcmc_py312",
        "贝叶斯计算与 Monte Carlo（新 Python）",
        "3.12",
        ["numpy", "scipy", "pandas", "pymc", "arviz", "emcee", "cmdstanpy", "xarray", "matplotlib"],
        ["pymc", "arviz", "emcee", "cmdstanpy", "xarray"],
        "CPython 3.12 对应组合。Stan 仍为外部依赖。",
    ),
    env_spec(
        "07_tensorflow_cpu_py310",
        "TensorFlow CPU",
        "3.10",
        ["numpy", "tensorflow-cpu", "keras"],
        ["tensorflow", "keras", "numpy"],
        "使用 tensorflow-cpu，不下载 GPU/CUDA 构建。",
    ),
    env_spec(
        "07_tensorflow_cpu_py312",
        "TensorFlow CPU（新 Python）",
        "3.12",
        ["numpy", "tensorflow-cpu", "keras"],
        ["tensorflow", "keras", "numpy"],
        "CPython 3.12 + TensorFlow CPU。",
    ),
    env_spec(
        "07b_gpflow_tf218_py310",
        "GPflow（TensorFlow 2.18 专用）",
        "3.10",
        [
            "numpy<2",
            "gpflow==2.11.2",
            "tensorflow-cpu==2.18.0",
            "tensorflow-probability==0.25.0",
            "tf-keras",
            "scipy",
        ],
        ["gpflow", "tensorflow", "tensorflow_probability"],
        "GPflow 2.11.2 官方测试针对 TensorFlow 2.18 与 TFP 0.25，且 numpy<2。不与 TensorFlow 2.21 环境合并。",
    ),
    env_spec(
        "07b_gpflow_tf218_py312",
        "GPflow（TensorFlow 2.18 专用，新 Python）",
        "3.12",
        [
            "numpy<2",
            "gpflow==2.11.2",
            "tensorflow-cpu==2.18.0",
            "tensorflow-probability==0.25.0",
            "tf-keras",
            "scipy",
        ],
        ["gpflow", "tensorflow", "tensorflow_probability"],
        "若无 cp312 wheel，将记入未完成项。",
    ),
    env_spec(
        "08_rl_basics_py310",
        "强化学习基础",
        "3.10",
        ["numpy", "gymnasium", "stable-baselines3", "tensorboard", "torch", "pandas", "matplotlib"],
        ["gymnasium", "stable_baselines3", "tensorboard", "torch"],
        "不含 Atari ROM、MuJoCo 或大型仿真器。SB3 依赖 PyTorch CPU。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "08_rl_basics_py312",
        "强化学习基础（新 Python）",
        "3.12",
        ["numpy", "gymnasium", "stable-baselines3", "tensorboard", "torch", "pandas", "matplotlib"],
        ["gymnasium", "stable_baselines3", "tensorboard", "torch"],
        "CPython 3.12 对应组合，仍不含大型仿真资源。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "09_huggingface_llm_py310",
        "Hugging Face 与大模型基础",
        "3.10",
        [
            "numpy",
            "torch",
            "transformers",
            "datasets",
            "tokenizers",
            "accelerate",
            "peft",
            "trl",
            "safetensors",
            "huggingface_hub",
            "sentencepiece",
        ],
        ["transformers", "datasets", "tokenizers", "accelerate", "peft", "trl", "safetensors", "torch"],
        "仅库与传递依赖。不含模型权重或数据集。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "09_huggingface_llm_py312",
        "Hugging Face 与大模型基础（新 Python）",
        "3.12",
        [
            "numpy",
            "torch",
            "transformers",
            "datasets",
            "tokenizers",
            "accelerate",
            "peft",
            "trl",
            "safetensors",
            "huggingface_hub",
            "sentencepiece",
        ],
        ["transformers", "datasets", "tokenizers", "accelerate", "peft", "trl", "safetensors", "torch"],
        "CPython 3.12 CPU 基础环境，不含权重。",
        needs_torch_cpu=True,
    ),
    env_spec(
        "10_onnx_api_ui_py310",
        "ONNX CPU、API 与应用界面",
        "3.10",
        [
            "numpy",
            "onnx",
            "onnxruntime",
            "fastapi",
            "uvicorn",
            "pydantic",
            "gradio",
            "streamlit",
            "Pillow",
        ],
        ["onnx", "onnxruntime", "fastapi", "uvicorn", "pydantic", "gradio", "streamlit"],
        "仅 onnxruntime CPU。不与 onnxruntime-gpu 放在同一环境。",
    ),
    env_spec(
        "10_onnx_api_ui_py312",
        "ONNX CPU、API 与应用界面（新 Python）",
        "3.12",
        [
            "numpy",
            "onnx",
            "onnxruntime",
            "fastapi",
            "uvicorn",
            "pydantic",
            "gradio",
            "streamlit",
            "Pillow",
        ],
        ["onnx", "onnxruntime", "fastapi", "uvicorn", "pydantic", "gradio", "streamlit"],
        "CPython 3.12 对应组合。",
    ),
    env_spec(
        "11_optimization_control_py310",
        "优化与控制计算",
        "3.10",
        ["numpy", "scipy", "cvxpy", "osqp", "clarabel", "control", "casadi"],
        ["cvxpy", "osqp", "clarabel", "control", "casadi", "numpy", "scipy"],
        "不含 slycot（通常需编译）。Casadi 使用官方 manylinux wheel。",
    ),
    env_spec(
        "11_optimization_control_py312",
        "优化与控制计算（新 Python）",
        "3.12",
        ["numpy", "scipy", "cvxpy", "osqp", "clarabel", "control", "casadi"],
        ["cvxpy", "osqp", "clarabel", "control", "casadi", "numpy", "scipy"],
        "CPython 3.12 对应组合。",
    ),
]


def ensure_dirs() -> None:
    for p in [
        ENV_ROOT,
        STATE_DIR,
        CACHE_DIR,
        LOG_DIR,
        INDEX_DIR,
        PENDING,
        RUNTIME_STANDALONE,
        RUNTIME_SOURCE,
        ROOT / "system_dependencies" / "ubuntu_22.04" / "runtime_debs",
        ROOT / "system_dependencies" / "ubuntu_22.04" / "build_debs",
        ROOT / "system_dependencies" / "ubuntu_24.04" / "runtime_debs",
        ROOT / "system_dependencies" / "ubuntu_24.04" / "build_debs",
        ROOT / "guides",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state() -> dict:
    path = STATE_DIR / "prepare_state_en.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"completed": {}, "issues": []}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_DIR / "prepare_state_en.json.tmp"
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_DIR / "prepare_state_en.json")


def append_progress(step: str, status: str, detail: str) -> None:
    path = ROOT / "progress_cn.csv"
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["time_utc", "step", "status", "detail"])
        w.writerow([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), step, status, detail])


def download_url(url: str, dest: Path, resume: bool = True) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    cmd = ["wget", "-O", str(tmp), url]
    if resume and tmp.exists():
        cmd = ["wget", "-c", "-O", str(tmp), url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"wget failed for {url}: {proc.stderr[-400:]}")
    tmp.replace(dest)


def pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_wheel_filename(name: str) -> dict | None:
    if not name.endswith(".whl"):
        return None
    stem = name[:-4]
    parts = stem.split("-")
    if len(parts) < 5:
        return None
    py_tag, abi, plat = parts[-3], parts[-2], parts[-1]
    # PEP 427 build tag exists only when there are 6+ hyphen parts.
    # Do not treat versions like 2.14.1+cpu as a build tag.
    if len(parts) >= 6 and re.match(r"^\d[\w.]*$", parts[-4] or ""):
        build = parts[-4]
        version = parts[-5]
        dist = "-".join(parts[:-5])
    else:
        build = ""
        version = parts[-4]
        dist = "-".join(parts[:-4])
    return {
        "filename": name,
        "name": dist,
        "name_norm": pep503(dist),
        "version": version,
        "build": build,
        "python_tag": py_tag,
        "abi": abi,
        "platform": plat,
    }


def manylinux_glibc_from_platform(platform: str) -> tuple[int, int] | None:
    required = (2, 17)
    found = False
    for tag in platform.split("."):
        if tag.startswith("manylinux_"):
            bits = tag.split("_")
            if len(bits) >= 3 and bits[1].isdigit() and bits[2].isdigit():
                cur = (int(bits[1]), int(bits[2]))
                required = cur if not found else max(required, cur)
                found = True
        elif tag in MANYLINUX_GLIBC:
            cur = MANYLINUX_GLIBC[tag]
            required = cur if not found else max(required, cur)
            found = True
    if found:
        return required
    if platform == "any":
        return (0, 0)
    if platform.startswith("linux_"):
        return None
    return None


def glibc_tuple_to_str(t: tuple[int, int] | None) -> str:
    if t is None:
        return "unknown"
    if t == (0, 0):
        return "purelib/any"
    return f"{t[0]}.{t[1]}"


def inspect_wheel(path: Path) -> dict:
    meta = parse_wheel_filename(path.name) or {
        "filename": path.name,
        "name": path.stem,
        "name_norm": pep503(path.stem),
        "version": "",
        "python_tag": "",
        "abi": "",
        "platform": "",
    }
    meta["size_bytes"] = path.stat().st_size
    meta["sha256"] = sha256_file(path)
    meta["requires_python"] = ""
    meta["requires_dist"] = ""
    meta["wheel_tags"] = ""
    meta["root_is_purelib"] = ""
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            md_name = next((n for n in names if n.endswith(".dist-info/METADATA")), None)
            wh_name = next((n for n in names if n.endswith(".dist-info/WHEEL")), None)
            if md_name:
                parsed = Parser().parsestr(zf.read(md_name).decode("utf-8", "replace"))
                meta["name"] = parsed.get("Name", meta["name"])
                meta["name_norm"] = pep503(meta["name"])
                meta["version"] = parsed.get("Version", meta["version"])
                meta["requires_python"] = parsed.get("Requires-Python", "")
                reqs = parsed.get_all("Requires-Dist") or []
                meta["requires_dist"] = " | ".join(reqs[:30])
            if wh_name:
                parsed = Parser().parsestr(zf.read(wh_name).decode("utf-8", "replace"))
                tags = parsed.get_all("Tag") or []
                meta["wheel_tags"] = " ".join(tags)
                meta["root_is_purelib"] = parsed.get("Root-Is-Purelib", "")
    except zipfile.BadZipFile:
        meta["requires_dist"] = "INVALID_ZIP"
    plat = meta.get("platform") or ""
    meta["min_glibc"] = glibc_tuple_to_str(manylinux_glibc_from_platform(plat))
    meta["compatible_default"] = wheel_ok_for_default(meta)
    return meta


def wheel_ok_for_default(meta: dict) -> str:
    plat = meta.get("platform") or ""
    name = meta.get("filename") or ""
    if not name.endswith(".whl"):
        return "no_not_wheel"
    bad = ("win32", "win_amd64", "macosx", "aarch64", "armv7", "ppc64", "s390x", "musllinux", "i686")
    # allow manylinux_*_x86_64 and any and linux_x86_64
    if any(b in plat for b in bad):
        return "no_wrong_platform"
    glibc = manylinux_glibc_from_platform(plat)
    if glibc and glibc > MAX_DEFAULT_GLIBC:
        return "no_glibc_too_new"
    py = meta.get("python_tag") or ""
    if py and not any(tok in py.split(".") for tok in ("py2.py3", "py3", "py2", "cp310", "cp312", "cp3", "abi3")):
        # keep permissive; detailed python check is per-environment
        pass
    return "yes"


def pip_base(dest: Path, python_version: str) -> list[str]:
    tag = python_version.replace(".", "")
    cmd = [
        sys.executable,
        str(PIP_PYZ),
        "download",
        "--dest",
        str(dest),
        "--python-version",
        python_version,
        "--implementation",
        "cp",
        "--abi",
        f"cp{tag}",
        "--abi",
        "abi3",
        "--abi",
        "none",
        "--only-binary",
        ":all:",
        "--cache-dir",
        str(CACHE_DIR),
        "--disable-pip-version-check",
        "--timeout",
        "120",
        "--retries",
        "5",
    ]
    for plat in PLATFORMS:
        cmd.extend(["--platform", plat])
    return cmd


def run_logged(cmd: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write("\n$ " + " ".join(cmd) + "\n")
        fh.flush()
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, text=True)
        fh.write(f"\n[exit {proc.returncode}]\n")
        return proc.returncode


def write_req_file(path: Path, packages: list[str]) -> None:
    path.write_text("\n".join(packages) + "\n", encoding="utf-8")


def wheel_name_version(path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(path) as zf:
        md_name = next((n for n in zf.namelist() if n.endswith(".dist-info/METADATA")), None)
        if md_name:
            parsed = Parser().parsestr(zf.read(md_name).decode("utf-8", "replace"))
            return parsed.get("Name") or path.stem, parsed.get("Version") or ""
    parsed = parse_wheel_filename(path.name)
    if parsed:
        return parsed["name"], parsed["version"]
    return path.stem, ""


def pin_torch_from_wheelhouse(wheelhouse: Path) -> list[str]:
    pins = []
    wanted = {"torch", "torchvision", "torchaudio"}
    found = {}
    for path in sorted(wheelhouse.glob("*.whl")):
        name, version = wheel_name_version(path)
        key = pep503(name)
        if key in wanted and version:
            found[key] = f"{name}=={version}"
    for key in ("torch", "torchvision", "torchaudio"):
        if key in found:
            pins.append(found[key])
    return pins


def is_gpu_python_package(name: str) -> bool:
    n = pep503(name)
    if n in {"onnxruntime-gpu", "tensorflow-gpu", "nvidia-ml-py"}:
        return True
    if n.startswith("nvidia-") or n.startswith("cuda-") or n.startswith("nccl-"):
        return True
    return False


def marker_applies(marker: str, python_version: str) -> bool:
    if not marker or not marker.strip():
        return True
    text = marker.strip()
    if re.search(r"\bextra\s*==", text, re.I):
        return False
    if re.search(r"implementation_name\s*==\s*['\"]pypy['\"]", text, re.I):
        return False

    def flag(pattern: str) -> bool:
        return re.search(pattern, text, re.I) is not None

    if flag(r"sys_platform\s*==\s*['\"]win32['\"]") or flag(r"sys_platform\s*==\s*['\"]darwin['\"]"):
        return False
    if flag(r"platform_system\s*==\s*['\"]Windows['\"]") or flag(r"platform_system\s*==\s*['\"]Darwin['\"]"):
        return False
    if flag(r"os_name\s*==\s*['\"]nt['\"]"):
        return False
    if flag(r"platform_machine\s*==\s*['\"]aarch64['\"]") or flag(r"platform_machine\s*==\s*['\"]arm64['\"]"):
        return False

    ours = tuple(int(x) for x in python_version.split("."))
    for op, raw in re.findall(r"python_version\s*(<=|<|>=|>|==|!=)\s*['\"]([0-9.]+)['\"]", text):
        rhs = tuple(int(x) for x in raw.split("."))
        a = ours + (0,) * (max(len(ours), len(rhs)) - len(ours))
        b = rhs + (0,) * (max(len(ours), len(rhs)) - len(rhs))
        ok = {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b, "==": a == b, "!=": a != b}[op]
        if not ok:
            return False
    return True


def required_runtime_deps(path: Path, python_version: str) -> list[str]:
    names = []
    try:
        with zipfile.ZipFile(path) as zf:
            md_name = next((n for n in zf.namelist() if n.endswith(".dist-info/METADATA")), None)
            if not md_name:
                return []
            parsed = Parser().parsestr(zf.read(md_name).decode("utf-8", "replace"))
            for line in parsed.get_all("Requires-Dist") or []:
                if ";" in line:
                    req, marker = line.split(";", 1)
                else:
                    req, marker = line, ""
                if not marker_applies(marker, python_version):
                    continue
                name = re.split(r"[\s<=>!~\[]", req.strip(), maxsplit=1)[0].strip()
                if name:
                    names.append(pep503(name))
    except zipfile.BadZipFile:
        return []
    return names


def present_wheel_names(wheelhouse: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in wheelhouse.glob("*.whl"):
        parsed = parse_wheel_filename(path.name)
        if parsed and parsed.get("name"):
            found[parsed["name_norm"]] = path
            continue
        name, _ver = wheel_name_version(path)
        found[pep503(name)] = path
    return found


def fill_dependency_closure(env: dict, extra: list[str], log: Path, rounds: int = 8) -> dict:
    """Download runtime Requires-Dist recursively. Never use --no-deps here."""
    env_dir = ENV_ROOT / env["id"]
    wheelhouse = env_dir / "wheelhouse"
    missing_final: list[str] = []
    excluded_gpu: list[str] = []
    added: list[str] = []
    for _ in range(rounds):
        present = present_wheel_names(wheelhouse)
        needed: set[str] = set()
        for path in present.values():
            needed.update(required_runtime_deps(path, env["python"]))
        missing = sorted(n for n in needed if n not in present)
        to_fetch = []
        for name in missing:
            if is_gpu_python_package(name):
                if name not in excluded_gpu:
                    excluded_gpu.append(name)
                continue
            to_fetch.append(name)
        if not to_fetch:
            missing_final = []
            break
        before = {p.name for p in wheelhouse.glob("*.whl")}
        cmd = pip_base(wheelhouse, env["python"]) + extra + to_fetch
        rc = run_logged(cmd, log)
        if rc != 0:
            for name in to_fetch:
                run_logged(pip_base(wheelhouse, env["python"]) + extra + [name], log)
        after = {p.name for p in wheelhouse.glob("*.whl")}
        added.extend(sorted(after - before))
        present = present_wheel_names(wheelhouse)
        missing_final = [n for n in to_fetch if n not in present]
        if not missing_final:
            # one more loop to catch newly added wheels' deps
            continue
    present = present_wheel_names(wheelhouse)
    still = []
    needed_all: set[str] = set()
    for path in present.values():
        needed_all.update(required_runtime_deps(path, env["python"]))
    for name in sorted(needed_all):
        if name in present:
            continue
        if is_gpu_python_package(name):
            if name not in excluded_gpu:
                excluded_gpu.append(name)
            continue
        still.append(name)
    report = {
        "missing_runtime_deps": still,
        "excluded_gpu_deps": excluded_gpu,
        "added_from_closure": added,
        "present_count": len(present),
    }
    (env_dir / "dependency_closure_en.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (env_dir / "missing_runtime_deps_en.txt").write_text("\n".join(still) + ("\n" if still else ""), encoding="utf-8")
    return report


def reject_non_default_wheels(env_dir: Path, wheelhouse: Path) -> list[str]:
    rejected = []
    for whl in list(wheelhouse.glob("*.whl")):
        lower = whl.name.lower()
        gpu_or_wrong = (
            "+cu" in lower
            or "onnxruntime_gpu" in lower
            or "musllinux" in lower
            or "win_amd64" in lower
            or "macosx" in lower
            or "_aarch64" in lower
            or "-aarch64" in lower
            or lower.startswith("nvidia_")
        )
        if gpu_or_wrong and "+cpu" not in lower:
            rejected.append(whl.name)
            reject_dir = env_dir / "rejected_not_default"
            reject_dir.mkdir(exist_ok=True)
            target = reject_dir / whl.name
            if target.exists():
                shutil.move(str(whl), str(reject_dir / (whl.name + ".dup")))
            else:
                shutil.move(str(whl), str(target))
    return rejected


def download_environment(env: dict) -> dict:
    env_dir = ENV_ROOT / env["id"]
    wheelhouse = env_dir / "wheelhouse"
    env_dir.mkdir(parents=True, exist_ok=True)
    wheelhouse.mkdir(parents=True, exist_ok=True)
    marker = env_dir / "download_complete_en.json"
    log = LOG_DIR / f"{env['id']}.log"
    direct = env_dir / "requirements_direct_en.txt"
    write_req_file(direct, env["packages"])
    previous = {}
    if marker.exists():
        try:
            previous = json.loads(marker.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
    complete_enough = (
        previous.get("status") == "downloaded"
        and previous.get("deps_complete") is True
        and not previous.get("failed_packages")
        and any(wheelhouse.glob("*.whl"))
    )

    packages = list(env["packages"])
    extra = list(env.get("extra_pip") or [])
    failed: list[str] = []
    if env.get("needs_torch_cpu"):
        extra = ["--extra-index-url", TORCH_CPU]
        torch_pkgs = [
            p
            for p in ("torch", "torchvision", "torchaudio")
            if any(x == p or x.startswith(p + "==") for x in packages)
        ] or ["torch"]
        # Download torch family AND their runtime dependencies from the CPU index.
        cmd = pip_base(wheelhouse, env["python"]) + [
            "--index-url",
            TORCH_CPU,
            "--extra-index-url",
            PYPI,
            *torch_pkgs,
        ]
        rc = run_logged(cmd, log)
        if rc != 0:
            for pkg in torch_pkgs:
                run_logged(
                    pip_base(wheelhouse, env["python"])
                    + ["--index-url", TORCH_CPU, "--extra-index-url", PYPI, pkg],
                    log,
                )
        pins = pin_torch_from_wheelhouse(wheelhouse)
        if not pins:
            raise RuntimeError(f"{env['id']}: no torch CPU wheels saved")
        rewritten = []
        for p in packages:
            name = re.split(r"[<=>~\[]", p, maxsplit=1)[0]
            if pep503(name) in {"torch", "torchvision", "torchaudio"}:
                continue
            rewritten.append(p)
        packages = rewritten + pins

    if not complete_enough:
        req_tmp = env_dir / "requirements_resolver_en.txt"
        write_req_file(req_tmp, packages)
        cmd = pip_base(wheelhouse, env["python"]) + extra + ["-r", str(req_tmp)]
        rc = run_logged(cmd, log)
        if rc != 0:
            failed = []
            for pkg in packages:
                if not pkg or pkg.startswith("=="):
                    failed.append(pkg or "<empty>")
                    continue
                cmd_one = pip_base(wheelhouse, env["python"]) + extra + [pkg]
                if run_logged(cmd_one, log) != 0:
                    failed.append(pkg)

    rejected = reject_non_default_wheels(env_dir, wheelhouse)
    closure = fill_dependency_closure(env, extra, log)
    rejected.extend(reject_non_default_wheels(env_dir, wheelhouse))
    missing = closure.get("missing_runtime_deps") or []
    deps_complete = not missing
    status = "downloaded" if deps_complete and not failed else "partial"
    result = {
        "status": status,
        "failed_packages": failed,
        "rejected": sorted(set(rejected)),
        "wheel_count": len(list(wheelhouse.glob("*.whl"))),
        "deps_complete": deps_complete,
        "missing_runtime_deps": missing,
        "excluded_gpu_deps": closure.get("excluded_gpu_deps") or [],
        "added_from_closure": closure.get("added_from_closure") or [],
    }
    marker.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def build_lock_and_inventory(env: dict) -> dict:
    env_dir = ENV_ROOT / env["id"]
    wheelhouse = env_dir / "wheelhouse"
    rows = []
    for path in sorted(wheelhouse.glob("*.whl")):
        rows.append(inspect_wheel(path))
    inv = env_dir / "wheel_inventory_cn.csv"
    fields = [
        "name",
        "version",
        "filename",
        "size_bytes",
        "python_tag",
        "abi",
        "platform",
        "min_glibc",
        "requires_python",
        "compatible_default",
        "source",
        "sha256",
        "wheel_tags",
        "requires_dist",
    ]
    with inv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            row["source"] = TORCH_CPU if env.get("needs_torch_cpu") and pep503(row["name"]) in {"torch", "torchvision", "torchaudio"} else PYPI
            w.writerow(row)
    # lock file: unique name==version
    seen = {}
    for row in rows:
        seen[row["name_norm"]] = f"{row['name']}=={row['version']}"
    lock_lines = sorted(seen.values(), key=str.lower)
    (env_dir / "requirements_lock_en.txt").write_text("\n".join(lock_lines) + ("\n" if lock_lines else ""), encoding="utf-8")
    glibcs = []
    for row in rows:
        t = manylinux_glibc_from_platform(row.get("platform") or "")
        if t and t != (0, 0):
            glibcs.append(t)
    min_glibc = max(glibcs) if glibcs else (2, 17)
    total = sum(r["size_bytes"] for r in rows)
    bad = [r["filename"] for r in rows if r.get("compatible_default") != "yes"]
    sdists = [p.name for p in wheelhouse.glob("*.tar.*")] + [p.name for p in wheelhouse.glob("*.zip")]
    return {
        "rows": rows,
        "count": len(rows),
        "total_bytes": total,
        "min_glibc": glibc_tuple_to_str(min_glibc),
        "bad_wheels": bad,
        "sdists": sdists,
        "framework": infer_framework(seen),
    }


def infer_framework(seen: dict) -> str:
    if "tensorflow-cpu" in seen or "tensorflow" in seen:
        if "gpflow" in seen:
            return "GPflow + TensorFlow CPU"
        return "TensorFlow CPU"
    if "torch" in seen:
        if "gpytorch" in seen or "botorch" in seen:
            return "PyTorch CPU + GPyTorch/BoTorch"
        if "transformers" in seen:
            return "PyTorch CPU + Hugging Face"
        if "stable-baselines3" in seen:
            return "PyTorch CPU + SB3"
        return "PyTorch CPU"
    if "onnxruntime" in seen:
        return "ONNX Runtime CPU"
    if "scikit-learn" in seen:
        return "scikit-learn / statsmodels"
    if "cvxpy" in seen:
        return "CVXPY / CasADi"
    if "librosa" in seen or "opencv-python-headless" in seen:
        return "SciPy signal / OpenCV headless"
    if "pymc" in seen:
        return "PyMC / ArviZ"
    return "NumPy / SciPy stack"


def write_install_script(env: dict) -> None:
    env_dir = ENV_ROOT / env["id"]
    major, minor = env["python"].split(".")
    text = f"""#!/usr/bin/env bash
set -euo pipefail

# Offline installer for {env['id']}.
# Does not use sudo, does not modify system Python, does not fall back to PyPI.

ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
WHEELHOUSE="${{ROOT}}/wheelhouse"
LOCK="${{ROOT}}/requirements_lock_en.txt"
VENV_DIR="${{VENV_DIR:-${{ROOT}}/venv}}"
PYTHON_BIN="${{PYTHON_BIN:-}}"

if [[ ! -d "${{WHEELHOUSE}}" ]]; then
  echo "ERROR: wheelhouse missing: ${{WHEELHOUSE}}" >&2
  exit 1
fi
if [[ ! -s "${{LOCK}}" ]]; then
  echo "ERROR: lock file missing: ${{LOCK}}" >&2
  exit 1
fi
if [[ -z "${{PYTHON_BIN}}" ]]; then
  echo "ERROR: set PYTHON_BIN to a CPython {env['python']} x86-64 interpreter." >&2
  echo "Extract python-build-standalone first, for example:" >&2
  echo "  tar -xzf ../../runtimes/python_build_standalone/cpython-{env['python']}*-x86_64-unknown-linux-gnu-install_only.tar.gz -C /tmp" >&2
  echo "  export PYTHON_BIN=/tmp/python/bin/python3" >&2
  exit 1
fi
if [[ ! -x "${{PYTHON_BIN}}" ]]; then
  echo "ERROR: PYTHON_BIN is not executable: ${{PYTHON_BIN}}" >&2
  exit 1
fi

"${{PYTHON_BIN}}" - <<'PY'
import platform, sys
maj, minr = {major}, {minor}
if sys.version_info[:2] != (maj, minr):
    raise SystemExit(f"Need CPython {{maj}}.{{minr}}, got {{sys.version}}")
if sys.maxsize <= 2**32:
    raise SystemExit("Need 64-bit Python")
if platform.machine() not in ("x86_64", "AMD64"):
    raise SystemExit(f"Need x86-64, got {{platform.machine()}}")
PY

export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_FIND_LINKS="${{WHEELHOUSE}}"

if ! "${{PYTHON_BIN}}" -m venv "${{VENV_DIR}}"; then
  echo "venv with pip failed; retrying --without-pip" >&2
  "${{PYTHON_BIN}}" -m venv --without-pip "${{VENV_DIR}}"
fi
VPY="${{VENV_DIR}}/bin/python"
if [[ ! -x "${{VPY}}" ]]; then
  echo "ERROR: venv python missing" >&2
  exit 1
fi

bootstrap_pip() {{
  local pip_whl
  pip_whl="$(ls -1 "${{WHEELHOUSE}}"/pip-*.whl 2>/dev/null | head -n 1 || true)"
  if [[ -z "${{pip_whl}}" ]]; then
    echo "ERROR: no pip wheel in wheelhouse and venv has no pip" >&2
    exit 1
  fi
  "${{VPY}}" - "${{pip_whl}}" "${{WHEELHOUSE}}" <<'PY'
import runpy, sys
whl, find_links = sys.argv[1], sys.argv[2]
sys.path.insert(0, whl)
sys.argv = ["pip", "install", "--no-index", "--find-links", find_links, "pip", "setuptools", "wheel"]
runpy.run_module("pip", run_name="__main__")
PY
}}

if ! "${{VPY}}" -m pip --version >/dev/null 2>&1; then
  bootstrap_pip
fi

"${{VPY}}" -m pip install --no-index --find-links "${{WHEELHOUSE}}" --upgrade pip setuptools wheel
"${{VPY}}" -m pip install --no-index --find-links "${{WHEELHOUSE}}" --no-warn-script-location -r "${{LOCK}}"
"${{VPY}}" -m pip check
echo "Offline install finished: ${{VENV_DIR}}"
echo "Next: ${{VPY}} ${{ROOT}}/check_environment_en.py"
"""
    path = env_dir / "install_offline_en.sh"
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_check_script(env: dict) -> None:
    imports = env["imports"]
    body = f'''#!/usr/bin/env python3
"""Static/runtime checks to run on the *target* Linux after offline install."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = "{env["python"]}"
IMPORTS = {imports!r}
REPORT = Path(__file__).resolve().parent / "check_report_en.json"


def glibc() -> str:
    try:
        return os.confstr("CS_GNU_LIBC_VERSION")
    except Exception:
        return "unknown"


def main() -> int:
    info = {{
        "environment": "{env["id"]}",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "executable": sys.executable,
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "is_64bit": sys.maxsize > 2**32,
        "glibc": glibc(),
        "imports": {{}},
        "pip_check": None,
        "notes": [],
        "passed": True,
    }}
    if sys.version_info[:2] != tuple(int(x) for x in EXPECTED.split(".")):
        info["passed"] = False
        info["notes"].append(f"Python {{EXPECTED}} required")
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
        info["pip_check"] = {{
            "returncode": pip_check.returncode,
            "stdout": pip_check.stdout.strip(),
            "stderr": pip_check.stderr.strip(),
        }}
        if pip_check.returncode != 0:
            info["passed"] = False
    except Exception as exc:
        info["pip_check"] = {{"error": str(exc)}}
        info["passed"] = False

    for name in IMPORTS:
        try:
            mod = __import__(name)
            info["imports"][name] = getattr(mod, "__version__", "imported")
        except Exception as exc:
            info["imports"][name] = f"FAIL: {{exc}}"
            info["passed"] = False

    try:
        import numpy as np
        x = np.arange(9, dtype=np.float64).reshape(3, 3)
        info["numpy_dot"] = float(x.dot(x).sum())
    except Exception as exc:
        info["numpy_dot"] = f"FAIL: {{exc}}"
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
            info["torch"] = f"FAIL: {{exc}}"
            info["passed"] = False

    if "tensorflow" in IMPORTS:
        try:
            import tensorflow as tf
            info["tf_version"] = tf.__version__
            info["tf_gpus"] = [g.name for g in tf.config.list_physical_devices("GPU")]
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            info["tf_matmul_sum"] = float(tf.reduce_sum(tf.matmul(a, a)).numpy())
        except Exception as exc:
            info["tensorflow"] = f"FAIL: {{exc}}"
            info["passed"] = False

    REPORT.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(json.dumps(info, indent=2))
    return 0 if info["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''
    path = ENV_ROOT / env["id"] / "check_environment_en.py"
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def write_readme(env: dict, stats: dict, download_info: dict) -> None:
    env_dir = ENV_ROOT / env["id"]
    status = download_info.get("status")
    failed = download_info.get("failed_packages") or []
    text = f"""# {env['title_cn']}

- 环境编号：`{env['id']}`
- 目标解释器：CPython {env['python']}，Linux x86-64，glibc
- 参考发行版：Ubuntu 22.04 LTS（glibc 2.35）、Ubuntu 24.04 LTS（glibc 2.39）
- 框架：{stats.get('framework', '')}
- wheel 数量：{stats.get('count', 0)}
- wheel 总大小：{stats.get('total_bytes', 0)} 字节
- 由 wheel 标签推断的最低 glibc：{stats.get('min_glibc', '')}
- 本轮状态：{status}（仅下载与静态检查，尚未在目标 Linux 上安装验证）

## 用途与限制

{env['notes_cn']}

本目录是按用途准备的通用 CPU 环境，不是全部历史研究项目的精确复现。
不要与 `windows_python_offline_resources/` 或其他 Linux 组混装。

默认集合 **不适用于**：ARM64、Alpine/musl、非 glibc 系统、GPU/CUDA。
Ubuntu 22.04 需要 glibc ≥ 2.35 且不高于本环境实际 wheel 需求；若最低 glibc 标记 ≤ 2.35，则 22.04 与 24.04 都可作为候选。若某 wheel 需要更新的 glibc，22.04 不可用。

## 离线安装

1. 准备 CPython {env['python']} x86-64 运行时（推荐解压 `runtimes/python_build_standalone/` 中对应 `install_only` 包，或自行从官方源码构建）。
2. 该运行时是 **Astral/indygreg python-build-standalone 第三方构建**，不是 python.org 官方 Linux 二进制。
3. 指定解释器并安装：

```bash
export PYTHON_BIN=/path/to/python{env['python']}
bash ./install_offline_en.sh
"$PYTHON_BIN"/../bin/python -m pip  # 不使用
./venv/bin/python ./check_environment_en.py
```

安装脚本使用 `venv` + `pip install --no-index --find-links wheelhouse`。
失败即停止，不会静默联网，不会修改系统 Python，不会调用 sudo。

## 文件

- `requirements_direct_en.txt`：直接依赖
- `requirements_lock_en.txt`：锁定版本（含传递依赖）
- `wheelhouse/`：完整 wheel
- `wheel_inventory_cn.csv`：包名、版本、来源、大小、平台、最低 glibc
- `install_offline_en.sh`
- `check_environment_en.py`

## 未完成 / 注意

- 失败的直接依赖：{failed if failed else '无'}
- 静态检查判定为不适合默认 Linux x86-64 的 wheel：{stats.get('bad_wheels') or '无'}
- 源码包（不能当 wheel 安装）：{stats.get('sdists') or '无'}
- 系统库（OpenMP、FFmpeg、Graphviz、音频等）见仓库根目录 `external_dependencies_cn.csv` 与 `system_dependencies/`。
- 本轮 **没有** 在目标 Ubuntu 22.04/24.04 上创建 venv 或执行导入检查。
"""
    (env_dir / "README_cn.md").write_text(text, encoding="utf-8")


def parse_packages_gz(path: Path) -> dict:
    pkgs: dict[str, dict] = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        block = []
        for line in fh:
            if line.strip() == "":
                if block:
                    rec = Parser().parsestr("".join(block))
                    name = rec.get("Package")
                    if name:
                        rec_d = {
                            "Package": name,
                            "Version": rec.get("Version", ""),
                            "Filename": rec.get("Filename", ""),
                            "SHA256": rec.get("SHA256", ""),
                            "Size": rec.get("Size", ""),
                            "Depends": rec.get("Depends", ""),
                            "Pre-Depends": rec.get("Pre-Depends", ""),
                            "Provides": rec.get("Provides", ""),
                            "Architecture": rec.get("Architecture", ""),
                        }
                        old = pkgs.get(name)
                        if old is None or rec_d["Version"] > old["Version"]:
                            pkgs[name] = rec_d
                    block = []
            else:
                block.append(line)
    return pkgs


def split_deps(field: str) -> list[str]:
    if not field:
        return []
    out = []
    for part in field.split(","):
        alt = part.split("|")[0]
        name = re.split(r"[\s:(]", alt.strip(), maxsplit=1)[0].strip()
        if name:
            out.append(name)
    return out


def resolve_deb_closure(index: dict, seeds: list[str]) -> tuple[list[str], list[str]]:
    provides: dict[str, str] = {}
    for name, rec in index.items():
        provides[name] = name
        if rec.get("Provides"):
            for item in rec["Provides"].split(","):
                prov = re.split(r"[\s:(]", item.strip(), maxsplit=1)[0].strip()
                provides.setdefault(prov, name)
    chosen: list[str] = []
    missing: list[str] = []
    seen = set()
    stack = list(seeds)
    while stack:
        raw = stack.pop()
        name = provides.get(raw, raw)
        if name in seen:
            continue
        seen.add(name)
        if name in ASSUMED_PRESENT or raw in ASSUMED_PRESENT:
            continue
        rec = index.get(name)
        if rec is None:
            missing.append(raw)
            continue
        chosen.append(name)
        for dep in split_deps(rec.get("Depends", "")) + split_deps(rec.get("Pre-Depends", "")):
            if dep not in seen:
                stack.append(dep)
    return chosen, missing


def download_ubuntu_indexes() -> None:
    base = "http://archive.ubuntu.com/ubuntu/dists"
    for suite, cfg in UBUNTU_SUITES.items():
        for pocket in cfg["pockets"]:
            for comp in cfg["components"]:
                url = f"{base}/{pocket}/{comp}/binary-amd64/Packages.gz"
                dest = INDEX_DIR / suite / pocket / comp / "Packages.gz"
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and dest.stat().st_size > 0:
                    continue
                print(f"index {url}")
                download_url(url, dest)


def merged_index(suite: str) -> dict:
    cfg = UBUNTU_SUITES[suite]
    merged: dict[str, dict] = {}
    for pocket in cfg["pockets"]:
        for comp in cfg["components"]:
            path = INDEX_DIR / suite / pocket / comp / "Packages.gz"
            if not path.exists():
                continue
            part = parse_packages_gz(path)
            for name, rec in part.items():
                rec = dict(rec)
                rec["_pool_base"] = "http://archive.ubuntu.com/ubuntu/"
                rec["_suite"] = suite
                rec["_pocket"] = pocket
                rec["_component"] = comp
                old = merged.get(name)
                if old is None or rec["Version"] > old["Version"]:
                    merged[name] = rec
    return merged


def download_debs(suite: str, kind: str, names: list[str], index: dict) -> tuple[int, int]:
    dest_dir = ROOT / "system_dependencies" / suite / f"{kind}_debs"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    manifest = dest_dir / "deb_manifest_cn.csv"
    rows = []
    for name in names:
        rec = index.get(name)
        if not rec:
            fail += 1
            continue
        url = urljoin("http://archive.ubuntu.com/ubuntu/", rec["Filename"])
        filename = Path(rec["Filename"]).name
        dest = dest_dir / filename
        try:
            download_url(url, dest)
            ok += 1
            rows.append(
                {
                    "package": name,
                    "version": rec.get("Version", ""),
                    "filename": filename,
                    "size": rec.get("Size", ""),
                    "sha256_index": rec.get("SHA256", ""),
                    "url": url,
                    "suite": suite,
                    "kind": kind,
                }
            )
        except Exception as exc:
            fail += 1
            rows.append(
                {
                    "package": name,
                    "version": rec.get("Version", ""),
                    "filename": filename,
                    "size": rec.get("Size", ""),
                    "sha256_index": rec.get("SHA256", ""),
                    "url": f"FAIL:{exc}",
                    "suite": suite,
                    "kind": kind,
                }
            )
    with manifest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["package", "version", "filename", "size", "sha256_index", "url", "suite", "kind"])
        w.writeheader()
        w.writerows(rows)
    return ok, fail


def write_static_docs() -> None:
    (RUNTIME_STANDALONE / "notes_cn.md").write_text(
        """# python-build-standalone 运行时说明

这些文件 **不是** python.org 官方 Linux 二进制。

- 上游项目：https://github.com/astral-sh/python-build-standalone
- 文档：https://docs.astral.sh/python-build-standalone/
- 许可证：项目自身主要为 MIT；内含 CPython（PSF）及其它第三方库许可证，详见上游发行说明
- 构建来源：Astral 发布的 `install_only` 归档，目标三元组 `x86_64-unknown-linux-gnu`
- 最低 glibc（上游文档）：多数目标为 **2.17**（覆盖 Ubuntu 14.04+；本仓库默认参考场景为 Ubuntu 22.04/24.04）
- 选用 `x86_64` 基线构建，不用 `x86_64_v2/v3/v4`，也不用 musl

解压后得到 `python/bin/python3`，可直接作为 `PYTHON_BIN` 创建 venv。
本准备过程 **没有执行** 这些运行时。
""",
        encoding="utf-8",
    )
    (RUNTIME_SOURCE / "build_from_source_cn.md").write_text(
        """# CPython 官方源码包（备选）

`Python-*.tar.xz` 是 python.org 官方源码。**源码包本身不能直接运行。**

从源码构建仍需要目标机器上的编译器与开发库，例如 Ubuntu 上：

```bash
sudo apt install build-essential pkg-config libssl-dev zlib1g-dev libffi-dev \\
  libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev libncurses-dev \\
  uuid-dev tk-dev libgdbm-dev libgdbm-compat-dev
./configure --prefix=/opt/python-3.x.x --enable-optimizations
make -j"$(nproc)"
make install
```

本仓库若提供 `system_dependencies/*/build_debs/`，也只是按 Ubuntu 官方索引解析的 `.deb` 闭包，**不能**替代在对应发行版上用 `dpkg`/`apt` 正确安装，且本轮没有在当前机器安装它们。

官方构建指南：https://devguide.python.org/getting-started/setup-building/
""",
        encoding="utf-8",
    )
    (PENDING / "arm64_cn.md").write_text(
        "# ARM64 待补\n\n默认包集合仅为 Linux x86-64 / glibc。AArch64 运行时与 `manylinux_*_aarch64` wheel 未下载。\n",
        encoding="utf-8",
    )
    (PENDING / "alpine_musl_cn.md").write_text(
        "# Alpine / musl 待补\n\n未下载 `x86_64-unknown-linux-musl` 运行时，也未下载 `musllinux` wheel。不要把 manylinux 包用于 Alpine。\n",
        encoding="utf-8",
    )
    (PENDING / "other_distros_cn.md").write_text(
        "# 其他发行版待补\n\n默认参考 Ubuntu 22.04/24.04。RHEL、Debian、SLES 等需要按各自 glibc 与系统库另做解析，不能直接宣称可用。\n",
        encoding="utf-8",
    )
    (PENDING / "gpu_optional_cn.md").write_text(
        """# GPU 待选（未下载）

硬件型号、驱动和 CUDA 版本未知，因此 **没有** 下载 CUDA/cuDNN 或 GPU wheel。

若目标机器确认具备 NVIDIA GPU，需要单独准备，且不得并入当前 CPU 环境：

- PyTorch：使用与驱动匹配的官方 CUDA 索引（例如 `https://download.pytorch.org/whl/cu128`），版本必须与驱动/CUDA 兼容
- TensorFlow：Linux 原生 GPU 构建与 WSL2 方案不同，需按官方文档单独锁定
- ONNX Runtime：使用 `onnxruntime-gpu`，不要与 `onnxruntime` CPU 混装

在目标机器先采集：`nvidia-smi`、驱动版本、CUDA 版本、GPU 型号，再决定下载哪一套。
""",
        encoding="utf-8",
    )


def write_global_inventories(env_stats: list[dict], issues: list[dict], deb_notes: list[dict]) -> None:
    # runtime inventory
    rt_fields = ["name", "kind", "version", "arch", "filename", "size_bytes", "sha256", "source_url", "license_note", "glibc_min", "official_python_org_binary", "runnable_without_build"]
    rt_rows = [
        {
            "name": "CPython via python-build-standalone",
            "kind": "relocatable_runtime_third_party",
            "version": "3.10.22",
            "arch": "x86_64-unknown-linux-gnu",
            "filename": "cpython-3.10.22+20261001-x86_64-unknown-linux-gnu-install_only.tar.gz",
            "size_bytes": (RUNTIME_STANDALONE / "cpython-3.10.22+20261001-x86_64-unknown-linux-gnu-install_only.tar.gz").stat().st_size,
            "sha256": "d2897121f0d0e41ac7fecc241980d5e33025e608ae85f5c253af5b377182dd79",
            "source_url": "https://github.com/astral-sh/python-build-standalone/releases/tag/20261001",
            "license_note": "Upstream project MIT; bundled CPython PSF + third-party licenses",
            "glibc_min": "2.17 (upstream doc); default scenario Ubuntu 22.04/24.04",
            "official_python_org_binary": "no",
            "runnable_without_build": "yes_after_extract_not_executed_this_round",
        },
        {
            "name": "CPython via python-build-standalone",
            "kind": "relocatable_runtime_third_party",
            "version": "3.12.16",
            "arch": "x86_64-unknown-linux-gnu",
            "filename": "cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz",
            "size_bytes": (RUNTIME_STANDALONE / "cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz").stat().st_size,
            "sha256": "6a79e922e50006b601f29e688407659da1c2b86ebcd4e9c7254cf234be8b89de",
            "source_url": "https://github.com/astral-sh/python-build-standalone/releases/tag/20261026",
            "license_note": "Upstream project MIT; bundled CPython PSF + third-party licenses",
            "glibc_min": "2.17 (upstream doc); default scenario Ubuntu 22.04/24.04",
            "official_python_org_binary": "no",
            "runnable_without_build": "yes_after_extract_not_executed_this_round",
        },
        {
            "name": "CPython official source",
            "kind": "source_tarball",
            "version": "3.10.22",
            "arch": "source",
            "filename": "Python-3.10.22.tar.xz",
            "size_bytes": (RUNTIME_SOURCE / "Python-3.10.22.tar.xz").stat().st_size,
            "sha256": sha256_file(RUNTIME_SOURCE / "Python-3.10.22.tar.xz"),
            "source_url": "https://www.python.org/ftp/python/3.10.22/Python-3.10.22.tar.xz",
            "license_note": "PSF License",
            "glibc_min": "n/a_source",
            "official_python_org_binary": "no_source_only",
            "runnable_without_build": "no",
        },
        {
            "name": "CPython official source",
            "kind": "source_tarball",
            "version": "3.12.16",
            "arch": "source",
            "filename": "Python-3.12.16.tar.xz",
            "size_bytes": (RUNTIME_SOURCE / "Python-3.12.16.tar.xz").stat().st_size,
            "sha256": sha256_file(RUNTIME_SOURCE / "Python-3.12.16.tar.xz"),
            "source_url": "https://www.python.org/ftp/python/3.12.16/Python-3.12.16.tar.xz",
            "license_note": "PSF License",
            "glibc_min": "n/a_source",
            "official_python_org_binary": "no_source_only",
            "runnable_without_build": "no",
        },
    ]
    with (ROOT / "runtime_inventory_cn.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rt_fields)
        w.writeheader()
        w.writerows(rt_rows)

    pkg_fields = ["environment", "python", "name", "version", "filename", "size_bytes", "platform", "min_glibc", "source", "compatible_default"]
    with (ROOT / "package_inventory_cn.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=pkg_fields)
        w.writeheader()
        for item in env_stats:
            for row in item.get("rows") or []:
                w.writerow(
                    {
                        "environment": item["id"],
                        "python": item["python"],
                        "name": row.get("name"),
                        "version": row.get("version"),
                        "filename": row.get("filename"),
                        "size_bytes": row.get("size_bytes"),
                        "platform": row.get("platform"),
                        "min_glibc": row.get("min_glibc"),
                        "source": row.get("source"),
                        "compatible_default": row.get("compatible_default"),
                    }
                )

    issue_fields = ["environment", "severity", "item", "detail"]
    with (ROOT / "compatibility_issues_cn.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=issue_fields)
        w.writeheader()
        for issue in issues:
            w.writerow(issue)

    ext_fields = ["component", "category", "needed_by", "ubuntu_22.04", "ubuntu_24.04", "offline_status", "official_docs", "notes_cn"]
    ext_rows = [
        {
            "component": "glibc",
            "category": "c_runtime",
            "needed_by": "all_wheels_and_runtimes",
            "ubuntu_22.04": "libc6 2.35, assumed present",
            "ubuntu_24.04": "libc6 2.39, assumed present",
            "offline_status": "not_downloaded_base_system",
            "official_docs": "distro base",
            "notes_cn": "默认 wheel 按最高 manylinux_2_35 选择，覆盖 22.04/24.04。",
        },
        {
            "component": "OpenMP libgomp",
            "category": "c_runtime",
            "needed_by": "numpy/sklearn/xgboost/lightgbm 等",
            "ubuntu_22.04": "libgomp1",
            "ubuntu_24.04": "libgomp1",
            "offline_status": "runtime_debs_if_resolved",
            "official_docs": "https://packages.ubuntu.com/libgomp1",
            "notes_cn": "多数 manylinux wheel 已捆绑；仍登记系统包。",
        },
        {
            "component": "libgfortran",
            "category": "c_runtime",
            "needed_by": "scipy 等",
            "ubuntu_22.04": "libgfortran5",
            "ubuntu_24.04": "libgfortran5",
            "offline_status": "runtime_debs_if_resolved",
            "official_docs": "https://packages.ubuntu.com/libgfortran5",
            "notes_cn": "scipy 的 manylinux wheel 通常捆绑 Fortran 运行库。",
        },
        {
            "component": "FFmpeg",
            "category": "audio_video",
            "needed_by": "librosa/部分音视频 I/O",
            "ubuntu_22.04": "ffmpeg",
            "ubuntu_24.04": "ffmpeg",
            "offline_status": "runtime_debs_if_resolved",
            "official_docs": "https://ffmpeg.org/",
            "notes_cn": "Python 包安装完成不等于系统 FFmpeg 已具备。",
        },
        {
            "component": "Graphviz",
            "category": "graphics",
            "needed_by": "部分可视化、模型图",
            "ubuntu_22.04": "graphviz",
            "ubuntu_24.04": "graphviz",
            "offline_status": "runtime_debs_if_resolved",
            "official_docs": "https://graphviz.org/download/",
            "notes_cn": "python-graphviz 只是绑定，需要系统 graphviz 可执行文件。",
        },
        {
            "component": "libsndfile",
            "category": "audio",
            "needed_by": "soundfile",
            "ubuntu_22.04": "libsndfile1",
            "ubuntu_24.04": "libsndfile1",
            "offline_status": "runtime_debs_if_resolved",
            "official_docs": "https://github.com/bastibe/python-soundfile",
            "notes_cn": "wheel 可能捆绑；系统库作后备。",
        },
        {
            "component": "CmdStan",
            "category": "compiler_toolchain",
            "needed_by": "06_bayesian_mcmc / cmdstanpy",
            "ubuntu_22.04": "not_in_default",
            "ubuntu_24.04": "not_in_default",
            "offline_status": "not_downloaded",
            "official_docs": "https://mc-stan.org/cmdstanpy/",
            "notes_cn": "仅下载了 cmdstanpy wheel。Stan 需 C++ 工具链，单列待补。",
        },
        {
            "component": "CUDA / GPU driver",
            "category": "gpu",
            "needed_by": "可选 PyTorch/TF/ORT GPU",
            "ubuntu_22.04": "unknown_hardware",
            "ubuntu_24.04": "unknown_hardware",
            "offline_status": "not_downloaded",
            "official_docs": "https://docs.nvidia.com/cuda/",
            "notes_cn": "硬件未知，不下载多套 CUDA。见 pending_not_in_default/gpu_optional_cn.md。",
        },
        {
            "component": "CPython build toolchain",
            "category": "compiler_toolchain",
            "needed_by": "官方源码构建备选",
            "ubuntu_22.04": "build-essential 及开发库",
            "ubuntu_24.04": "build-essential 及开发库",
            "offline_status": "build_debs_if_resolved",
            "official_docs": "https://devguide.python.org/getting-started/setup-building/",
            "notes_cn": "源码包不能直接运行。未在本机 apt install。",
        },
        {
            "component": "slycot",
            "category": "python_optional_compile",
            "needed_by": "python-control 部分功能",
            "ubuntu_22.04": "needs_build",
            "ubuntu_24.04": "needs_build",
            "offline_status": "not_downloaded",
            "official_docs": "https://python-control.readthedocs.io/",
            "notes_cn": "无稳定通用 wheel 时不纳入默认集合。",
        },
    ]
    for note in deb_notes:
        ext_rows.append(note)
    with (ROOT / "external_dependencies_cn.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ext_fields)
        w.writeheader()
        w.writerows(ext_rows)

    lines = [
        "# Linux 通用科研 Python 离线环境总览",
        "",
        "默认目标：**Linux x86-64 + glibc**，参考 Ubuntu 22.04/24.04 LTS，**CPU**。",
        "这不是“全部 Linux”环境。ARM64、musl、其他发行版、GPU 见 `pending_not_in_default/`。",
        "",
        "Windows 资源在 `windows_python_offline_resources/`，两套安装包不混用。",
        "",
        "## Python 运行时",
        "",
        "| 版本 | 类型 | 文件 | 官方 python.org 二进制 | 本轮是否执行 |",
        "| --- | --- | --- | --- | --- |",
        "| 3.10.22 | python-build-standalone 第三方可解压运行时 | `runtimes/python_build_standalone/cpython-3.10.22+20261001-x86_64-unknown-linux-gnu-install_only.tar.gz` | 否 | 否 |",
        "| 3.12.16 | python-build-standalone 第三方可解压运行时 | `runtimes/python_build_standalone/cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz` | 否 | 否 |",
        "| 3.10.22 | CPython 官方源码 | `runtimes/cpython_official_source/Python-3.10.22.tar.xz` | 否（源码） | 否 |",
        "| 3.12.16 | CPython 官方源码 | `runtimes/cpython_official_source/Python-3.12.16.tar.xz` | 否（源码） | 否 |",
        "",
        "选择依据：3.10 已于 2026-10-01 结束上游支持，仅作兼容环境；3.12 安全支持至 2028-10，科学计算 wheel 覆盖较 3.13/3.14 更稳。",
        "",
        "## 环境分组",
        "",
        "| 目录 | Python | 框架 | wheel 数 | 总字节 | 最低 glibc | 下载状态 | 目标机安装验证 |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for item in env_stats:
        lines.append(
            f"| `{item['id']}` | {item['python']} | {item.get('framework','')} | {item.get('count',0)} | {item.get('total_bytes',0)} | {item.get('min_glibc','')} | {item.get('status','')} | 未做 |"
        )
    lines += [
        "",
        "## 离线安装步骤（目标 Linux）",
        "",
        "1. 确认 `uname -m` 为 `x86_64`，`ldd --version` 显示 glibc ≥ 本环境最低要求，且发行版为 glibc（非 musl）。",
        "2. 解压对应 python-build-standalone：`tar -xzf runtimes/python_build_standalone/cpython-*.tar.gz`",
        "3. `export PYTHON_BIN=/path/to/python/bin/python3`",
        "4. 进入某一 `environments/<id>/`，执行 `bash install_offline_en.sh`",
        "5. 用该 venv 运行 `check_environment_en.py`",
        "6. 按需用发行版包管理器安装 `external_dependencies_cn.csv` 中的系统库。当前机器 **没有** apt install。",
        "",
        "## 静态检查与未完成",
        "",
        "- 已做：下载、wheel 文件名/METADATA/manylinux 标签检查、Ubuntu Packages 索引解析。",
        "- 未做：解压或执行运行时、创建 venv、导入测试、训练、部署、GPU 包下载。",
        "- 系统 `.deb` 若已下载，也 **不能** 宣称跨发行版离线系统依赖已经齐备；22.04 与 24.04 必须分别安装对应目录中的包。",
        "",
    ]
    (ROOT / "environments_overview_cn.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    readme = """# Linux 通用科研 Python 离线资源

目录：`linux_python_offline_resources/`

本仓库按用途准备 **Linux x86-64 / glibc / CPU** 科研 Python 离线环境，与 `windows_python_offline_resources/` 独立，不混用安装包。

- 总览：`environments_overview_cn.md`
- 运行时清单：`runtime_inventory_cn.csv`
- 包清单：`package_inventory_cn.csv`
- 系统/外部依赖：`external_dependencies_cn.csv`
- 兼容性问题：`compatibility_issues_cn.csv`
- 准备脚本：`scripts/prepare_offline_en.py`（支持断点续跑）

默认参考 Ubuntu 22.04 与 24.04 LTS。不要声称适用于全部 Linux。
"""
    (ROOT / "README_cn.md").write_text(readme, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-group", action="append", default=[])
    parser.add_argument("--skip-debs", action="store_true")
    args = parser.parse_args()
    ensure_dirs()
    write_static_docs()
    state = load_state()
    issues: list[dict] = []

    if not PIP_PYZ.exists():
        raise SystemExit("pip.pyz missing")

    selected = ENVIRONMENTS
    if args.only_group:
        selected = [e for e in ENVIRONMENTS if e["id"] in args.only_group]
        if not selected:
            raise SystemExit("no matching groups")

    deb_notes: list[dict] = []
    if not args.skip_debs:
        try:
            download_ubuntu_indexes()
            for suite, cfg in UBUNTU_SUITES.items():
                idx = merged_index(suite)
                if not idx:
                    issues.append({"environment": suite, "severity": "system", "item": "packages_index", "detail": "index missing"})
                    continue
                for kind, seeds in (("runtime", cfg["seed_runtime"]), ("build", cfg["seed_build"])):
                    names, missing = resolve_deb_closure(idx, seeds)
                    (ROOT / "system_dependencies" / suite / f"{kind}_closure_en.txt").write_text(
                        "\n".join(names) + "\n", encoding="utf-8"
                    )
                    (ROOT / "system_dependencies" / suite / f"{kind}_missing_en.txt").write_text(
                        "\n".join(missing) + "\n", encoding="utf-8"
                    )
                    ok, fail = download_debs(suite, kind, names, idx)
                    append_progress(f"debs_{suite}_{kind}", "ok" if fail == 0 else "partial", f"ok={ok} fail={fail} missing_names={len(missing)}")
                    deb_notes.append(
                        {
                            "component": f"{suite}_{kind}_debs",
                            "category": "deb_closure",
                            "needed_by": kind,
                            "ubuntu_22.04": f"see system_dependencies/{suite}" if suite.endswith("22.04") else "",
                            "ubuntu_24.04": f"see system_dependencies/{suite}" if suite.endswith("24.04") else "",
                            "offline_status": f"downloaded={ok}; fail={fail}; unresolved={len(missing)}",
                            "official_docs": "http://archive.ubuntu.com/ubuntu/",
                            "notes_cn": "按官方 Packages 索引解析。未在本机安装。不能当作所有 glibc 发行版通用。",
                        }
                    )
                    for m in missing:
                        issues.append({"environment": suite, "severity": "system", "item": m, "detail": f"unresolved in {kind} closure"})
        except Exception as exc:
            append_progress("debs", "failed", str(exc))
            issues.append({"environment": "system", "severity": "system", "item": "deb_resolve", "detail": str(exc)})
            deb_notes.append(
                {
                    "component": "ubuntu_debs",
                    "category": "deb_closure",
                    "needed_by": "runtime_and_build",
                    "ubuntu_22.04": "use official apt documentation",
                    "ubuntu_24.04": "use official apt documentation",
                    "offline_status": "not_complete",
                    "official_docs": "https://packages.ubuntu.com/",
                    "notes_cn": f"未能安全完成解析或下载：{exc}。不宣称系统依赖已离线齐备。",
                }
            )

    env_stats: list[dict] = []
    for env in selected:
        print(f"=== {env['id']} ===", flush=True)
        append_progress(env["id"], "start", env["title_cn"])
        try:
            info = download_environment(env)
            stats = build_lock_and_inventory(env)
            write_install_script(env)
            write_check_script(env)
            write_readme(env, stats, info)
            row = {
                "id": env["id"],
                "python": env["python"],
                "title_cn": env["title_cn"],
                "status": info.get("status"),
                **{k: stats[k] for k in ("count", "total_bytes", "min_glibc", "framework", "bad_wheels", "sdists", "rows")},
            }
            env_stats.append(row)
            if info.get("failed_packages"):
                for pkg in info["failed_packages"]:
                    issues.append({"environment": env["id"], "severity": "python", "item": pkg, "detail": "no compatible binary wheel under default linux x86-64 tags"})
            for pkg in info.get("missing_runtime_deps") or []:
                issues.append({"environment": env["id"], "severity": "dependency", "item": pkg, "detail": "runtime Requires-Dist not present in wheelhouse after closure download"})
            for pkg in info.get("excluded_gpu_deps") or []:
                issues.append({"environment": env["id"], "severity": "gpu_excluded", "item": pkg, "detail": "GPU/NVIDIA transitive dependency excluded from default CPU set"})
            for bad in stats.get("bad_wheels") or []:
                issues.append({"environment": env["id"], "severity": "wheel_tag", "item": bad, "detail": "static tag check not default-compatible"})
            append_progress(env["id"], info.get("status") or "ok", f"wheels={stats['count']} bytes={stats['total_bytes']}")
            state["completed"][env["id"]] = info
            state["issues"] = issues
            save_state(state)
        except Exception as exc:
            append_progress(env["id"], "failed", str(exc))
            issues.append({"environment": env["id"], "severity": "error", "item": "download", "detail": str(exc)})
            env_stats.append(
                {
                    "id": env["id"],
                    "python": env["python"],
                    "title_cn": env["title_cn"],
                    "status": "failed",
                    "count": 0,
                    "total_bytes": 0,
                    "min_glibc": "",
                    "framework": "",
                    "rows": [],
                }
            )
            state["issues"] = issues
            save_state(state)
            continue

    # If only-group, still rewrite inventories from existing env dirs when possible.
    if args.only_group:
        all_stats = []
        for env in ENVIRONMENTS:
            env_dir = ENV_ROOT / env["id"]
            if not (env_dir / "wheelhouse").exists():
                continue
            if env["id"] in {e["id"] for e in selected}:
                all_stats.extend([s for s in env_stats if s["id"] == env["id"]])
            elif (env_dir / "download_complete_en.json").exists():
                stats = build_lock_and_inventory(env)
                info = json.loads((env_dir / "download_complete_en.json").read_text())
                all_stats.append(
                    {
                        "id": env["id"],
                        "python": env["python"],
                        "title_cn": env["title_cn"],
                        "status": info.get("status"),
                        **{k: stats[k] for k in ("count", "total_bytes", "min_glibc", "framework", "bad_wheels", "sdists", "rows")},
                    }
                )
        env_stats = all_stats or env_stats

    write_global_inventories(env_stats, issues, deb_notes)
    save_state(state)
    append_progress("all", "finished_pass", f"groups={len(env_stats)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

