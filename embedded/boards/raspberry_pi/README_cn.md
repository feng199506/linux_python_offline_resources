# 树莓派板端 Python 资源

适用：Raspberry Pi OS Bookworm，**板端** CPython 3.11。  
**不能**使用仓库里 Linux x86-64 的 3.10/3.12 wheel。

## 本组能做什么

在树莓派上调用 GPIO、I2C/SPI 包装、串口和部分 Adafruit Blinka 库。摄像头以系统 `python3-picamera2` 等 deb 为主，不是所有功能都有 wheel。

| 目录 | 架构 | 说明 |
| --- | --- | --- |
| [`bookworm_arm64/`](bookworm_arm64/) | aarch64 | 板端 wheel 与系统 deb |
| [`bookworm_armhf/`](bookworm_armhf/) | armv7 | 板端 wheel 与系统 deb |

专用库（如 `RPi.GPIO`）只给树莓派，不要套到 ODROID/Orange Pi。  
未在目标板上安装或接线验证。主机串口调试见 [`embedded/host_linux_x86_64/`](../../host_linux_x86_64/)。

文档：[gpiozero](https://gpiozero.readthedocs.io/) · [Blinka](https://docs.circuitpython.org/projects/blinka/)
