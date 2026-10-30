# 开发板 armv7l / CPython 3.12.10 信号处理

PyPI 通常没有 numpy/scipy/PyWavelets 的 linux_armv7l 官方 wheel。兼容的 any-wheel（EMD-signal、filterpy、pykalman、pathos）已放入 [`packages_wheel/`](packages_wheel/)；缺 wheel 的包以源码形式放在 [`packages_sdist_unbuilt/`](packages_sdist_unbuilt/)，构建依赖在 [`build_deps_unbuilt/`](build_deps_unbuilt/)。状态：**未构建、未验证**。禁止用 x86-64 wheel 代替。
