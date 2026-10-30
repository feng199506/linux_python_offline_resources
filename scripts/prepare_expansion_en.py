#!/usr/bin/env python3
"""Incremental Linux offline expansion. Does not re-audit existing 24 groups."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from expansion_specs_en import EXPANSION_ENVIRONMENTS, EXPANSION_SEEDS_DEB  # noqa: E402
from prepare_offline_en import (  # noqa: E402
    CACHE_DIR,
    ENV_ROOT,
    INDEX_DIR,
    LOG_DIR,
    PIP_PYZ,
    PYPI,
    ROOT as PREP_ROOT,
    STATE_DIR,
    UBUNTU_SUITES,
    append_progress,
    build_lock_and_inventory,
    download_debs,
    download_environment,
    download_url,
    ensure_dirs,
    load_state,
    merged_index,
    pip_base,
    resolve_deb_closure,
    run_logged,
    save_state,
    write_check_script,
    write_install_script,
    write_readme,
)

assert PREP_ROOT == ROOT
EXT_RT = ROOT / "external_runtimes"
SDIST_NOTE = "sdist_needs_build; not a direct offline wheel"


def try_sdists(env: dict, failed: list[str]) -> list[dict]:
    if not failed:
        return []
    env_dir = ENV_ROOT / env["id"]
    sdir = env_dir / "sdist_needs_build"
    sdir.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"{env['id']}_sdist.log"
    saved = []
    for pkg in failed:
        if not pkg or pkg.startswith("=="):
            continue
        cmd = [
            sys.executable,
            str(PIP_PYZ),
            "download",
            "--dest",
            str(sdir),
            "--python-version",
            env["python"],
            "--no-deps",
            "--no-binary",
            pkg.split("[")[0].split("==")[0].split(">")[0].split("<")[0],
            "--cache-dir",
            str(CACHE_DIR),
            "--disable-pip-version-check",
            pkg,
        ]
        rc = run_logged(cmd, log)
        files = sorted(p.name for p in sdir.glob("*") if p.is_file())
        saved.append({"package": pkg, "ok": rc == 0, "files": files})
    (env_dir / "sdist_needs_build_en.json").write_text(json.dumps(saved, indent=2), encoding="utf-8")
    return saved


def append_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    existing = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            existing = list(csv.DictReader(fh))
    seen = {(r.get("environment"), r.get("filename") or r.get("item") or r.get("component")) for r in existing}
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in existing:
            w.writerow(r)
        for r in rows:
            key = (r.get("environment"), r.get("filename") or r.get("item") or r.get("component"))
            if key in seen:
                continue
            w.writerow(r)


def update_overview(new_rows: list[dict]) -> None:
    path = ROOT / "environments_overview_cn.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = "## 本轮扩展（数据处理、工程与应用）"
    table = [
        "",
        marker,
        "",
        "本段为增量扩展，未重新审计原 01–11 组。",
        "",
        "| 目录 | Python | 用途 | wheel 数 | 总字节 | 最低 glibc | 下载状态 | 目标机安装验证 |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for item in new_rows:
        table.append(
            f"| `{item['id']}` | {item['python']} | {item.get('title_cn','')} | {item.get('count',0)} | {item.get('total_bytes',0)} | {item.get('min_glibc','')} | {item.get('status','')} | 未做 |"
        )
    block = "\n".join(table) + "\n"
    if marker in text:
        pre, rest = text.split(marker, 1)
        # drop old expansion section until next ## or end
        nxt = rest.find("\n## ")
        if nxt >= 0:
            # rest starts with title line after split; find following heading in rest
            parts = rest.split("\n## ", 1)
            text = pre.rstrip() + "\n" + block + ("\n## " + parts[1] if len(parts) > 1 else "")
        else:
            text = pre.rstrip() + "\n" + block
    else:
        # insert before 离线安装步骤
        key = "## 离线安装步骤（目标 Linux）"
        if key in text:
            pre, post = text.split(key, 1)
            text = pre.rstrip() + "\n" + block + "\n" + key + post
        else:
            text = text.rstrip() + "\n" + block
    path.write_text(text, encoding="utf-8")


def update_readme() -> None:
    path = ROOT / "README_cn.md"
    extra = """
## 扩展环境（增量）

原 01–11 组保持不动。新增 12–23 覆盖数据处理、统计时序、机器学习工程、NLP/检索、媒体 OCR、Web、数据库、爬虫、文档、可视化、桌面 GUI、工程工具与通用 SDK。

- 扩展准备脚本：`scripts/prepare_expansion_en.py`
- 外部运行时（Playwright 浏览器、Pandoc 等）：`external_runtimes/`
- Ubuntu 22.04/24.04 扩展 `.deb`：`system_dependencies/*/expansion_debs/`
"""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if "扩展环境（增量）" not in text:
        path.write_text(text.rstrip() + "\n" + extra, encoding="utf-8")


def download_expansion_debs() -> list[dict]:
    notes = []
    issues = []
    for suite, seeds in EXPANSION_SEEDS_DEB.items():
        idx = merged_index(suite)
        dest_kind = "expansion"
        names, missing = resolve_deb_closure(idx, seeds)
        suite_dir = ROOT / "system_dependencies" / suite
        (suite_dir / "expansion_closure_en.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
        (suite_dir / "expansion_missing_en.txt").write_text("\n".join(missing) + "\n", encoding="utf-8")
        ok, fail = download_debs(suite, dest_kind, names, idx)
        append_progress(f"expansion_debs_{suite}", "ok" if fail == 0 else "partial", f"ok={ok} fail={fail} missing={len(missing)}")
        notes.append(
            {
                "component": f"{suite}_expansion_debs",
                "category": "deb_closure",
                "needed_by": "tesseract/poppler/weasyprint/ffmpeg/libpq",
                "ubuntu_22.04": f"system_dependencies/{suite}/expansion_debs" if suite.endswith("22.04") else "",
                "ubuntu_24.04": f"system_dependencies/{suite}/expansion_debs" if suite.endswith("24.04") else "",
                "offline_status": f"downloaded={ok}; fail={fail}; unresolved={len(missing)}",
                "official_docs": "http://archive.ubuntu.com/ubuntu/",
                "notes_cn": "扩展用途系统包。未在本机安装。Python wheel 成功不等于 Tesseract/Poppler/FFmpeg 已可运行。",
            }
        )
        for m in missing:
            issues.append({"environment": suite, "severity": "system", "item": m, "detail": "unresolved expansion deb"})
    return notes, issues


def playwright_browsers_from_wheel(wheelhouse: Path) -> dict | None:
    wheels = sorted(wheelhouse.glob("playwright-*.whl")) + sorted(wheelhouse.glob("playwright_core-*.whl"))
    for whl in wheels:
        with zipfile.ZipFile(whl) as zf:
            names = [n for n in zf.namelist() if n.endswith("browsers.json")]
            if not names:
                continue
            return json.loads(zf.read(names[0]).decode("utf-8"))
    return None


def download_playwright_browsers(spec: dict) -> list[dict]:
    dest = EXT_RT / "playwright_browsers_linux_x64"
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    wanted = {"chromium", "firefox", "webkit", "ffmpeg"}
    for browser in spec.get("browsers") or []:
        name = browser.get("name")
        if name not in wanted:
            continue
        revision = str(browser.get("revision") or "")
        if not revision:
            continue
        # Skip if browser metadata says it is not for this platform; still try linux.
        filename = f"{name}-linux.zip"
        url = f"https://playwright.azureedge.net/builds/{name}/{revision}/{filename}"
        out = dest / f"{name}-{revision}-linux.zip"
        try:
            if not (out.exists() and out.stat().st_size > 0):
                download_url(url, out)
            rows.append(
                {
                    "component": f"playwright_{name}",
                    "category": "browser_runtime",
                    "needed_by": "19_scraping_automation",
                    "ubuntu_22.04": "linux-x64 zip, not distro-specific",
                    "ubuntu_24.04": "linux-x64 zip, not distro-specific",
                    "offline_status": f"downloaded:{out.name}; size={out.stat().st_size}",
                    "official_docs": "https://playwright.dev/python/docs/browsers",
                    "notes_cn": "Playwright 官方 Linux x64 浏览器包。未执行安装。glibc 目标仍为 Ubuntu 22.04/24.04。",
                }
            )
            append_progress(f"playwright_{name}", "ok", str(out))
        except Exception as exc:
            rows.append(
                {
                    "component": f"playwright_{name}",
                    "category": "browser_runtime",
                    "needed_by": "19_scraping_automation",
                    "ubuntu_22.04": "missing",
                    "ubuntu_24.04": "missing",
                    "offline_status": f"not_downloaded:{exc}",
                    "official_docs": "https://playwright.dev/python/docs/browsers",
                    "notes_cn": "未能获取该浏览器 zip，不能把 playwright wheel 当作浏览器已齐备。",
                }
            )
            append_progress(f"playwright_{name}", "failed", str(exc))
    (dest / "browsers_source_en.json").write_text(json.dumps(spec, indent=2)[:20000], encoding="utf-8")
    return rows


def download_pandoc() -> dict:
    dest = EXT_RT / "pandoc"
    dest.mkdir(parents=True, exist_ok=True)
    # Resolve latest linux-amd64 tarball from GitHub API without cloning repos.
    api = "https://api.github.com/repos/jgm/pandoc/releases/latest"
    raw = dest / "latest_release_en.json"
    try:
        if not (raw.exists() and raw.stat().st_size > 100):
            subprocess.run(
                [
                    "wget",
                    "-q",
                    "-O",
                    str(raw),
                    "--header=Accept: application/vnd.github+json",
                    "--header=User-Agent: linux-python-offline-resources",
                    api,
                ],
                check=True,
            )
        data = json.loads(raw.read_text(encoding="utf-8"))
        asset = None
        for a in data.get("assets") or []:
            name = a.get("name") or ""
            if re.search(r"linux-amd64\.tar\.gz$", name):
                asset = a
                break
        if not asset:
            return {
                "component": "pandoc",
                "category": "document_runtime",
                "needed_by": "20_documents / pypandoc",
                "ubuntu_22.04": "missing",
                "ubuntu_24.04": "missing",
                "offline_status": "no linux-amd64 asset in latest release JSON",
                "official_docs": "https://github.com/jgm/pandoc/releases",
                "notes_cn": "未找到官方 linux-amd64 包。pypandoc wheel 不能单独完成转换。",
            }
        url = asset["browser_download_url"]
        out = dest / asset["name"]
        if not (out.exists() and out.stat().st_size > 0):
            download_url(url, out)
        return {
            "component": "pandoc",
            "category": "document_runtime",
            "needed_by": "20_documents / pypandoc",
            "ubuntu_22.04": out.name,
            "ubuntu_24.04": out.name,
            "offline_status": f"downloaded; size={out.stat().st_size}",
            "official_docs": url,
            "notes_cn": "官方静态 tarball，非 Ubuntu deb。未执行。",
        }
    except Exception as exc:
        return {
            "component": "pandoc",
            "category": "document_runtime",
            "needed_by": "20_documents / pypandoc",
            "ubuntu_22.04": "missing",
            "ubuntu_24.04": "missing",
            "offline_status": f"not_downloaded:{exc}",
            "official_docs": "https://github.com/jgm/pandoc/releases",
            "notes_cn": "未能下载 Pandoc。文档组 Python 包不能替代该可执行文件。",
        }


def main() -> int:
    ensure_dirs()
    EXT_RT.mkdir(parents=True, exist_ok=True)
    (ROOT / "system_dependencies" / "ubuntu_22.04" / "expansion_debs").mkdir(parents=True, exist_ok=True)
    (ROOT / "system_dependencies" / "ubuntu_24.04" / "expansion_debs").mkdir(parents=True, exist_ok=True)
    if not PIP_PYZ.exists():
        raise SystemExit("pip.pyz missing")
    state = load_state()
    issues: list[dict] = []
    env_stats: list[dict] = []

    print("=== expansion debs ===", flush=True)
    deb_notes, deb_issues = download_expansion_debs()
    issues.extend(deb_issues)

    print("=== pandoc ===", flush=True)
    pandoc_note = download_pandoc()
    deb_notes.append(pandoc_note)

    for env in EXPANSION_ENVIRONMENTS:
        print(f"=== {env['id']} ===", flush=True)
        append_progress(env["id"], "start", env["title_cn"])
        try:
            info = download_environment(env)
            failed = list(info.get("failed_packages") or [])
            if failed:
                try_sdists(env, failed)
            stats = build_lock_and_inventory(env)
            write_install_script(env)
            write_check_script(env)
            write_readme(env, stats, info)
            row = {
                "id": env["id"],
                "python": env["python"],
                "title_cn": env["title_cn"],
                "status": info.get("status"),
                "count": stats.get("count", 0),
                "total_bytes": stats.get("total_bytes", 0),
                "min_glibc": stats.get("min_glibc", ""),
                "framework": stats.get("framework", ""),
                "bad_wheels": stats.get("bad_wheels", []),
                "sdists": stats.get("sdists", []),
                "rows": stats.get("rows", []),
                "direct_packages": len(env["packages"]),
                "failed": failed,
                "missing_runtime_deps": info.get("missing_runtime_deps") or [],
                "excluded_gpu_deps": info.get("excluded_gpu_deps") or [],
            }
            env_stats.append(row)
            for pkg in failed:
                issues.append(
                    {
                        "environment": env["id"],
                        "severity": "python",
                        "item": pkg,
                        "detail": "no compatible binary wheel; sdist attempted under sdist_needs_build/",
                    }
                )
            for pkg in info.get("missing_runtime_deps") or []:
                issues.append(
                    {
                        "environment": env["id"],
                        "severity": "dependency",
                        "item": pkg,
                        "detail": "runtime Requires-Dist missing; group not marked complete",
                    }
                )
            for pkg in info.get("excluded_gpu_deps") or []:
                issues.append(
                    {
                        "environment": env["id"],
                        "severity": "gpu_excluded",
                        "item": pkg,
                        "detail": "declared GPU/NVIDIA dependency excluded; group not complete if still required",
                    }
                )
            append_progress(env["id"], info.get("status") or "ok", f"wheels={stats['count']} bytes={stats['total_bytes']}")
            state.setdefault("expansion", {})[env["id"]] = info
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
                    "direct_packages": len(env["packages"]),
                    "failed": [str(exc)],
                    "missing_runtime_deps": [],
                    "excluded_gpu_deps": [],
                }
            )
            save_state(state)
            continue

    # Playwright browsers from a successfully downloaded scraping env.
    spec = None
    for env_id in ("19_scraping_automation_py310", "19_scraping_automation_py312"):
        spec = playwright_browsers_from_wheel(ENV_ROOT / env_id / "wheelhouse")
        if spec:
            break
    if spec:
        deb_notes.extend(download_playwright_browsers(spec))
    else:
        deb_notes.append(
            {
                "component": "playwright_browsers",
                "category": "browser_runtime",
                "needed_by": "19_scraping_automation",
                "ubuntu_22.04": "missing",
                "ubuntu_24.04": "missing",
                "offline_status": "playwright wheel had no browsers.json",
                "official_docs": "https://playwright.dev/python/docs/browsers",
                "notes_cn": "未能从 wheel 读取浏览器清单，浏览器未下载。",
            }
        )

    pkg_rows = []
    for item in env_stats:
        for row in item.get("rows") or []:
            pkg_rows.append(
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
    append_csv(
        ROOT / "package_inventory_cn.csv",
        ["environment", "python", "name", "version", "filename", "size_bytes", "platform", "min_glibc", "source", "compatible_default"],
        pkg_rows,
    )
    append_csv(
        ROOT / "compatibility_issues_cn.csv",
        ["environment", "severity", "item", "detail"],
        issues,
    )
    append_csv(
        ROOT / "external_dependencies_cn.csv",
        ["component", "category", "needed_by", "ubuntu_22.04", "ubuntu_24.04", "offline_status", "official_docs", "notes_cn"],
        deb_notes,
    )
    update_overview(env_stats)
    update_readme()
    summary = {
        "new_groups": len(env_stats),
        "direct_packages": sum(e.get("direct_packages", 0) for e in env_stats),
        "wheels": sum(e.get("count", 0) for e in env_stats),
        "bytes": sum(e.get("total_bytes", 0) for e in env_stats),
        "failed_direct": {e["id"]: e.get("failed") for e in env_stats if e.get("failed")},
        "missing_deps": {e["id"]: e.get("missing_runtime_deps") for e in env_stats if e.get("missing_runtime_deps")},
    }
    (STATE_DIR / "expansion_summary_en.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    append_progress("expansion", "finished_pass", json.dumps({k: summary[k] for k in ("new_groups", "wheels", "bytes")}))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
