# 电脑端通信与烧录 Python 包（CPython 3.12）

仅 **Linux x86-64**。不能拷到树莓派或 MicroPython 板端使用。  
本轮未安装、未连接硬件，示例未验证。包集合与 3.10 组相同，解释器必须是 3.12。

## 本组能做什么

在开发电脑上做串口、USB、CAN、MQTT、Modbus、MAVLink 以及部分 MCU 文件传输。不是飞控固件。

`esptool`、`rshell` 只有 sdist（[`sdist_needs_build/`](sdist_needs_build/)）。常用包说明与 3.10 组一致，见 [`../python_host_comms_py310/README_cn.md`](../python_host_comms_py310/README_cn.md) 与 [`../../../guides/常用工具与包用途索引_cn.md`](../../../guides/常用工具与包用途索引_cn.md) 第 12 节。
