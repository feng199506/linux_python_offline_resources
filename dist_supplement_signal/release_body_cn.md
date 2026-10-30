# Linux 信号处理定向补充 v1

对应原 Release：[`lpo-full-20261030`](https://github.com/feng199506/linux_python_offline_resources/releases/tag/lpo-full-20261030)  
本包是**新的相关 Release**，不覆盖原 tar 资产。

目标：Linux x86-64 glibc 上的 CPython **3.10 / 3.12**。必须使用原树对应运行时，不要混装其它主版本。

## 本包做什么

在原 `03_signal_audio_image` 上增量追加（Kalman 相关 any-wheel 也从原 13 组复用进本包，便于只装 03 时一次装齐）：

- 傅里叶 / 频谱：复用原 03 NumPy、SciPy
- 小波：复用原 03 PyWavelets
- EMD / EEMD / CEEMDAN：新增 `EMD-signal`（导入名 **`PyEMD`**）
- Kalman：`filterpy` 实时滤波；`pykalman.smooth` 离线平滑（使用未来观测）

## 开发板

原板端是 Raspberry Pi OS Bookworm **Python 3.11** GPIO 包，不是 3.10/3.12。
`embedded_boards/aarch64/` 仅含 **aarch64 + 对应 CPython 3.10/3.12** 的 wheel（含 numpy/scipy/PyWavelets 的 aarch64 二进制）。
**没有**把 x86-64 二进制放进板端目录。
`embedded_boards/armv7l/`：EMD-signal / filterpy / pykalman 等 any-wheel 可用；numpy/scipy/PyWavelets/matplotlib **无官方 armv7l wheel**，源码与构建依赖单独保存，状态 **未构建、未验证**。

示例状态：**未执行验证**。

## 资产

| 文件 | SHA-256 |
| --- | --- |
| `linux_python310_x86_64_supplement_signal_v1.zip` | `3ac4e560bcd84c7791540b6e987a54f56ffbe9302256da79f5dd7a4596c22deb` |
| `linux_python312_x86_64_supplement_signal_v1.zip` | `5a263eb1fd7d3319f3e0864a19f1bd5c00e647c32b2222cc09b02020720f80d0` |
