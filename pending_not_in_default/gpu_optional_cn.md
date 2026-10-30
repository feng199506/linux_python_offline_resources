# GPU 待选（未下载）

硬件型号、驱动和 CUDA 版本未知，因此 **没有** 下载 CUDA/cuDNN 或 GPU wheel。

若目标机器确认具备 NVIDIA GPU，需要单独准备，且不得并入当前 CPU 环境：

- PyTorch：使用与驱动匹配的官方 CUDA 索引（例如 `https://download.pytorch.org/whl/cu128`），版本必须与驱动/CUDA 兼容
- TensorFlow：Linux 原生 GPU 构建与 WSL2 方案不同，需按官方文档单独锁定
- ONNX Runtime：使用 `onnxruntime-gpu`，不要与 `onnxruntime` CPU 混装

在目标机器先采集：`nvidia-smi`、驱动版本、CUDA 版本、GPU 型号，再决定下载哪一套。
