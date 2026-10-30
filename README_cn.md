# Linux 通用科研 Python 离线资源

目录：`linux_python_offline_resources/`

本仓库按用途准备 **Linux x86-64 / glibc / CPU** 科研 Python 离线环境，与 `windows_python_offline_resources/` 独立，不混用安装包。

- 总览：[`environments_overview_cn.md`](environments_overview_cn.md)
- 运行时清单：[`runtime_inventory_cn.csv`](runtime_inventory_cn.csv)
- 包清单：[`package_inventory_cn.csv`](package_inventory_cn.csv)
- 系统/外部依赖：[`external_dependencies_cn.csv`](external_dependencies_cn.csv)
- 兼容性问题：[`compatibility_issues_cn.csv`](compatibility_issues_cn.csv)
- 准备脚本：[`scripts/prepare_offline_en.py`](scripts/prepare_offline_en.py)（支持断点续跑）
- 补充说明（随增量包发布，不改原 01–11 wheelhouse）：
  - [`guides/常用工具与包用途索引_cn.md`](guides/%E5%B8%B8%E7%94%A8%E5%B7%A5%E5%85%B7%E4%B8%8E%E5%8C%85%E7%94%A8%E9%80%94%E7%B4%A2%E5%BC%95_cn.md)
  - [`guides/常见任务快速入门_cn.md`](guides/%E5%B8%B8%E8%A7%81%E4%BB%BB%E5%8A%A1%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8_cn.md)
  - [`guides/离线安装与使用_cn.md`](guides/%E7%A6%BB%E7%BA%BF%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8_cn.md)

默认参考 Ubuntu 22.04 与 24.04 LTS。不要声称适用于全部 Linux。
## 嵌入式开发板

见 [`embedded/README_cn.md`](embedded/README_cn.md)。电脑端工具与板端资源分开；固件不是 CPython wheel。

## 综合技术离线资料库（独立目录）

学习资料不在本仓库内，也不与大模型混放：

- 工程/信号/控制等：`/root/engineering_offline_library/`（入口 `00_portal/总入口.md`）
- 大模型：`/root/llm_lifecycle_resources/`
- Agent：`/root/ai_agent_resources/`
