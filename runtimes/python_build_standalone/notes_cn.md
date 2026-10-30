# python-build-standalone 运行时说明

这些文件 **不是** python.org 官方 Linux 二进制。

- 上游项目：https://github.com/astral-sh/python-build-standalone
- 文档：https://docs.astral.sh/python-build-standalone/
- 许可证：项目自身主要为 MIT；内含 CPython（PSF）及其它第三方库许可证，详见上游发行说明
- 构建来源：Astral 发布的 `install_only` 归档，目标三元组 `x86_64-unknown-linux-gnu`
- 最低 glibc（上游文档）：多数目标为 **2.17**（覆盖 Ubuntu 14.04+；本仓库默认参考场景为 Ubuntu 22.04/24.04）
- 选用 `x86_64` 基线构建，不用 `x86_64_v2/v3/v4`，也不用 musl

解压后得到 `python/bin/python3`，可直接作为 `PYTHON_BIN` 创建 venv。
本准备过程 **没有执行** 这些运行时。
