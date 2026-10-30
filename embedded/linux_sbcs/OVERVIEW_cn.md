# Linux 开发板离线镜像覆盖（已下载、未做目标板验证）

目录：[`embedded/linux_sbcs/_shared/images/`](_shared/images/)（约 20 GiB）。未安装、未烧录、未连接硬件。  
引导/设备树/厂商驱动若未另存，视为**包含在镜像或 L4T 包内**。  
匹配发行版的离线 deb/wheel 尚未按新板 ABI 补齐；树莓派 Bookworm 3.11 ARM 包仍用既有 [`embedded/boards/raspberry_pi/`](../boards/raspberry_pi/)。  
Arduino / ESP32 / Pico / STM32 **不计入**下表。

状态列统一：**已下载、未做目标板验证**。

## Raspberry Pi（官方 Raspberry Pi OS Bookworm Lite 2026-10-06）

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| Raspberry Pi 4 Model B | 共用 `raspios_bookworm_lite_arm64` Lite | aarch64 glibc | 3.11（Bookworm） | 既有 Pi arm64/armhf wheel+deb | 主机 rpi-imager 2.0.4 deb；EEPROM JSON | Trixie 镜像未下；未上板 |
| Raspberry Pi 5 | 同上 | aarch64 | 3.11 | 同上 | EEPROM 2712 JSON | 同上 |
| Raspberry Pi Zero 2 W | 64 位同上；另有 `raspios_bookworm_lite_armhf` | aarch64 / armhf | 3.11 | 同上 | rpi-imager | 同上 |
| Compute Module 4 / 5 | 共用 64 位 Lite | aarch64 | 3.11 | 同上 | 同上 | CM 专用 IO 板镜像未单列 |

## ODROID（Armbian Trixie current minimal，社区源已标注）

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| ODROID-N2 / N2+ | Armbian 26.8.1 Trixie current 6.18.43 minimal | aarch64 | 3.13（Trixie） | 未按 Trixie ABI 另下 | 主机 Etcher zip、rpi-imager（通用写卡） | Hardkernel 官方 Ubuntu 镜像因镜像站 403/404 未下 |
| ODROID-M1 | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 同上 |
| ODROID-M1S | Armbian community 26.11.0-trunk.108 Trixie | aarch64 | 3.13 | 未另下 | 同上 | trunk 构建，非稳定编号 |
| ODROID-M2 | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 官方镜像未下 |
| ODROID-XU4 | Armbian 26.8.1 Trixie current 6.6.143 | armhf | 3.13 | 未另下 | 同上 | ARMv7；官方 Ubuntu 未下 |
| ODROID-C4（H 系列代表） | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 官方未下 |

## Orange Pi（Armbian；官方站多为网盘，未用）

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| Orange Pi PC（H3） | Armbian community 26.11 trunk Trixie | armhf/aarch64 以镜像为准 | 3.13 | 未另下 | rkdeveloptool 源码（本板非 RK） | 官方 Ubuntu/Debian 未下 |
| Orange Pi PC2（H5） | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 官方未下 |
| Orange Pi 3 LTS（H6） | Armbian 26.8.2 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 官方未下 |
| Orange Pi Zero 3（H618） | Armbian community 26.11 trunk Trixie | aarch64 | 3.13 | 未另下 | 同上 | 官方未下 |
| Orange Pi 3B（RK3566） | Armbian community 26.11 trunk Trixie | aarch64 | 3.13 | 未另下 | rkdeveloptool 源码 | 官方未下 |
| Orange Pi 5（RK3588S） | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | rkdeveloptool 源码 | 官方未下 |

## Radxa

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| ROCK Pi 4B | 官方 `rock-pi-4b_bookworm_kde_r4` | aarch64 | 3.11（Bookworm） | 未按该桌面镜像另下 deb | rkdeveloptool 源码；sha512sum 已存 | KDE 桌面镜像偏大；未上板 |
| ROCK 5B | 官方 `rock-5b_bookworm_kde_b5` | aarch64 | 3.11 | 未另下 | 同上 | 5A/5C 未单下 |
| Radxa ZERO | Armbian 26.8.3 Trixie minimal | aarch64 | 3.13 | 未另下 | 同上 | 官方 GitHub 最新为 T 测试版，未采用 |

## Banana Pi

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| BPI-M5 | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 通用写卡工具 | 官方镜像在百度/Drive，未下 |
| BPI-M2S | Armbian 26.8.1 Trixie | aarch64 | 3.13 | 未另下 | 同上 | 同上 |
| BPI-F3 | Armbian 26.8.3 Trixie | riscv64 | 3.13 | 无 riscv64 科学 wheel | 同上 | RISC-V wheel 稀缺 |
| BPI-R3 | OpenWrt 24.10.4 sdcard（官方 OpenWrt） | aarch64 musl | OpenWrt Python ≠ CPython 科学栈 | 未下 OpenWrt opkg 包 | sha256sums + .asc | 不是通用 Debian；厂商 Linux 镜像未下 |

## BeagleBoard（官方 files.beagle.cc）

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| BeagleBone Black | Debian 12.11 base-vscode v6.12 armhf | armhf | 3.11 | 未按该镜像另下 | bmap-tools 源码 | 未上板 |
| BeagleBone AI-64 | Debian 12.7 minimal arm64 | aarch64 | 3.11 | 未另下 | 同上 | 未上板 |
| BeaglePlay | Debian 12.7 XFCE arm64 | aarch64 | 3.11 | 未另下 | 同上 | 桌面镜像偏大 |

## NVIDIA Jetson（公开 L4T，与通用 ARM64 **分开存放**）

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| Jetson Nano | L4T 32.7.4 BSP + Sample RootFS | aarch64（Tegra） | Ubuntu 18.04 → Python 3.6 | **未**混入通用 ARM64 wheel | BSP 内含 flash 脚本（未执行） | CUDA/TensorRT/SDK Manager 需 NVIDIA 账号；未下 |
| Jetson Xavier NX | L4T 35.5.0 BSP + Sample RootFS | aarch64 | Ubuntu 20.04 → Python 3.8 | 未混入通用 ARM64 | 同上 | CUDA 需账号；未下 |
| Jetson Orin Nano / Orin NX | 共用 L4T 36.4.4 BSP + Sample RootFS | aarch64 | Ubuntu 22.04 → Python 3.10 | 未混入通用 ARM64 | 同上 | 按型号分开引用同一 L4T；CUDA/JetPack 完整件需账号 |

## 工业与 RISC-V

| 板卡型号 | 系统镜像及版本 | CPU 架构 | Python 基线 | 已下载系统包与 wheel | 专用工具 | 未完成项 |
| --- | --- | --- | --- | --- | --- | --- |
| CuBox-i（i.MX6 代表） | Armbian 26.8.1 Trixie | armhf | 3.13 | 未另下 | 通用写卡 | NXP BSP 需账号，未下 |
| TQMa8MPxL / MBA8MPxL（i.MX8） | Armbian 26.8.4 Trixie | aarch64 | 3.13 | 未另下 | 同上 | NXP 官方 BSP 未下 |
| VisionFive 2 | StarFive Debian 202510 Wayland img.bz2 | riscv64 | Bookworm 系 3.11（厂商镜像） | 无完整 riscv64 wheelhouse | 仓库密钥已下 | 未解压、未上板 |

## 主机 x86-64 写卡/恢复工具（独立目录）

已落盘：`rpi-imager_2.0.4_amd64.deb`、`balenaEtcher-linux-x64-2.1.9.zip`、`rkdeveloptool` 源码、`bmap-tools` 源码、EEPROM recovery JSON。  
USBImager 预编译包 URL 无效（接近 0 字节/失败），仅留下源码尝试记录。交叉编译器 deb 未下。

## 共享缓存说明

镜像按板卡子目录存放，多型号共用同一文件时在上表写明。尚未生成每板 `refs.json` 打包脚本。全部套件 **已下载、未做目标板验证**。
