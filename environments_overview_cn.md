# Linux 通用科研 Python 离线环境总览

默认目标：**Linux x86-64 + glibc**，参考 Ubuntu 22.04/24.04 LTS，**CPU**。
这不是“全部 Linux”环境。ARM64、musl、其他发行版、GPU 见 [`pending_not_in_default/`](pending_not_in_default/)。

Windows 资源在 `windows_python_offline_resources/`，两套安装包不混用。

## Python 运行时

| 版本 | 类型 | 文件 | 官方 python.org 二进制 | 本轮是否执行 |
| --- | --- | --- | --- | --- |
| 3.10.22 | python-build-standalone 第三方可解压运行时 | [`runtimes/python_build_standalone/cpython-3.10.22+20261001-x86_64-unknown-linux-gnu-install_only.tar.gz`](runtimes/python_build_standalone/cpython-3.10.22+20261001-x86_64-unknown-linux-gnu-install_only.tar.gz) | 否 | 否 |
| 3.12.16 | python-build-standalone 第三方可解压运行时 | [`runtimes/python_build_standalone/cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz`](runtimes/python_build_standalone/cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz) | 否 | 否 |
| 3.10.22 | CPython 官方源码 | [`runtimes/cpython_official_source/Python-3.10.22.tar.xz`](runtimes/cpython_official_source/Python-3.10.22.tar.xz) | 否（源码） | 否 |
| 3.12.16 | CPython 官方源码 | [`runtimes/cpython_official_source/Python-3.12.16.tar.xz`](runtimes/cpython_official_source/Python-3.12.16.tar.xz) | 否（源码） | 否 |

选择依据：3.10 已于 2026-10-01 结束上游支持，仅作兼容环境；3.12 安全支持至 2028-10，科学计算 wheel 覆盖较 3.13/3.14 更稳。

## 环境分组

| 目录 | Python | 框架 | wheel 数 | 总字节 | 最低 glibc | 下载状态 | 目标机安装验证 |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| [`01_scientific_notebook_py310`](environments/01_scientific_notebook_py310/) | 3.10 | NumPy / SciPy stack | 128 | 230098833 | 2.34 | downloaded | 未做 |
| [`01_scientific_notebook_py312`](environments/01_scientific_notebook_py312/) | 3.12 | NumPy / SciPy stack | 124 | 233424932 | 2.34 | downloaded | 未做 |
| [`02_ml_stats_timeseries_em_py310`](environments/02_ml_stats_timeseries_em_py310/) | 3.10 | scikit-learn / statsmodels | 35 | 359631843 | 2.28 | downloaded | 未做 |
| [`02_ml_stats_timeseries_em_py312`](environments/02_ml_stats_timeseries_em_py312/) | 3.12 | scikit-learn / statsmodels | 34 | 282700184 | 2.28 | downloaded | 未做 |
| [`03_signal_audio_image_py310`](environments/03_signal_audio_image_py310/) | 3.10 | scikit-learn / statsmodels | 73 | 268984171 | 2.28 | downloaded | 未做 |
| [`03_signal_audio_image_py312`](environments/03_signal_audio_image_py312/) | 3.12 | scikit-learn / statsmodels | 69 | 266422082 | 2.28 | downloaded | 未做 |
| [`04_pytorch_cpu_py310`](environments/04_pytorch_cpu_py310/) | 3.10 | PyTorch CPU | 17 | 233962432 | 2.28 | downloaded | 未做 |
| [`04_pytorch_cpu_py312`](environments/04_pytorch_cpu_py312/) | 3.12 | PyTorch CPU | 17 | 247890784 | 2.28 | downloaded | 未做 |
| [`05_gpr_bayesopt_py310`](environments/05_gpr_bayesopt_py310/) | 3.10 | PyTorch CPU + GPyTorch/BoTorch | 35 | 291189314 | 2.28 | downloaded | 未做 |
| [`05_gpr_bayesopt_py312`](environments/05_gpr_bayesopt_py312/) | 3.12 | PyTorch CPU + GPyTorch/BoTorch | 32 | 303160869 | 2.28 | downloaded | 未做 |
| [`06_bayesian_mcmc_py310`](environments/06_bayesian_mcmc_py310/) | 3.10 | PyMC / ArviZ | 45 | 106976544 | 2.28 | downloaded | 未做 |
| [`06_bayesian_mcmc_py312`](environments/06_bayesian_mcmc_py312/) | 3.12 | PyMC / ArviZ | 41 | 163939814 | 2.28 | downloaded | 未做 |
| [`07_tensorflow_cpu_py310`](environments/07_tensorflow_cpu_py310/) | 3.10 | TensorFlow CPU | 33 | 340584060 | 2.28 | downloaded | 未做 |
| [`07_tensorflow_cpu_py312`](environments/07_tensorflow_cpu_py312/) | 3.12 | TensorFlow CPU | 33 | 337018938 | 2.28 | downloaded | 未做 |
| [`07b_gpflow_tf218_py310`](environments/07b_gpflow_tf218_py310/) | 3.10 | GPflow + TensorFlow CPU | 53 | 976142666 | 2.31 | downloaded | 未做 |
| [`07b_gpflow_tf218_py312`](environments/07b_gpflow_tf218_py312/) | 3.12 | GPflow + TensorFlow CPU | 52 | 969570552 | 2.31 | downloaded | 未做 |
| [`08_rl_basics_py310`](environments/08_rl_basics_py310/) | 3.10 | PyTorch CPU + SB3 | 37 | 282746998 | 2.31 | downloaded | 未做 |
| [`08_rl_basics_py312`](environments/08_rl_basics_py312/) | 3.12 | PyTorch CPU + SB3 | 36 | 296582228 | 2.31 | downloaded | 未做 |
| [`09_huggingface_llm_py310`](environments/09_huggingface_llm_py310/) | 3.10 | PyTorch CPU + Hugging Face | 63 | 322647778 | 2.28 | downloaded | 未做 |
| [`09_huggingface_llm_py312`](environments/09_huggingface_llm_py312/) | 3.12 | PyTorch CPU + Hugging Face | 60 | 339457398 | 2.28 | downloaded | 未做 |
| [`10_onnx_api_ui_py310`](environments/10_onnx_api_ui_py310/) | 3.10 | ONNX Runtime CPU | 84 | 231531523 | 2.28 | downloaded | 未做 |
| [`10_onnx_api_ui_py312`](environments/10_onnx_api_ui_py312/) | 3.12 | ONNX Runtime CPU | 77 | 229294366 | 2.28 | downloaded | 未做 |
| [`11_optimization_control_py310`](environments/11_optimization_control_py310/) | 3.10 | CVXPY / CasADi | 28 | 220502065 | 2.28 | downloaded | 未做 |
| [`11_optimization_control_py312`](environments/11_optimization_control_py312/) | 3.12 | CVXPY / CasADi | 31 | 241387896 | 2.28 | downloaded | 未做 |

## 补充说明文档

随增量补充包提供，不重新打包原 01–11 wheel：

- [`guides/离线安装与使用_cn.md`](guides/%E7%A6%BB%E7%BA%BF%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8_cn.md)
- [`guides/常用工具与包用途索引_cn.md`](guides/%E5%B8%B8%E7%94%A8%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%8C%85%E7%94%A8%E9%80%94%E7%B4%A2%E5%BC%95_cn.md)
- [`guides/常见任务快速入门_cn.md`](guides/%E5%B8%B8%E8%A7%81%E4%BB%BB%E5%8A%A1%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8_cn.md)

各组 README 含「本组能做什么」。全部示例与安装步骤均为**未在目标机验证**。

## 离线安装步骤（目标 Linux）

1. 确认 `uname -m` 为 `x86_64`，`ldd --version` 显示 glibc ≥ 本环境最低要求，且发行版为 glibc（非 musl）。
2. 解压对应 python-build-standalone：`tar -xzf runtimes/python_build_standalone/cpython-*.tar.gz`
3. `export PYTHON_BIN=/path/to/python/bin/python3`
4. 进入某一 `environments/<id>/`，执行 `bash install_offline_en.sh`
5. 用该 venv 运行 `check_environment_en.py`
6. 按需用发行版包管理器安装 [`external_dependencies_cn.csv`](external_dependencies_cn.csv) 中的系统库。当前机器 **没有** apt install。

## 静态检查与未完成

- 已做：下载、wheel 文件名/METADATA/manylinux 标签检查、Ubuntu Packages 索引解析。
- 未做：解压或执行运行时、创建 venv、导入测试、训练、部署、GPU 包下载。
- 系统 `.deb` 若已下载，也 **不能** 宣称跨发行版离线系统依赖已经齐备；22.04 与 24.04 必须分别安装对应目录中的包。

## 嵌入式（增量）

详见 [`embedded/README_cn.md`](embedded/README_cn.md) 与 [`embedded/inventories/`](embedded/inventories/)。不以 Python wheel 数量代表嵌入式套件完整。
