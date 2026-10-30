# 机器学习工程工具

- 环境编号：[`14_ml_tooling_py310`](./)
- 目标解释器：CPython 3.10，Linux x86-64，glibc
- 参考发行版：Ubuntu 22.04 LTS（glibc 2.35）、Ubuntu 24.04 LTS（glibc 2.39）
- 框架：scikit-learn / statsmodels
- wheel 数量：198
- wheel 总大小：387595742 字节
- 由 wheel 标签推断的最低 glibc：2.28
- 本轮状态：partial（仅下载与静态检查，尚未在目标 Linux 上安装验证）

## 用途与限制

特征工程、类别不平衡、解释性、调参与实验跟踪。不含 PyTorch/TensorFlow 训练框架。

本目录是按用途准备的通用 CPU 环境，不是全部历史研究项目的精确复现。
不要与 `windows_python_offline_resources/` 或其他 Linux 组混装。

默认集合 **不适用于**：ARM64、Alpine/musl、非 glibc 系统、GPU/CUDA。
Ubuntu 22.04 需要 glibc ≥ 2.35 且不高于本环境实际 wheel 需求；若最低 glibc 标记 ≤ 2.35，则 22.04 与 24.04 都可作为候选。若某 wheel 需要更新的 glibc，22.04 不可用。

## 本组能做什么

做特征工程、不平衡学习、SHAP/LIME 解释、Optuna 调参和 MLflow 跟踪。不含训练框架本体。

目标解释器：**CPython 3.10**（Linux x86-64 glibc）。本轮未在目标机安装或运行，不能写成开箱即用。

详细对照见 [`../../guides/常用工具与包用途索引_cn.md`](../../guides/常用工具与包用途索引_cn.md)；安装步骤见 [`../../guides/离线安装与使用_cn.md`](../../guides/离线安装与使用_cn.md)；最小示例见 [`../../guides/常见任务快速入门_cn.md`](../../guides/常见任务快速入门_cn.md)。

## 常用包说明

| 包 | 本环境版本 | 作用 | 额外依赖 | 官方文档 |
| --- | --- | --- | --- | --- |
| `shap` | 0.49.1 | 特征贡献 | 否 | [shap 文档](https://shap.readthedocs.io/) |
| `optuna` | 5.0.0 | 超参搜索 | 远程存储才要网 | [optuna 文档](https://optuna.readthedocs.io/) |
| `mlflow` | 3.17.2 | 实验跟踪 | 跟踪服务器才要网 | [mlflow 文档](https://mlflow.org/docs/latest/index.html) |
| `imbalanced-learn` | 0.14.2 | 类别不平衡 | 否 | [imbalanced-learn 文档](https://imbalanced-learn.org/) |
| `feature-engine` | 1.9.4 | 特征变换 | 否 | [feature-engine 文档](https://feature-engine.readthedocs.io/) |
| `scikit-learn` | 1.7.2 | 基线模型 | 否 | [scikit-learn 文档](https://scikit-learn.org/stable/) |

传递依赖只列在 [`requirements_lock_en.txt`](requirements_lock_en.txt) / [`wheel_inventory_cn.csv`](wheel_inventory_cn.csv)，不逐个写教程。

## 离线安装

1. 准备 CPython 3.10 x86-64 运行时（推荐解压 [`runtimes/python_build_standalone/`](../../runtimes/python_build_standalone/) 中对应 `install_only` 包，或自行从官方源码构建）。
2. 该运行时是 **Astral/indygreg python-build-standalone 第三方构建**，不是 python.org 官方 Linux 二进制。
3. 指定解释器并安装：

```bash
export PYTHON_BIN=/path/to/python3.10
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

- 失败的直接依赖：['lime']
- 静态检查判定为不适合默认 Linux x86-64 的 wheel：无
- 源码包（不能当 wheel 安装）：无
- 系统库（OpenMP、FFmpeg、Graphviz、音频等）见仓库根目录 [`external_dependencies_cn.csv`](../../external_dependencies_cn.csv) 与 [`system_dependencies/`](../../system_dependencies/)。
- 本轮 **没有** 在目标 Ubuntu 22.04/24.04 上创建 venv 或执行导入检查。
