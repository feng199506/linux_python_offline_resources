# 文档处理（新 Python）

- 环境编号：[`20_documents_py312`](./)
- 目标解释器：CPython 3.12，Linux x86-64，glibc
- 参考发行版：Ubuntu 22.04 LTS（glibc 2.35）、Ubuntu 24.04 LTS（glibc 2.39）
- 框架：ONNX Runtime CPU
- wheel 数量：67
- wheel 总大小：175689230 字节
- 由 wheel 标签推断的最低 glibc：2.28
- 本轮状态：downloaded（仅下载与静态检查，尚未在目标 Linux 上安装验证）

## 用途与限制

PDF/Office/Markdown/HTML 转换与模板。WeasyPrint 依赖 Cairo/Pango；pypandoc 依赖 Pandoc 可执行文件。 CPython 3.12 对应组合。

本目录是按用途准备的通用 CPU 环境，不是全部历史研究项目的精确复现。
不要与 `windows_python_offline_resources/` 或其他 Linux 组混装。

默认集合 **不适用于**：ARM64、Alpine/musl、非 glibc 系统、GPU/CUDA。
Ubuntu 22.04 需要 glibc ≥ 2.35 且不高于本环境实际 wheel 需求；若最低 glibc 标记 ≤ 2.35，则 22.04 与 24.04 都可作为候选。若某 wheel 需要更新的 glibc，22.04 不可用。

## 本组能做什么

读写 PDF/Word/PPT/Excel，以及部分 HTML/Markdown 转换。WeasyPrint 要 Cairo；pypandoc 要 Pandoc 二进制（本库未齐备）。

目标解释器：**CPython 3.12**（Linux x86-64 glibc）。本轮未在目标机安装或运行，不能写成开箱即用。

详细对照见 [`../../guides/常用工具与包用途索引_cn.md`](../../guides/常用工具与包用途索引_cn.md)；安装步骤见 [`../../guides/离线安装与使用_cn.md`](../../guides/离线安装与使用_cn.md)；最小示例见 [`../../guides/常见任务快速入门_cn.md`](../../guides/常见任务快速入门_cn.md)。

## 常用包说明

| 包 | 本环境版本 | 作用 | 额外依赖 | 官方文档 |
| --- | --- | --- | --- | --- |
| `pypdf` | 6.21.4 | 轻量 PDF | 否 | [pypdf 文档](https://pypdf.readthedocs.io/) |
| `pymupdf` | 2.0 | PDF 渲染/提取 | 否 | [pymupdf 文档](https://pymupdf.readthedocs.io/) |
| `python-docx` | 1.2.0 | Word | 否 | [python-docx 文档](https://python-docx.readthedocs.io/) |
| `python-pptx` | 1.0.2 | PPT | 否 | [python-pptx 文档](https://python-pptx.readthedocs.io/) |
| `openpyxl` | 3.1.5 | Excel | 否 | [openpyxl 文档](https://openpyxl.readthedocs.io/) |
| `reportlab` | 5.1.0 | 生成 PDF | 否 | [reportlab 文档](https://www.reportlab.com/docs/reportlab-userguide.pdf) |
| `weasyprint` | 70.0 | HTML→PDF | Cairo/Pango | [weasyprint 文档](https://weasyprint.readthedocs.io/) |
| `pypandoc` | 1.17 | 调 Pandoc | Pandoc 未齐备 | [pypandoc 文档](https://github.com/JessicaTegner/pypandoc) |

传递依赖只列在 [`requirements_lock_en.txt`](requirements_lock_en.txt) / [`wheel_inventory_cn.csv`](wheel_inventory_cn.csv)，不逐个写教程。

## 离线安装

1. 准备 CPython 3.12 x86-64 运行时（推荐解压 [`runtimes/python_build_standalone/`](../../runtimes/python_build_standalone/) 中对应 `install_only` 包，或自行从官方源码构建）。
2. 该运行时是 **Astral/indygreg python-build-standalone 第三方构建**，不是 python.org 官方 Linux 二进制。
3. 指定解释器并安装：

```bash
export PYTHON_BIN=/path/to/python3.12
bash ./install_offline_en.sh
"$PYTHON_BIN"/../bin/python -m pip  # 不使用
./venv/bin/python ./check_environment_en.py
```

安装脚本使用 `venv` + `pip install --no-index --find-links wheelhouse`。
失败即停止，不会静默联网，不会修改系统 Python，不会调用 sudo。

## 文件

- [`requirements_direct_en.txt`](requirements_direct_en.txt)：直接依赖
- [`requirements_lock_en.txt`](requirements_lock_en.txt)：锁定版本（含传递依赖）
- [`wheelhouse/`](wheelhouse/)：完整 wheel
- [`wheel_inventory_cn.csv`](wheel_inventory_cn.csv)：包名、版本、来源、大小、平台、最低 glibc
- [`install_offline_en.sh`](install_offline_en.sh)
- [`check_environment_en.py`](check_environment_en.py)

## 未完成 / 注意

- 失败的直接依赖：无
- 静态检查判定为不适合默认 Linux x86-64 的 wheel：无
- 源码包（不能当 wheel 安装）：无
- 系统库（OpenMP、FFmpeg、Graphviz、音频等）见仓库根目录 [`external_dependencies_cn.csv`](../../external_dependencies_cn.csv) 与 [`system_dependencies/`](../../system_dependencies/)。
- 本轮 **没有** 在目标 Ubuntu 22.04/24.04 上创建 venv 或执行导入检查。
