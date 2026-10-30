# 数据库与数据接入（新 Python）

- 环境编号：[`18_database_py312`](./)
- 目标解释器：CPython 3.12，Linux x86-64，glibc
- 参考发行版：Ubuntu 22.04 LTS（glibc 2.35）、Ubuntu 24.04 LTS（glibc 2.39）
- 框架：NumPy / SciPy stack
- wheel 数量：44
- wheel 总大小：160823310 字节
- 由 wheel 标签推断的最低 glibc：2.28
- 本轮状态：downloaded（仅下载与静态检查，尚未在目标 Linux 上安装验证）

## 用途与限制

PostgreSQL/MySQL/SQLite/Redis/Mongo 驱动与 SQLAlchemy/Alembic。mysqlclient 源码包若无 wheel 则另存。不含数据库服务器本身。 CPython 3.12 对应组合。

本目录是按用途准备的通用 CPU 环境，不是全部历史研究项目的精确复现。
不要与 `windows_python_offline_resources/` 或其他 Linux 组混装。

默认集合 **不适用于**：ARM64、Alpine/musl、非 glibc 系统、GPU/CUDA。
Ubuntu 22.04 需要 glibc ≥ 2.35 且不高于本环境实际 wheel 需求；若最低 glibc 标记 ≤ 2.35，则 22.04 与 24.04 都可作为候选。若某 wheel 需要更新的 glibc，22.04 不可用。

## 本组能做什么

用 SQLAlchemy/Alembic 和各数据库驱动访问 PostgreSQL/MySQL/SQLite/Redis/Mongo。本环境没有数据库服务器。

目标解释器：**CPython 3.12**（Linux x86-64 glibc）。本轮未在目标机安装或运行，不能写成开箱即用。

详细对照见 [`../../guides/常用工具与包用途索引_cn.md`](../../guides/常用工具与包用途索引_cn.md)；安装步骤见 [`../../guides/离线安装与使用_cn.md`](../../guides/离线安装与使用_cn.md)；最小示例见 [`../../guides/常见任务快速入门_cn.md`](../../guides/常见任务快速入门_cn.md)。

## 常用包说明

| 包 | 本环境版本 | 作用 | 额外依赖 | 官方文档 |
| --- | --- | --- | --- | --- |
| `sqlalchemy` | 2.1.6 | ORM | 连远程要网 | [sqlalchemy 文档](https://docs.sqlalchemy.org/) |
| `alembic` | 1.20.1 | 迁移 | 否 | [alembic 文档](https://alembic.sqlalchemy.org/) |
| `psycopg` | 3.3.6 | PostgreSQL | 需要服务器 | [psycopg 文档](https://www.psycopg.org/psycopg3/docs/) |
| `pymysql` | 1.2.3 | MySQL | 需要服务器 | [pymysql 文档](https://pymysql.readthedocs.io/) |
| `pymongo` | 4.19.0 | MongoDB | 需要服务器 | [pymongo 文档](https://pymongo.readthedocs.io/) |
| `redis` | 8.1.0 | Redis | 需要服务器 | [redis 文档](https://redis.readthedocs.io/) |
| `duckdb` | 2.0.0 | 本地分析库 | 否 | [duckdb 文档](https://duckdb.org/docs/) |

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
