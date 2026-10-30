#!/usr/bin/env python3
"""Download host-side and board-side embedded-dev offline kits.

Does not flash hardware, install into the system, or compile-verify.
Does not re-audit existing scientific Python environments.
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import subprocess
import sys
import time
from email.parser import Parser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path("/root/linux_python_offline_resources")
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_offline_en import (  # noqa: E402
    CACHE_DIR,
    PIP_PYZ,
    PLATFORMS,
    append_progress,
    download_url,
    pip_base,
    run_logged,
    sha256_file,
)

EMB = ROOT / "embedded"
IDX = EMB / "indexes"
HOST = EMB / "host_linux_x86_64"
BOARDS = EMB / "boards"
FW = EMB / "firmware"
INV = EMB / "inventories"
LOG = ROOT / "state" / "logs" / "embedded.log"

HOST_HINTS = (
    "x86_64-linux-gnu",
    "x86_64-pc-linux-gnu",
    "linux-amd64",
    "linux64",
    "x86_64-linux",
)

# Basic Arduino cores only. Do not pull every third-party board package.
ARDUINO_PLATFORMS = [
    ("package_index.json", "arduino", "avr"),
    ("package_index.json", "arduino", "megaavr"),
    ("package_index.json", "arduino", "renesas_uno"),
    ("package_esp32_index.json", "esp32", "esp32"),
    ("package_esp8266com_index.json", "esp8266", "esp8266"),
]

# Chip support libs kept for mainstream ESP32/S2/S3/C3; others listed as not-in-basic-kit.
ESP32_BASIC_TOOLS = {
    "esp-x32",
    "esp-rv32",
    "xtensa-esp-elf-gdb",
    "riscv32-esp-elf-gdb",
    "openocd-esp32",
    "esptool_py",
    "mkspiffs",
    "mklittlefs",
    "dfu-util",
    "esp32-libs",
    "esp32s2-libs",
    "esp32s3-libs",
    "esp32c3-libs",
}

HOST_PY_PACKAGES = [
    "pyserial",
    "pyusb",
    "hidapi",
    "pyftdi",
    "python-can",
    "canopen",
    "paho-mqtt",
    "pymodbus",
    "minimalmodbus",
    "bleak",
    "pymavlink",
    "esptool",
    "mpremote",
    "rshell",
    "adafruit-ampy",
    "mpy-cross",
    "intelhex",
    "pyserial-asyncio",
    "python-periphery",
    "progressbar2",
    "requests",
    "pyspiflash",
    "circup",
]

PI_PACKAGES = [
    "gpiozero",
    "lgpio",
    "rpi-lgpio",
    "RPi.GPIO",
    "pigpio",
    "smbus2",
    "spidev",
    "adafruit-blinka",
    "adafruit-circuitpython-busdevice",
    "adafruit-circuitpython-requests",
    "numpy",
    "pillow",
    "pyserial",
    "paho-mqtt",
    "flask",
    "requests",
    "gpiozero[extra]",
]

GITHUB_TARBALLS = [
    # Official SDKs / tools. Not historical research-project releases.
    (
        "boards/rp2040_pico/pico-sdk",
        "https://github.com/raspberrypi/pico-sdk/archive/refs/tags/2.1.1.tar.gz",
        "pico-sdk-2.1.1.tar.gz",
    ),
    (
        "boards/rp2040_pico/picotool-src",
        "https://github.com/raspberrypi/picotool/archive/refs/tags/2.1.1.tar.gz",
        "picotool-2.1.1.tar.gz",
    ),
    (
        "boards/espressif/esp-idf-src",
        "https://github.com/espressif/esp-idf/archive/refs/tags/v5.5.1.tar.gz",
        "esp-idf-v5.5.1.tar.gz",
    ),
    (
        "boards/stm32/stm32flash-src",
        "https://sourceforge.net/projects/stm32flash/files/stm32flash-0.7.tar.gz/download",
        "stm32flash-0.7.tar.gz",
    ),
]

ARDUINO_LIBS = [
    ("ArduinoJson", "https://github.com/bblanchon/ArduinoJson/archive/refs/tags/v7.4.2.tar.gz"),
    ("PubSubClient", "https://github.com/knolleary/pubsubclient/archive/refs/tags/v2.8.tar.gz"),
    ("Adafruit_NeoPixel", "https://github.com/adafruit/Adafruit_NeoPixel/archive/refs/tags/v1.12.5.tar.gz"),
    ("OneWire", "https://github.com/PaulStoffregen/OneWire/archive/refs/tags/v2.3.8.tar.gz"),
    ("DallasTemperature", "https://github.com/milesburton/Arduino-Temperature-Control-Library/archive/refs/tags/3.11.0.tar.gz"),
    ("Servo", "https://github.com/arduino-libraries/Servo/archive/refs/tags/1.2.2.tar.gz"),
    ("FastLED", "https://github.com/FastLED/FastLED/archive/refs/tags/3.9.20.tar.gz"),
    ("LiquidCrystal_I2C", "https://github.com/johnrickman/LiquidCrystal_I2C/archive/refs/heads/master.tar.gz"),
]

rows_tools: list[dict] = []
rows_cores: list[dict] = []
rows_fw: list[dict] = []
rows_sys: list[dict] = []
rows_py: list[dict] = []
rows_miss: list[dict] = []


def rec(kind: str, **kw) -> None:
    kw.setdefault("time_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    {"toolchain": rows_tools, "core": rows_cores, "firmware": rows_fw, "system": rows_sys, "python": rows_py, "missing": rows_miss}[kind].append(kw)


def wget(url: str, dest: Path, ua: bool = True) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    cmd = ["wget", "-c", "-O", str(dest) + ".part", url]
    if ua:
        cmd[1:1] = ["--header=User-Agent: linux-python-offline-resources"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    part = Path(str(dest) + ".part")
    if proc.returncode != 0 or not part.exists() or part.stat().st_size == 0:
        if part.exists() and part.stat().st_size == 0:
            part.unlink()
        raise RuntimeError(proc.stderr[-500:] if proc.stderr else f"wget failed {url}")
    part.replace(dest)


def safe_wget(url: str, dest: Path, **kw) -> bool:
    try:
        wget(url, dest, **kw)
        return True
    except Exception as exc:
        rec("missing", item=dest.name, url=url, detail=str(exc)[:400], category=str(dest.parent.relative_to(EMB)) if dest.is_relative_to(EMB) else str(dest.parent))
        append_progress("embedded", "missing", f"{dest.name}: {exc}"[:200])
        return False


def pick_host_system(systems: list[dict]) -> dict | None:
    by_host = {s.get("host"): s for s in systems if s.get("host")}
    for h in HOST_HINTS:
        if h in by_host:
            return by_host[h]
    for s in systems:
        host = (s.get("host") or "").lower()
        if "x86_64" in host and "linux" in host and "mingw" not in host:
            return s
    return None


def latest_platform(index: dict, pkg_name: str, arch: str) -> tuple[dict, dict] | None:
    for pkg in index.get("packages") or []:
        if pkg.get("name") != pkg_name:
            continue
        best = None
        for pl in pkg.get("platforms") or []:
            if pl.get("architecture") != arch:
                continue
            ver = pl.get("version") or ""
            if best is None or ver > best[0]:
                best = (ver, pl, pkg)
        if best:
            return best[1], best[2]
    return None


def download_arduino_platform(index_file: str, pkg_name: str, arch: str) -> None:
    index = json.loads((IDX / index_file).read_text(encoding="utf-8"))
    found = latest_platform(index, pkg_name, arch)
    if not found:
        rec("missing", item=f"{pkg_name}:{arch}", url=index_file, detail="platform not in index", category="arduino_core")
        return
    plat, pkg = found
    dest_dir = BOARDS / "arduino_espressif_cores" / f"{pkg_name}_{arch}_{plat['version']}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    plat_name = Path(plat["url"]).name
    plat_path = dest_dir / plat_name
    ok = safe_wget(plat["url"], plat_path)
    rec(
        "core",
        name=f"{pkg_name}:{arch}",
        version=plat.get("version"),
        filename=plat_name if ok else "",
        size=plat_path.stat().st_size if ok and plat_path.exists() else plat.get("size"),
        url=plat.get("url"),
        applies_to=f"Arduino {arch} core; host Linux x86-64 compiles, not a board Python wheel",
        sha256=plat.get("checksum", ""),
        status="downloaded" if ok else "missing",
    )
    tools_by_key = {}
    for t in pkg.get("tools") or []:
        tools_by_key[(t.get("name"), t.get("version"))] = t
    for dep in plat.get("toolsDependencies") or []:
        tname, tver = dep.get("name"), dep.get("version")
        if pkg_name == "esp32" and tname not in ESP32_BASIC_TOOLS:
            rec(
                "missing",
                item=f"{tname}@{tver}",
                url="",
                detail="ESP32 extra chip tool not in basic kit (C5/C6/H2/P4 etc.)",
                category="esp32_optional_tool",
            )
            continue
        tool = tools_by_key.get((tname, tver))
        if not tool:
            rec("missing", item=f"{tname}@{tver}", url="", detail="tool not found in package index", category="arduino_tool")
            continue
        sysrec = pick_host_system(tool.get("systems") or [])
        if not sysrec:
            rec("missing", item=f"{tname}@{tver}", url="", detail="no x86_64-linux host build in index", category="arduino_tool")
            continue
        tdir = HOST / "arduino_tools" / f"{tname}_{tver}"
        fname = Path(sysrec["url"]).name
        path = tdir / fname
        ok = safe_wget(sysrec["url"], path)
        rec(
            "toolchain",
            name=tname,
            version=tver,
            filename=fname if ok else "",
            size=path.stat().st_size if ok and path.exists() else sysrec.get("size"),
            url=sysrec.get("url"),
            applies_to=f"host Linux x86-64; required by {pkg_name}:{arch}",
            host=sysrec.get("host"),
            status="downloaded" if ok else "missing",
        )


def download_arduino_cli() -> None:
    dest = HOST / "arduino_cli"
    dest.mkdir(parents=True, exist_ok=True)
    url = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz"
    path = dest / "arduino-cli_latest_Linux_64bit.tar.gz"
    ok = safe_wget(url, path)
    rec(
        "toolchain",
        name="arduino-cli",
        version="latest",
        filename=path.name if ok else "",
        size=path.stat().st_size if ok and path.exists() else 0,
        url=url,
        applies_to="Linux x86-64 host CLI; not executed this round",
        status="downloaded" if ok else "missing",
    )


def github_latest_asset(repo: str, name_re: str) -> tuple[str, str] | None:
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    raw = IDX / f"gh_{repo.replace('/', '_')}_latest.json"
    if not (raw.exists() and raw.stat().st_size > 100):
        proc = subprocess.run(
            [
                "wget",
                "-q",
                "-O",
                str(raw),
                "--header=User-Agent: linux-python-offline-resources",
                "--header=Accept: application/vnd.github+json",
                api,
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            rec("missing", item=repo, url=api, detail="github api failed", category="github_release")
            return None
    try:
        data = json.loads(raw.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        rec("missing", item=repo, url=api, detail="github api json invalid", category="github_release")
        return None
    for a in data.get("assets") or []:
        if re.search(name_re, a.get("name") or ""):
            return a["name"], a["browser_download_url"]
    rec("missing", item=repo, url=api, detail=f"no asset matching {name_re}", category="github_release")
    return None


def download_host_binaries() -> None:
    specs = [
        ("xpack-dev-tools/arm-none-eabi-gcc-xpack", r"linux-x64\.tar\.gz$", HOST / "gcc_arm_none_eabi", "ARM GNU toolchain for Pico/STM32/UNO R4 host builds"),
        ("xpack-dev-tools/openocd-xpack", r"linux-x64\.tar\.gz$", HOST / "openocd", "OpenOCD SWD/JTAG for STM32/Pico"),
        ("stlink-org/stlink", r"x86_64\.tar\.|linux", HOST / "stlink", "ST-Link userspace tools (if asset exists)"),
        ("raspberrypi/picotool", r"linux|x86_64|amd64", HOST / "picotool", "picotool binary if published; otherwise source tarball only"),
        ("xpack-dev-tools/windows-build-tools-xpack", r"never-match", HOST / "unused", "skip"),
    ]
    for repo, pat, dest, note in specs:
        if dest.name == "unused":
            continue
        hit = github_latest_asset(repo, pat)
        if not hit:
            continue
        name, url = hit
        path = dest / name
        ok = safe_wget(url, path)
        rec(
            "toolchain",
            name=repo.split("/")[-1],
            version="latest_release",
            filename=name if ok else "",
            size=path.stat().st_size if ok and path.exists() else 0,
            url=url,
            applies_to=note,
            status="downloaded" if ok else "missing",
        )


def pip_host(python_version: str) -> None:
    dest = HOST / f"python_host_comms_py{python_version.replace('.', '')}" / "wheelhouse"
    dest.mkdir(parents=True, exist_ok=True)
    req = dest.parent / "requirements_direct_en.txt"
    req.write_text("\n".join(HOST_PY_PACKAGES) + "\n", encoding="utf-8")
    cmd = pip_base(dest, python_version) + ["-r", str(req)]
    rc = run_logged(cmd, LOG)
    if rc != 0:
        for pkg in HOST_PY_PACKAGES:
            run_logged(pip_base(dest, python_version) + [pkg], LOG)
    wheels = list(dest.glob("*.whl"))
    rec(
        "python",
        name=f"host_comms_py{python_version}",
        version=python_version,
        filename=f"{len(wheels)} wheels",
        size=sum(p.stat().st_size for p in wheels),
        url="PyPI",
        applies_to="Linux x86-64 host: serial/USB/CAN/MQTT/Modbus/BLE/MAVLink/esptool/mpremote",
        status="downloaded" if wheels else "missing",
    )
    (dest.parent / "README_cn.md").write_text(
        f"# 电脑端通信与烧录 Python 包（CPython {python_version}）\n\n"
        "仅 Linux x86-64。不能拷到树莓派或 MicroPython 板端使用。\n"
        "本轮未安装、未连接硬件。\n",
        encoding="utf-8",
    )


def pip_pi(python_version: str, platform_set: list[str], label: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    tag = python_version.replace(".", "")
    req = dest.parent / "requirements_direct_en.txt"
    req.write_text("\n".join(PI_PACKAGES) + "\n", encoding="utf-8")
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
        "--extra-index-url",
        "https://www.piwheels.org/simple",
        "--cache-dir",
        str(CACHE_DIR),
        "--disable-pip-version-check",
        "-r",
        str(req),
    ]
    for p in platform_set:
        cmd.extend(["--platform", p])
    rc = run_logged(cmd, LOG)
    if rc != 0:
        for pkg in PI_PACKAGES:
            run_logged(cmd[:-2] + [pkg], LOG)
    wheels = list(dest.glob("*.whl"))
    rec(
        "python",
        name=f"raspberry_pi_{label}_py{tag}",
        version=python_version,
        filename=f"{len(wheels)} wheels",
        size=sum(p.stat().st_size for p in wheels),
        url="PyPI + piwheels.org",
        applies_to=f"board-side Raspberry Pi OS {label}; NOT Linux x86-64",
        status="downloaded" if wheels else "missing",
    )


def download_firmware() -> None:
    # MicroPython official firmware names change; try GitHub firmware workflow artifacts via download pages.
    mp = FW / "micropython"
    mp.mkdir(parents=True, exist_ok=True)
    candidates = {
        "ESP32_GENERIC": [
            "https://micropython.org/resources/firmware/ESP32_GENERIC-20250911-v1.26.1.bin",
            "https://micropython.org/resources/firmware/ESP32_GENERIC-20241129-v1.24.1.bin",
        ],
        "ESP32_GENERIC_S3": [
            "https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20250911-v1.26.1.bin",
            "https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20241129-v1.24.1.bin",
        ],
        "ESP32_GENERIC_C3": [
            "https://micropython.org/resources/firmware/ESP32_GENERIC_C3-20250911-v1.26.1.bin",
            "https://micropython.org/resources/firmware/ESP32_GENERIC_C3-20241129-v1.24.1.bin",
        ],
        "ESP8266_GENERIC": [
            "https://micropython.org/resources/firmware/ESP8266_GENERIC-20250911-v1.26.1.bin",
            "https://micropython.org/resources/firmware/ESP8266_GENERIC-20241129-v1.24.1.bin",
        ],
        "RPI_PICO": [
            "https://micropython.org/resources/firmware/RPI_PICO-20250911-v1.26.1.uf2",
            "https://micropython.org/resources/firmware/RPI_PICO-20241129-v1.24.1.uf2",
        ],
        "RPI_PICO_W": [
            "https://micropython.org/resources/firmware/RPI_PICO_W-20250911-v1.26.1.uf2",
            "https://micropython.org/resources/firmware/RPI_PICO_W-20241129-v1.24.1.uf2",
        ],
        "RPI_PICO2": [
            "https://micropython.org/resources/firmware/RPI_PICO2-20250911-v1.26.1.uf2",
            "https://micropython.org/resources/firmware/RPI_PICO2-20241129-v1.24.1.uf2",
        ],
        "PYBV11": [
            "https://micropython.org/resources/firmware/PYBV11-20250911-v1.26.1.dfu",
            "https://micropython.org/resources/firmware/PYBV11-20241129-v1.24.1.dfu",
        ],
        "STM32F405DISC": [
            "https://micropython.org/resources/firmware/STM32F405DISC-20250911-v1.26.1.dfu",
            "https://micropython.org/resources/firmware/STM32F405DISC-20241129-v1.24.1.dfu",
        ],
        "NUCLEO_F401RE": [
            "https://micropython.org/resources/firmware/NUCLEO_F401RE-20250911-v1.26.1.hex",
            "https://micropython.org/resources/firmware/NUCLEO_F401RE-20241129-v1.24.1.hex",
        ],
    }
    for board, urls in candidates.items():
        got = False
        for url in urls:
            path = mp / Path(url).name
            if safe_wget(url, path):
                rec(
                    "firmware",
                    name="MicroPython",
                    version=Path(url).name,
                    filename=path.name,
                    size=path.stat().st_size,
                    url=url,
                    applies_to=board,
                    status="downloaded",
                )
                got = True
                break
        if not got:
            rec("missing", item=f"micropython_{board}", url=urls[0], detail="firmware URL not found", category="micropython")

    cp = FW / "circuitpython"
    cp.mkdir(parents=True, exist_ok=True)
    cp_urls = [
        "https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-10.0.3.uf2",
        "https://downloads.circuitpython.org/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-10.0.3.uf2",
        "https://downloads.circuitpython.org/bin/raspberry_pi_pico2/en_US/adafruit-circuitpython-raspberry_pi_pico2-en_US-10.0.3.uf2",
        "https://downloads.circuitpython.org/bin/espressif_esp32_devkitc_v4/en_US/adafruit-circuitpython-espressif_esp32_devkitc_v4-en_US-10.0.3.bin",
        "https://downloads.circuitpython.org/bin/espressif_esp32s3_devkitc_1_n8/en_US/adafruit-circuitpython-espressif_esp32s3_devkitc_1_n8-en_US-10.0.3.bin",
        "https://downloads.circuitpython.org/bin/st_stm32f411ce_blackpill/en_US/adafruit-circuitpython-st_stm32f411ce_blackpill-en_US-10.0.3.uf2",
    ]
    for url in cp_urls:
        path = cp / Path(url).name
        if safe_wget(url, path):
            rec("firmware", name="CircuitPython", version="10.0.3", filename=path.name, size=path.stat().st_size, url=url, applies_to=Path(url).name, status="downloaded")

    # Official library bundles (not infinite third-party sensor packs).
    for label, url, fname in [
        (
            "Adafruit_CircuitPython_Bundle",
            "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20251029/adafruit-circuitpython-bundle-10.x-mpy-20251029.zip",
            "adafruit-circuitpython-bundle-10.x-mpy-20251029.zip",
        ),
        (
            "micropython-lib",
            "https://github.com/micropython/micropython-lib/archive/refs/tags/v1.24.0.tar.gz",
            "micropython-lib-v1.24.0.tar.gz",
        ),
    ]:
        dest = FW / "library_bundles" / fname
        if safe_wget(url, dest):
            rec("firmware", name=label, version=fname, filename=fname, size=dest.stat().st_size, url=url, applies_to="board Python libs, not CPython wheels", status="downloaded")


def download_pi_debs() -> None:
    seeds = [
        "python3-libgpiod",
        "libgpiod2",
        "python3-lgpio",
        "python3-spidev",
        "python3-smbus",
        "python3-pigpio",
        "python3-gpiozero",
        "python3-picamera2",
        "python3-libcamera",
        "i2c-tools",
        "raspi-gpio",
        "python3-rpi.gpio",
        "python3-serial",
    ]
    bases = {
        "bookworm_arm64": [
            "http://archive.raspberrypi.com/debian/dists/bookworm/main/binary-arm64/Packages.gz",
            "http://deb.debian.org/debian/dists/bookworm/main/binary-arm64/Packages.gz",
        ],
        "bookworm_armhf": [
            "http://archive.raspberrypi.com/debian/dists/bookworm/main/binary-armhf/Packages.gz",
            "http://deb.debian.org/debian/dists/bookworm/main/binary-armhf/Packages.gz",
        ],
    }
    pool_roots = {
        "archive.raspberrypi.com": "http://archive.raspberrypi.com/debian/",
        "deb.debian.org": "http://deb.debian.org/debian/",
    }
    for label, urls in bases.items():
        index: dict[str, dict] = {}
        for url in urls:
            gz = IDX / f"pi_{label}_{Path(url).parts[-3]}_{Path(url).parts[1].split('.')[0]}.Packages.gz"
            if not safe_wget(url, gz):
                continue
            root = "http://archive.raspberrypi.com/debian/" if "raspberrypi" in url else "http://deb.debian.org/debian/"
            with gzip.open(gz, "rt", encoding="utf-8", errors="replace") as fh:
                block = []
                for line in fh:
                    if line.strip() == "":
                        if block:
                            recp = Parser().parsestr("".join(block))
                            name = recp.get("Package")
                            if name and name not in index:
                                index[name] = {
                                    "Version": recp.get("Version", ""),
                                    "Filename": recp.get("Filename", ""),
                                    "SHA256": recp.get("SHA256", ""),
                                    "Size": recp.get("Size", ""),
                                    "root": root,
                                }
                            block = []
                    else:
                        block.append(line)
        dest = BOARDS / "raspberry_pi" / label / "system_debs"
        dest.mkdir(parents=True, exist_ok=True)
        got = 0
        for seed in seeds:
            recp = index.get(seed)
            if not recp:
                rec("missing", item=seed, url=label, detail="not in Packages index", category=f"pi_deb_{label}")
                continue
            fname = Path(recp["Filename"]).name
            path = dest / fname
            url = urljoin(recp["root"], recp["Filename"])
            if safe_wget(url, path):
                got += 1
                rec(
                    "system",
                    name=seed,
                    version=recp.get("Version"),
                    filename=fname,
                    size=path.stat().st_size,
                    url=url,
                    applies_to=f"Raspberry Pi OS {label} BOARD, not host x86-64",
                    status="downloaded",
                )
        rec(
            "system",
            name=f"pi_deb_summary_{label}",
            version="",
            filename="",
            size=got,
            url="",
            applies_to=label,
            status=f"downloaded_seeds={got}/{len(seeds)}",
        )


def write_inventories() -> None:
    INV.mkdir(parents=True, exist_ok=True)
    specs = [
        ("toolchains_cn.csv", rows_tools, ["name", "version", "filename", "size", "url", "applies_to", "host", "status", "time_utc"]),
        ("board_cores_cn.csv", rows_cores, ["name", "version", "filename", "size", "url", "applies_to", "sha256", "status", "time_utc"]),
        ("firmware_cn.csv", rows_fw, ["name", "version", "filename", "size", "url", "applies_to", "status", "time_utc"]),
        ("system_deps_cn.csv", rows_sys, ["name", "version", "filename", "size", "url", "applies_to", "status", "time_utc"]),
        ("host_and_board_python_cn.csv", rows_py, ["name", "version", "filename", "size", "url", "applies_to", "status", "time_utc"]),
        ("missing_cn.csv", rows_miss, ["item", "url", "detail", "category", "time_utc"]),
    ]
    for fname, rows, fields in specs:
        with (INV / fname).open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    readme = EMB / "README_cn.md"
    n_py = sum(1 for r in rows_py if r.get("status") == "downloaded")
    n_tool = sum(1 for r in rows_tools if r.get("status") == "downloaded")
    n_core = sum(1 for r in rows_cores if r.get("status") == "downloaded")
    n_fw = sum(1 for r in rows_fw if r.get("status") == "downloaded")
    n_sys = sum(1 for r in rows_sys if r.get("status") == "downloaded")
    readme.write_text(
        f"""# 嵌入式开发离线资源

目录：`linux_python_offline_resources/embedded/`

电脑端与开发板端 **分开保存**。Linux x86-64 wheel **不能**代替树莓派 ARM wheel，也不能代替 MicroPython/CircuitPython 固件。

## 结构

- `host_linux_x86_64/`：在 x86-64 Linux 电脑上编译、烧录、调试、串口/USB/网络通信
- `boards/`：按板卡系列、架构与系统版本存放核心、SDK、系统 deb、ARM wheel
- `firmware/micropython/` 与 `firmware/circuitpython/`：固件与板端库，不按 CPython wheel 环境处理
- `inventories/`：分类清单；**不要用 wheel 数量代表嵌入式环境完整**

## 本轮下载计数（文件级，非完整性）

- 电脑端/板端 Python 套件条目：{n_py}
- 电脑端工具链条目：{n_tool}
- 开发板核心条目：{n_core}
- 固件/板端库条目：{n_fw}
- 板端系统 deb 条目：{n_sys}
- 未获取：见 `inventories/missing_cn.csv`（{len(rows_miss)} 条）

## 适用说明

| 套件 | 适用 | 架构/系统 | 已下载范围 |
| --- | --- | --- | --- |
| host python_host_comms | 电脑端通信/烧录脚本 | Linux x86-64 CPython 3.10/3.12 | pyserial/pyusb/CAN/MQTT/Modbus/BLE/MAVLink/esptool/mpremote |
| arduino-cli + AVR/megaAVR/UNO R4 核心 | 电脑端 Arduino 编译烧录 | 主机 x86-64；目标 AVR 或 RA4M1 | 官方 package_index 中的平台包与对应 host 工具 |
| ESP32/ESP8266 Arduino 核心 | 电脑端编译烧录 ESP | 主机 x86-64；目标 Xtensa/RISC-V | 主流芯片 libs（ESP32/S2/S3/C3），不含全部 C5/C6/H2/P4 |
| Raspberry Pi OS wheels/debs | **板端** | Bookworm ARM64 与 armhf；Python 3.11 | GPIO/I2C/SPI/串口/网络相关包；picamera2 以系统 deb 为主 |
| Pico SDK 源码 + MicroPython UF2 | Pico/RP2040 | 交叉编译在主机；固件在板端 | SDK 源码包与官方 UF2，本轮未编译 |
| STM32 | 主机 OpenOCD/stlink + 部分 MicroPython 固件 | Cortex-M | 无 STM32CubeProgrammer（专有，需 ST 账号） |
| MicroPython / CircuitPython | 板端解释器 | 见固件文件名 | 固件与官方库包；非 CPython wheel |

本轮 **未** 连接硬件、未烧录、未执行安装或交叉编译验证。
""",
        encoding="utf-8",
    )


def main() -> int:
    for p in (EMB, IDX, HOST, BOARDS, FW, INV, HOST / "arduino_tools"):
        p.mkdir(parents=True, exist_ok=True)
    append_progress("embedded", "start", "host tools + board resources")

    download_arduino_cli()
    for item in ARDUINO_PLATFORMS:
        print("core", item, flush=True)
        download_arduino_platform(*item)

    libdir = BOARDS / "arduino_espressif_cores" / "common_arduino_libraries"
    libdir.mkdir(parents=True, exist_ok=True)
    for name, url in ARDUINO_LIBS:
        path = libdir / f"{name}.tar.gz"
        if safe_wget(url, path):
            rec("core", name=f"arduino_lib_{name}", version="", filename=path.name, size=path.stat().st_size, url=url, applies_to="Arduino sketch libraries (host compile)", status="downloaded")

    download_host_binaries()
    for rel, url, fname in GITHUB_TARBALLS:
        dest = EMB / rel / fname
        if safe_wget(url, dest):
            rec("toolchain", name=fname, version="", filename=fname, size=dest.stat().st_size, url=url, applies_to=rel, status="downloaded")

    print("host python", flush=True)
    pip_host("3.10")
    pip_host("3.12")

    print("pi wheels", flush=True)
    aarch64_plats = [
        "manylinux2014_aarch64",
        "manylinux_2_17_aarch64",
        "manylinux_2_28_aarch64",
        "manylinux_2_31_aarch64",
        "manylinux_2_35_aarch64",
        "linux_aarch64",
        "any",
    ]
    armv7_plats = [
        "manylinux2014_armv7l",
        "linux_armv7l",
        "any",
    ]
    pip_pi("3.11", aarch64_plats, "bookworm_arm64", BOARDS / "raspberry_pi" / "bookworm_arm64" / "python311_wheels")
    pip_pi("3.11", armv7_plats, "bookworm_armhf", BOARDS / "raspberry_pi" / "bookworm_armhf" / "python311_wheels")

    print("pi debs", flush=True)
    download_pi_debs()
    print("firmware", flush=True)
    download_firmware()
    write_inventories()

    # Point top-level README at embedded without rewriting old sections heavily.
    top = ROOT / "README_cn.md"
    extra = "\n## 嵌入式开发板\n\n见 `embedded/README_cn.md`。电脑端工具与板端资源分开；固件不是 CPython wheel。\n"
    text = top.read_text(encoding="utf-8") if top.exists() else ""
    if "embedded/README_cn.md" not in text:
        top.write_text(text.rstrip() + extra, encoding="utf-8")
    ov = ROOT / "environments_overview_cn.md"
    ov_text = ov.read_text(encoding="utf-8") if ov.exists() else ""
    if "embedded/" not in ov_text:
        ov.write_text(ov_text.rstrip() + "\n\n## 嵌入式（增量）\n\n详见 `embedded/README_cn.md` 与 `embedded/inventories/`。不以 Python wheel 数量代表嵌入式套件完整。\n", encoding="utf-8")
    append_progress("embedded", "finished_pass", f"miss={len(rows_miss)} fw={len(rows_fw)} tools={len(rows_tools)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
