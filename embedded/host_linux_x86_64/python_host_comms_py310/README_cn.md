# 电脑端通信与烧录 Python 包（CPython 3.10）

仅 **Linux x86-64**。不能拷到树莓派或 MicroPython 板端使用。  
本轮未安装、未连接硬件，示例未验证。

## 本组能做什么

在开发电脑上做串口、USB、CAN、MQTT、Modbus、MAVLink 以及部分 MCU 文件传输。这不是飞控固件，也不是板端系统镜像。

安装示例（未验证；本组无 `install_offline_en.sh`）：

```bash
python3.10 -m venv /tmp/host_comms
/tmp/host_comms/bin/python -m pip install --no-index --find-links wheelhouse \
  pyserial paho-mqtt pymodbus python-can pymavlink
```

`esptool`、`rshell` 只有 sdist，见 [`sdist_needs_build/`](sdist_needs_build/)。

## 常用包说明

| 包 | 版本 | 作用 | 额外依赖 | 官方文档 |
| --- | --- | --- | --- | --- |
| pyserial | 3.5 | UART | 串口设备 | [文档](https://pyserial.readthedocs.io/) |
| pyusb | 1.3.1 | USB | udev / 设备 | [文档](https://github.com/pyusb/pyusb) |
| python-can | 4.6.1 | CAN | SocketCAN 或适配器 | [文档](https://python-can.readthedocs.io/) |
| paho-mqtt | 2.1.0 | MQTT 客户端 | broker；公网要联网 | [文档](https://eclipse.dev/paho/files/paho.mqtt.python/html/) |
| pymodbus | 3.16.1 | Modbus | 总线或 TCP 从站 | [文档](https://pymodbus.readthedocs.io/) |
| pymavlink | 2.4.50 | MAVLink | 数传/飞控；非固件 | [文档](https://mavlink.io/en/mavgen_python/) |
| mpremote | 1.29.0 | MicroPython REPL | MCU | [文档](https://docs.micropython.org/en/latest/reference/mpremote.html) |

最小串口示例见 [`../../../guides/常见任务快速入门_cn.md`](../../../guides/常见任务快速入门_cn.md) 第 9 节。  
树莓派 GPIO 见 [`embedded/boards/raspberry_pi/`](../../boards/raspberry_pi/)，不要用本组 x86-64 wheel。
