# 常见任务快速入门

示例按 **已下载版本** 编写，默认使用 CPython 3.10 对应环境（3.12 把目录名里的 `py310` 换成 `py312`，并核对该组 lock）。  
本轮 **未执行** 这些代码，一律视为 **示例未验证**。需要联网、模型、外部程序或硬件的步骤已标明，不能当成开箱即用。

安装步骤见 [`离线安装与使用_cn.md`](%E7%A6%BB%E7%BA%BF%E5%AE%89%E8%A3%85%E4%B8%8E%E4%BD%BF%E7%94%A8_cn.md)。先完成对应组的离线 `venv`，再用该 venv 的 `python`。

---

## 1. 数据分析（表格）

**环境：** [`environments/01_scientific_notebook_py310`](../environments/01_scientific_notebook_py310/)  
**包：** numpy 2.2.6，pandas 2.3.3，matplotlib 3.10.9

```python
# 示例未验证。仅读本地文件，不访问网络。
import numpy as np
import pandas as pd

df = pd.DataFrame(
    {"x": np.arange(5), "y": np.linspace(0, 1, 5)}
)
df.to_csv("out.csv", index=False)
print(df.describe())
```

更大表、Parquet、DuckDB 用 [`12_data_storage_py310`](../environments/12_data_storage_py310/)（polars 2.0.0，duckdb 1.5.6，pyarrow 25.0.1）：

```python
# 示例未验证
import duckdb
duckdb.sql("SELECT 1 AS n").show()
```

---

## 2. 量化指标

**环境：** [`environments/13_stats_timeseries_py310`](../environments/13_stats_timeseries_py310/)  
**包：** pandas 2.3.3，quantstats 0.0.86，arch 8.0.0，backtesting 0.6.6

`quantstats` 若调用 `extend_pandas()` 后再 `qs.reports.html(returns, "SPY")` 一类接口，会经 **yfinance 访问网络** 拉基准行情。离线只能喂本地收益率序列。

```python
# 示例未验证。使用本地序列，不调用 yfinance。
import numpy as np
import pandas as pd
import quantstats as qs

idx = pd.date_range("2024-01-02", periods=20, freq="B")
returns = pd.Series(np.random.default_rng(0).normal(0.0003, 0.01, size=20), index=idx)
print("sharpe", qs.stats.sharpe(returns))
print("max DD", qs.stats.max_drawdown(returns))
```

Prophet 还需要 **未下载的 CmdStan**，本页不给运行示例。

---

## 3. 机器学习（表格）

**环境：** [`environments/02_ml_stats_timeseries_em_py310`](../environments/02_ml_stats_timeseries_em_py310/)  
**包：** scikit-learn 1.7.2，xgboost 3.2.0（3.12 组 xgboost 为 3.4.1）

```python
# 示例未验证。拟合玩具数据，不下载数据集。
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
clf = RandomForestClassifier(n_estimators=50, random_state=0)
clf.fit(Xtr, ytr)
print(clf.score(Xte, yte))
```

解释性、调参加 [`14_ml_tooling_py310`](../environments/14_ml_tooling_py310/)（shap 0.49.1，optuna 5.0.0）。PyTorch 训练用 [`04_pytorch_cpu_py310`](../environments/04_pytorch_cpu_py310/)（torch 2.14.1+cpu），**无 CUDA、无预训练权重**。

```python
# 示例未验证。仅检查 CPU 张量，不加载 Hub 模型。
import torch
x = torch.zeros(2, 3)
print(x.device, torch.__version__)
```

---

## 4. 中文处理

**环境：** [`environments/15_nlp_retrieval_py310`](../environments/15_nlp_retrieval_py310/)  
**jieba / langdetect 没有 wheel**，源码包在 `sdist_needs_build/jieba-0.42.1.tar.gz`、`langdetect-1.0.9.tar.gz`。默认 `install_offline_en.sh` **不会**把它们装进 venv。若要分词，需先对 sdist 另装（示例未验证，且 sdist 安装可能需要本机构建环境）：

```bash
# 示例未验证
./venv/bin/python -m pip install --no-index \
  ./sdist_needs_build/jieba-0.42.1.tar.gz
```

```python
# 示例未验证。不下载 spaCy/NLTK 语料。
import jieba
print(list(jieba.cut("离线环境中的中文分词")))
```

`nltk.download(...)`、`spacy.cli.download(...)`、`SentenceTransformer(...)` **都要联网或预先放模型**，本页不演示。向量检索库 faiss-cpu 1.15.1 只提供索引 API，没有现成中文嵌入权重。

---

## 5. PDF / Office

**环境：** [`environments/20_documents_py310`](../environments/20_documents_py310/)  
**包：** pypdf 6.21.4，python-docx 1.2.0，python-pptx 1.0.2，openpyxl 3.1.5

```python
# 示例未验证。只写本地文件。
from pypdf import PdfWriter
from docx import Document
from openpyxl import Workbook

w = PdfWriter()
w.add_blank_page(width=72 * 8.27, height=72 * 11.69)
w.write("blank.pdf")

doc = Document()
doc.add_paragraph("hello")
doc.save("hello.docx")

wb = Workbook()
wb.active["A1"] = "n"
wb.save("hello.xlsx")
```

HTML 转 PDF（weasyprint 70.0）需要系统 **Cairo/Pango**，未安装前不要当可用。  
`pypandoc` 需要 **Pandoc 可执行文件**；本库 [`external_runtimes/pandoc/`](../external_runtimes/pandoc/) 不能当成已齐备二进制。

---

## 6. 音视频

**环境：** [`environments/16_media_ocr_py310`](../environments/16_media_ocr_py310/)（编解码）或 [`03_signal_audio_image_py310`](../environments/03_signal_audio_image_py310/)（librosa 0.11.0）  
**包：** av 17.1.0，moviepy 2.2.1，soundfile 0.14.0，opencv-python-headless 5.0.0.93

完整解码通常还要系统 **FFmpeg**（[`system_dependencies/`](../system_dependencies/) 里有 deb，**未在本机安装**）。

```python
# 示例未验证。不假设 FFmpeg 已在 PATH。
from PIL import Image
Image.new("RGB", (64, 64), "white").save("frame.png")
```

```python
# 示例未验证。若未装 FFmpeg，moviepy/av 可能失败。
import imageio.v3 as iio
arr = iio.imread("frame.png")
print(arr.shape)
```

不要对缺失的媒体文件或网络 URL 写“开箱即用”。

---

## 7. OCR

**环境：** [`environments/16_media_ocr_py310`](../environments/16_media_ocr_py310/)  
**包：** pytesseract 0.3.13，rapidocr-onnxruntime 1.4.4，pdf2image 1.17.0

pytesseract **没有**内置识别引擎，必须先有 `tesseract` 可执行文件和语言包（expansion_debs 中有 `tesseract-ocr`、`tesseract-ocr-chi-sim` 文件，**未 dpkg 安装、未验证路径**）。

```python
# 示例未验证。若 PATH 中没有 tesseract，会失败。
# 不能在未安装引擎时称为开箱即用。
import pytesseract
from PIL import Image

img = Image.new("L", (200, 60), 255)
# print(pytesseract.image_to_string(img, lang="eng"))
```

RapidOCR 可能在 wheel 内带 ONNX；是否还要额外下载 **未推理验证**。pdf2image 需要 **poppler**。

---

## 8. 浏览器自动化

**环境：** [`environments/19_scraping_automation_py310`](../environments/19_scraping_automation_py310/)  
**包：** playwright 1.64.1，selenium 4.52.0，scrapy 2.19.0，beautifulsoup4 4.15.0

Playwright **Python 包 ≠ 浏览器**。本库未下载 Chromium/Firefox/WebKit。官方 `playwright install` 默认访问网络。Selenium 的 `webdriver-manager` 同样会联网取驱动。

仅解析本地 HTML（不需要浏览器）：

```python
# 示例未验证。不访问网络。
from bs4 import BeautifulSoup
html = "<html><body><p>offline</p></body></html>"
print(BeautifulSoup(html, "lxml").p.text)
```

Scrapy 抓远程站点需要网络与目标站点授权，此处不给爬取示例。

Playwright 在浏览器官方安装完成前不要运行：

```python
# 示例未验证。当前补充包没有浏览器内核，预期失败。
# from playwright.sync_api import sync_playwright
```

---

## 9. 串口及开发板通信

**环境（主机）：** [`embedded/host_linux_x86_64/python_host_comms_py310`](../embedded/host_linux_x86_64/python_host_comms_py310/)  
**包：** pyserial 3.5，paho-mqtt 2.1.0，pymodbus 3.16.1，python-can 4.6.1，pymavlink 2.4.50  

需要 **真实串口/CAN/USB 设备**。本轮未连接硬件。列出端口而不打开设备：

```python
# 示例未验证。不打开端口、不发送数据。
from serial.tools import list_ports
for p in list_ports.comports():
    print(p.device, p.description)
```

打开串口（有设备时，示例未验证）：

```python
# 需要硬件。未验证。不要在无设备时当作成功。
# import serial
# ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
# ser.write(b"AT\r\n")
```

树莓派 GPIO 用板端 [`embedded/boards/raspberry_pi/`](../embedded/boards/raspberry_pi/)（Python 3.11，gpiozero 等），**不能**用上述主机 x86-64 wheel。  
MAVLink 只是通信库，**不是**飞控固件，不能当 ArduPilot/PX4 安装包。

MQTT 需要 broker；连公网 broker 要联网。Modbus/CAN 需要对应总线。

---

## 10. 环境对照（最小选择）

| 任务 | 目录 | 解释器 |
| --- | --- | --- |
| 数据分析 | [`01_scientific_notebook_py310`](../environments/01_scientific_notebook_py310/) | 3.10 |
| 量化指标 | [`13_stats_timeseries_py310`](../environments/13_stats_timeseries_py310/) | 3.10 |
| 机器学习 | [`02_ml_stats_timeseries_em_py310`](../environments/02_ml_stats_timeseries_em_py310/) 或 [`04_pytorch_cpu_py310`](../environments/04_pytorch_cpu_py310/) | 3.10 |
| 中文处理 | [`15_nlp_retrieval_py310`](../environments/15_nlp_retrieval_py310/) + jieba sdist | 3.10 |
| PDF/Office | [`20_documents_py310`](../environments/20_documents_py310/) | 3.10 |
| 音视频 | [`16_media_ocr_py310`](../environments/16_media_ocr_py310/) + FFmpeg deb | 3.10 |
| OCR | [`16_media_ocr_py310`](../environments/16_media_ocr_py310/) + Tesseract deb | 3.10 |
| 浏览器自动化 | [`19_scraping_automation_py310`](../environments/19_scraping_automation_py310/) + 自备浏览器 | 3.10 |
| 串口/开发板（电脑端） | [`embedded/host_linux_x86_64/python_host_comms_py310`](../embedded/host_linux_x86_64/python_host_comms_py310/) | 3.10 |

3.12 新项目把后缀改为 `_py312`，并核对该目录 README 中的版本差（例如 pandas 3.1.0、numpy 2.5.4、pymupdf 2.0）。
