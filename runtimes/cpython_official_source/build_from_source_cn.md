# CPython 官方源码包（备选）

`Python-*.tar.xz` 是 python.org 官方源码。**源码包本身不能直接运行。**

从源码构建仍需要目标机器上的编译器与开发库，例如 Ubuntu 上：

```bash
sudo apt install build-essential pkg-config libssl-dev zlib1g-dev libffi-dev \
  libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev libncurses-dev \
  uuid-dev tk-dev libgdbm-dev libgdbm-compat-dev
./configure --prefix=/opt/python-3.x.x --enable-optimizations
make -j"$(nproc)"
make install
```

本仓库若提供 `system_dependencies/*/build_debs/`，也只是按 Ubuntu 官方索引解析的 `.deb` 闭包，**不能**替代在对应发行版上用 `dpkg`/`apt` 正确安装，且本轮没有在当前机器安装它们。

官方构建指南：https://devguide.python.org/getting-started/setup-building/
