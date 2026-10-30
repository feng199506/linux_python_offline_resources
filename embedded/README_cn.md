# 嵌入式开发离线资源

目录：[`linux_python_offline_resources/embedded/`](./)

电脑端与开发板端 **分开保存**。Linux x86-64 wheel **不能**代替树莓派 ARM wheel，也不能代替 MicroPython/CircuitPython 固件。

## 结构

- [`host_linux_x86_64/`](host_linux_x86_64/)：在 x86-64 Linux 电脑上编译、烧录、调试、串口/USB/网络通信
- [`boards/`](boards/)：按板卡系列、架构与系统版本存放核心、SDK、系统 deb、ARM wheel
- [`firmware/micropython/`](firmware/micropython/) 与 [`firmware/circuitpython/`](firmware/circuitpython/)：固件与板端库，不按 CPython wheel 环境处理
- [`inventories/`](inventories/)：分类清单；**不要用 wheel 数量代表嵌入式环境完整**

## 本轮下载计数（文件级，非完整性）

- 电脑端/板端 Python 套件条目：3
- 电脑端工具链条目：33
- 开发板核心条目：11
- 固件/板端库条目：14
- 板端系统 deb 条目：26
- 未获取：见 [`inventories/missing_cn.csv`](inventories/missing_cn.csv)（16 条）

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

主机通信包的用途与串口示例见仓库 [`guides/常用工具与包用途索引_cn.md`](../guides/%E5%B8%B8%E7%94%A8%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%8C%85%E7%94%A8%E9%80%94%E7%B4%A2%E5%BC%95_cn.md) 第 12 节、[`guides/常见任务快速入门_cn.md`](../guides/%E5%B8%B8%E8%A7%81%E4%BB%BB%E5%8A%A1%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8_cn.md) 第 9 节。
