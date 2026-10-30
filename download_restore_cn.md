# 下载与解压说明（Linux 通用科研 Python 离线资源库）

本 Release 有 33 个**不压缩 tar 包**，合计约 36.1 GiB。wheel、deb 和系统镜像本身已经压缩，再压缩几乎不省空间。所有包都解压到**同一个目录**，彼此不重叠，可以只下需要的部分。

> 这些资源是给 **Linux x86-64（glibc，参考 Ubuntu 22.04/24.04）** 和 ARM 开发板用的，不能在 Windows 上安装。在 Windows 上下载、解压，可以离线阅读全部说明；真正使用时，请把资源拷到 Linux 机器上。

## 按需下载

| 包 | 用途 | 是否必需 |
| --- | --- | --- |
| `linux_python_offline_01_common_docs_runtimes_cn_en.tar` | 离线首页 `index_cn.html`、全部说明与登记表、guides、Python 运行时（python-build-standalone 3.10/3.12、CPython 源码、pandoc）、scripts | **必下**（185 MiB） |
| `…_02_system_debs_ubuntu_…` | Ubuntu 22.04 / 24.04 系统依赖 deb | 目标机缺系统库时下载 |
| `…_03–08_env_py310_part*` | Python 3.10 的环境组（每个 part 只含完整的组） | 用 3.10 时按需下载 |
| `…_09–14_env_py312_part*` | Python 3.12 的环境组 | 用 3.12 时按需下载 |
| `…_15–17_embedded_tools_boards_part*` | 嵌入式：电脑端工具链、开发板核心、树莓派 ARM wheel/deb、MicroPython/CircuitPython 固件、清单 | 做嵌入式时下载 |
| `…_18–28_board_images_part*` | 开发板系统镜像（Armbian、Raspberry Pi OS、BeagleBoard、Radxa、StarFive、OpenWrt） | 只下所用板卡所在的 part |
| `…_29–33_jetson_l4t_nvidia_part*` | NVIDIA Jetson L4T BSP 与示例根文件系统 | 只给 Jetson 用；受 NVIDIA 许可约束，单独成包 |

各包的完整内容见下表；每个文件属于哪个包，见附件 `archive_index_cn.csv`。

| 包 | 内容 | 大小 |
| --- | --- | ---: |
| `linux_python_offline_01_common_docs_runtimes_cn_en.tar` | 离线首页 index_cn.html、库根说明与登记表、guides、Python 运行时（runtimes/、external_runtimes/）、scripts、state（必下） | 185 MiB |
| `linux_python_offline_02_system_debs_ubuntu_cn_en.tar` | Ubuntu 22.04 / 24.04 系统依赖 deb（运行、编译、扩展三类） | 763 MiB |
| `linux_python_offline_03_env_py310_part1_cn_en.tar` | environments 中 py310 环境组第 1/6 部分：01_scientific_notebook_py310 … 03_signal_audio_image_py310 | 1,490 MiB |
| `linux_python_offline_04_env_py310_part2_cn_en.tar` | environments 中 py310 环境组第 2/6 部分：04_pytorch_cpu_py310 … 07_tensorflow_cpu_py310 | 928 MiB |
| `linux_python_offline_05_env_py310_part3_cn_en.tar` | environments 中 py310 环境组第 3/6 部分：07b_gpflow_tf218_py310 … 09_huggingface_llm_py310 | 1,509 MiB |
| `linux_python_offline_06_env_py310_part4_cn_en.tar` | environments 中 py310 环境组第 4/6 部分：10_onnx_api_ui_py310 … 14_ml_tooling_py310 | 1,480 MiB |
| `linux_python_offline_07_env_py310_part5_cn_en.tar` | environments 中 py310 环境组第 5/6 部分：15_nlp_retrieval_py310 … 21_viz_dashboard_py310 | 1,277 MiB |
| `linux_python_offline_08_env_py310_part6_cn_en.tar` | environments 中 py310 环境组第 6/6 部分：21b_desktop_pyside6_py310 … 22_engineering_py310 | 276 MiB |
| `linux_python_offline_09_env_py312_part1_cn_en.tar` | environments 中 py312 环境组第 1/6 部分：01_scientific_notebook_py312 … 03_signal_audio_image_py312 | 1,329 MiB |
| `linux_python_offline_10_env_py312_part2_cn_en.tar` | environments 中 py312 环境组第 2/6 部分：04_pytorch_cpu_py312 … 07_tensorflow_cpu_py312 | 1,004 MiB |
| `linux_python_offline_11_env_py312_part3_cn_en.tar` | environments 中 py312 环境组第 3/6 部分：07b_gpflow_tf218_py312 … 09_huggingface_llm_py312 | 1,531 MiB |
| `linux_python_offline_12_env_py312_part4_cn_en.tar` | environments 中 py312 环境组第 4/6 部分：10_onnx_api_ui_py312 … 13_stats_timeseries_py312 | 1,212 MiB |
| `linux_python_offline_13_env_py312_part5_cn_en.tar` | environments 中 py312 环境组第 5/6 部分：14_ml_tooling_py312 … 20_documents_py312 | 1,516 MiB |
| `linux_python_offline_14_env_py312_part6_cn_en.tar` | environments 中 py312 环境组第 6/6 部分：21_viz_dashboard_py312 … 21b_desktop_pyside6_py312 | 442 MiB |
| `linux_python_offline_15_embedded_tools_boards_part1_cn_en.tar` | 嵌入式第 1/3 部分（电脑端工具链、开发板核心与 ARM wheel/deb、固件、清单）：embedded/README_cn.html … embedded/host_linux_x86_64 | 250 MiB |
| `linux_python_offline_16_embedded_tools_boards_part2_cn_en.tar` | 嵌入式第 2/3 部分（电脑端工具链、开发板核心与 ARM wheel/deb、固件、清单）：embedded/host_linux_x86_64/arduino_tools … embedded/host_linux_x86_64/arduino_tools | 1,479 MiB |
| `linux_python_offline_17_embedded_tools_boards_part3_cn_en.tar` | 嵌入式第 3/3 部分（电脑端工具链、开发板核心与 ARM wheel/deb、固件、清单）：embedded/host_linux_x86_64/gcc_arm_none_eabi … embedded/linux_sbcs/_shared/host_x86_64 | 515 MiB |
| `linux_python_offline_18_board_images_part1_cn_en.tar` | 开发板系统镜像第 1/11 部分：armbian_bananapif3_trixie … armbian_cuboxi_trixie | 1,316 MiB |
| `linux_python_offline_19_board_images_part2_cn_en.tar` | 开发板系统镜像第 2/11 部分：armbian_mba8mpxl_trixie … armbian_odroidm1s_trixie | 1,318 MiB |
| `linux_python_offline_20_board_images_part3_cn_en.tar` | 开发板系统镜像第 3/11 部分：armbian_odroidm2_trixie … armbian_orangepi3b_trixie | 1,334 MiB |
| `linux_python_offline_21_board_images_part4_cn_en.tar` | 开发板系统镜像第 4/11 部分：armbian_orangepi3lts_trixie … armbian_orangepipc_trixie | 1,279 MiB |
| `linux_python_offline_22_board_images_part5_cn_en.tar` | 开发板系统镜像第 5/11 部分：armbian_orangepizero3_trixie … beagle_ai64_debian12 | 1,186 MiB |
| `linux_python_offline_23_board_images_part6_cn_en.tar` | 开发板系统镜像第 6/11 部分：beagle_bbb_debian12 … beagle_bbb_debian12 | 406 MiB |
| `linux_python_offline_24_board_images_part7_cn_en.tar` | 开发板系统镜像第 7/11 部分：beagle_play_debian12 … openwrt_bpi_r3 | 1,436 MiB |
| `linux_python_offline_25_board_images_part8_cn_en.tar` | 开发板系统镜像第 8/11 部分：radxa_rock5b_bookworm … radxa_rock5b_bookworm | 1,472 MiB |
| `linux_python_offline_26_board_images_part9_cn_en.tar` | 开发板系统镜像第 9/11 部分：radxa_rockpi4b_bookworm … radxa_rockpi4b_bookworm | 1,371 MiB |
| `linux_python_offline_27_board_images_part10_cn_en.tar` | 开发板系统镜像第 10/11 部分：raspios_bookworm_lite_arm64 … raspios_bookworm_lite_armhf | 918 MiB |
| `linux_python_offline_28_board_images_part11_cn_en.tar` | 开发板系统镜像第 11/11 部分：starfive_vf2_debian … starfive_vf2_debian | 1,395 MiB |
| `linux_python_offline_29_jetson_l4t_nvidia_part1_cn_en.tar` | NVIDIA Jetson L4T 第 1/5 部分（受 NVIDIA 许可约束，单独成包）：jetson_nano_l4t32.7.4 … jetson_nano_l4t32.7.4 | 266 MiB |
| `linux_python_offline_30_jetson_l4t_nvidia_part2_cn_en.tar` | NVIDIA Jetson L4T 第 2/5 部分（受 NVIDIA 许可约束，单独成包）：jetson_nano_l4t32.7.4/Tegra_Linux_Sample-Root-Filesystem_R32.7.4_aarch64.tbz2 … jetson_nano_l4t32.7.4/Tegra_Linux_Sample-Root-Filesystem_R32.7.4_aarch64.tbz2 | 1,455 MiB |
| `linux_python_offline_31_jetson_l4t_nvidia_part3_cn_en.tar` | NVIDIA Jetson L4T 第 3/5 部分（受 NVIDIA 许可约束，单独成包）：jetson_orin_l4t36.4.4/Tegra_Linux_Sample-Root-Filesystem_R36.4.4_aarch64.tbz2 … jetson_orin_l4t36.4.4/Tegra_Linux_Sample-Root-Filesystem_R36.4.4_aarch64.tbz2 | 1,746 MiB |
| `linux_python_offline_32_jetson_l4t_nvidia_part4_cn_en.tar` | NVIDIA Jetson L4T 第 4/5 部分（受 NVIDIA 许可约束，单独成包）：jetson_orin_l4t36.4.4 … jetson_xavier_nx_l4t35.5.0 | 1,436 MiB |
| `linux_python_offline_33_jetson_l4t_nvidia_part5_cn_en.tar` | NVIDIA Jetson L4T 第 5/5 部分（受 NVIDIA 许可约束，单独成包）：jetson_xavier_nx_l4t35.5.0/Tegra_Linux_Sample-Root-Filesystem_R35.5.0_aarch64.tbz2 … jetson_xavier_nx_l4t35.5.0/Tegra_Linux_Sample-Root-Filesystem_R35.5.0_aarch64.tbz2 | 1,453 MiB |

## 在 Windows 上解压并离线阅读

Windows 10/11 自带 `tar`，在 PowerShell 或 cmd 中都能用：

```powershell
mkdir D:\lpo
cd D:\lpo
tar -xf "$env:USERPROFILE\Downloads\linux_python_offline_01_common_docs_runtimes_cn_en.tar"
# 其余下载的包同样解压到 D:\lpo
```

然后用浏览器打开 `D:\lpo\index_cn.html`，不需要联网：

- 每个 `README_cn.md` 和指南都有同名 `.html`，其中的路径可以点击，跳到本地文件或目录。
- 每个 CSV 登记表都有同名 `.html` 表格视图：文件名可以点击，定位到对应的 `.whl`、`.deb` 或固件；环境名可以点击，跳到该组。
- 原始 CSV 中含中文的已加 UTF-8 BOM，用 Excel 双击打开不会乱码。
- 只有 http(s) 链接（上游来源和官方文档）需要联网。
- 链接指向的包没有下载时，该链接打不开，这是正常的。

目录越短越好。包内最长相对路径为 169 个字符，解压到 `D:\lpo\` 时不会超过 Windows 的 260 字符限制。7-Zip 也可以解压。包内没有符号链接和硬链接，Windows 自带 `tar` 与 7-Zip 解压结果相同。

## 在 Linux 上使用

**建议把 tar 包本身拷到 Linux 上再解压**：Linux 的 `tar` 会还原可执行权限，而 Windows 上解压再拷过去，`.sh` 脚本和工具链二进制会丢失可执行位。

```bash
mkdir -p ~/lpo && cd ~/lpo
for t in /path/to/linux_python_offline_*_cn_en.tar; do tar -xf "$t"; done
```

如果已经是在 Windows 上解压后拷过去的，就用 `bash install_offline_en.sh` 运行脚本，工具链目录用 `chmod -R u+x` 补回权限。

安装步骤见 `guides/离线安装与使用_cn.html`；每个环境组的 `README_cn.html` 给出该组的安装命令。

## 校验

附件 `archive_index_cn.csv` 列出每个文件所在的包、大小和 SHA256。

```powershell
Get-FileHash .\runtimes\python_build_standalone\*.tar.gz -Algorithm SHA256
```

```bash
sha256sum environments/04_pytorch_cpu_py312/wheelhouse/*.whl
```

## 与原库的差异

- **没有放入发布包的内容**：原库的 `.git/`（本地历史）、`state/pip_cache/`（6.8 GB pip HTTP 缓存，不能当 wheelhouse 用，所需 wheel 都已在各组 `wheelhouse/` 中），以及 `__pycache__/`、`.pyc`。
- **新增**：每个 Markdown 和 CSV 的同名 `.html`、离线首页 `index_cn.html`；Markdown 中存在的本地路径改成了可点击的相对链接；含中文的 CSV 加了 BOM。全部改动见 `offline_changes_cn.csv`。
- wheel、deb、运行时、固件、镜像、锁定清单和安装脚本都**没有改动**。
- `environments/22_engineering_py310` 在原库中就没有完成（只有需求清单，没有 wheel），3.12 版本和 `23_general_utils` 也没有下载。原样保留。

## 状态

原库只做了静态检查（wheel 平台标签、glibc 下限、依赖闭包、校验和），**没有在目标机上实际安装、烧录或上板验证**。
