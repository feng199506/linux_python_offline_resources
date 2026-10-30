# 常用工具与包用途索引

只解释**直接目标包**和用户会主动调用的工具。传递依赖见各环境 `requirements_lock_en.txt`，不在此写教程。

版本以各环境 lock / wheel 清单为准。下表 “3.10 / 3.12” 表示该组两种解释器都已下载对应 wheel（版本可能不同）。  
状态一律：**已下载、未在目标机安装或运行验证**。

图例：

- 联网：运行时是否还要访问网络（下载本身已完成不算）。
- 权重：是否还要模型/语料文件。
- 外部程序：是否还要 FFmpeg、Tesseract、浏览器、编译器等。
- 硬件：是否要 GPU、串口、开发板。

---

## 1. 科学计算、表格与 Notebook

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| numpy | 数组与线性代数 | 几乎所有数值代码 | 01，及多数组 | 3.10（2.2.6）/ 3.12（2.5.4）；07b 为 1.26.4 | 否 | 否 | 否（OpenMP 多已捆绑） | CPU |
| scipy | 统计、优化、信号处理 | 科学计算 | 01、02、03、11、13 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| pandas | 表格式数据 | 清洗、对齐、Excel/CSV | 01、12、13 等 | 3.10（2.3.3）/ 3.12（3.1.0） | 读本地文件否；读 URL 要网 | 否 | 否 | 否 |
| pyarrow | Arrow / Parquet | 列存读写 | 01、12 | 3.10（25.0.1）/ 3.12（26.0.0） | 否 | 否 | 否 | 否 |
| openpyxl / xlsxwriter | Excel 读写 | 报表 | 01、12、20 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| matplotlib / seaborn / plotly | 绘图 | 探索分析 | 01、21 | 3.10 / 3.12 | plotly 部分图要浏览器；默认否 | 否 | 否 | 否 |
| jupyterlab | Notebook 界面 | 交互分析 | 01、21 | 3.10 / 3.12（4.6.5） | 装扩展可能要网；本地否 | 否 | 浏览器打开 UI | 否 |
| sympy | 符号计算 | 公式推导 | 01 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| h5py / netCDF4 / xarray | 科学数组文件 | 气候、实验数据 | 01、12 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| polars | 高性能 DataFrame | 较大表格 | 12 | 3.10（2.0.0）/ 3.12（2.1.0） | 否 | 否 | 否 | CPU |
| duckdb | 嵌入式分析 SQL | 本地 Parquet/CSV 查询 | 12、18 | 3.10（1.5.6）/ 3.12（2.0.0） | 否 | 否 | 否 | 否 |
| dask | 延迟/分布式表与数组 | 内存放不下的表 | 12 | 3.10 / 3.12 | 多机调度才要网 | 否 | 否 | CPU |
| zarr | 分块数组存储 | 大规模阵列 | 12 | 3.10 / 3.12 | 对象存储才要网 | 否 | 否 | 否 |

官方文档： [NumPy](https://numpy.org/doc/stable/) · [pandas](https://pandas.pydata.org/docs/) · [SciPy](https://docs.scipy.org/doc/scipy/) · [Polars](https://docs.pola.rs/) · [DuckDB](https://duckdb.org/docs/) · [JupyterLab](https://jupyterlab.readthedocs.io/)

---

## 2. 量化指标、统计与时间序列

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| statsmodels | 回归、检验、部分时序 | 计量 | 02、13 | 3.10 / 3.12（0.15.0） | 否 | 否 | 否 | CPU |
| arch | GARCH 等波动率 | 金融时序 | 13 | 3.10 / 3.12（8.0.0） | 否 | 否 | 否 | CPU |
| linearmodels | 面板/IV | 计量 | 13 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| quantstats | 回测绩效指标与报告 | 策略评估 | 13 | 3.10 / 3.12（0.0.86） | **拉行情要网**（yfinance） | 否 | 否 | 否 |
| backtesting | 简易 OHLC 回测 | 规则策略 | 13 | 3.10 / 3.12（0.6.6） | 数据要自备 | 否 | 否 | 否 |
| statsforecast / sktime / pmdarima | 预测模型 | 时序预测 | 13 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| prophet | 加法时序模型 | 业务预测 | 13 | 3.10 / 3.12 | 否 | 否 | **CmdStan 未下载** | CPU |
| hmmlearn | 隐马尔可夫 | 状态序列 | 02、13 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |

`ta`（Technical Analysis）在 13 组直接依赖中列出，**未进入 py310 wheel 清单**，不要当已安装。`pandas-ta` 在 3.12 lock 中有 0.4.71b0，3.10 清单未见，使用前先看该环境 `wheel_inventory_cn.csv`。

官方文档： [statsmodels](https://www.statsmodels.org/stable/) · [arch](https://arch.readthedocs.io/) · [QuantStats](https://github.com/ranaroussi/quantstats) · [Prophet](https://facebook.github.io/prophet/)

---

## 3. 传统机器学习

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scikit-learn | 分类/回归/聚类/预处理 | 表格 ML | 02、14 | 3.10（1.7.2）/ 3.12（1.9.1） | 否 | 否 | 否 | CPU |
| xgboost / lightgbm / catboost | 梯度提升树 | 表格竞赛/生产 | 02 | 3.10 / 3.12 | 否 | 否 | 否 | CPU（非 GPU 包） |
| imbalanced-learn | 类别不平衡 | 抽样/合成 | 14 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| shap / lime / interpret | 解释模型 | 特征贡献 | 14 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| optuna | 超参搜索 | 调参 | 14 | 3.10 / 3.12（5.0.0） | 远程存储才要网 | 否 | 否 | CPU |
| mlflow | 实验跟踪 | 记录参数/指标 | 14 | 3.10 / 3.12（3.17.2） | 跟踪服务器才要网 | 否 | 否 | 否 |
| feature-engine / category-encoders / featuretools | 特征工程 | 表格特征 | 14 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |

官方文档： [scikit-learn](https://scikit-learn.org/stable/) · [XGBoost](https://xgboost.readthedocs.io/) · [SHAP](https://shap.readthedocs.io/) · [Optuna](https://optuna.readthedocs.io/) · [MLflow](https://mlflow.org/docs/latest/index.html)

---

## 4. 深度学习（仅 CPU 库，不含权重）

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| torch / torchvision / torchaudio | PyTorch CPU | 训练/推理代码 | 04、05、08、09 | 3.10 / 3.12（2.14.1+cpu） | 下权重要网 | **不含权重** | 否 | **CPU only**，非 CUDA |
| tensorflow-cpu / keras | TensorFlow CPU | 同上 | 07 | 3.10 / 3.12（2.21.0） | 下权重要网 | **不含权重** | 否 | CPU |
| gpflow | GPflow GPR | 与 TF 2.18 绑定 | 07b | 3.10 / 3.12（2.11.2）+ TF 2.18.0 + numpy&lt;2 | 否 | 否 | 否 | CPU |
| gpytorch / botorch | GPR / 贝叶斯优化 | PyTorch 路线 | 05 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| transformers | 预训练模型 API | NLP/多模态代码 | 09 | 3.10（5.20.2）/ 3.12（5.22.0） | **from_pretrained 默认联网** | **需自备** | 否 | CPU（慢） |
| datasets / tokenizers / accelerate / peft | 数据、分词、微调辅助 | 跟 transformers | 09 | 3.10 / 3.12 | Hub 访问要网 | 数据集要自备 | 否 | CPU |
| onnx / onnxruntime | ONNX CPU 推理 | 导出模型推理 | 10、15、16 | 3.10（ORT 1.23.2）/ 3.12（1.31.1） | 否 | 需 .onnx 文件 | 否 | CPU |
| gymnasium / stable-baselines3 | RL 接口与算法 | 小规模 RL | 08 | 3.10 / 3.12（SB3 2.9.2） | 否 | 否 | **无 Atari ROM / MuJoCo** | CPU |
| pymc / arviz / emcee | 贝叶斯 MCMC | 统计推断 | 06 | 3.10 / 3.12 | 否 | 否 | cmdstanpy 另需 CmdStan | CPU |
| cvxpy / casadi / osqp | 凸优化 / 最优控制 | 规划与控制 | 11 | 3.10 / 3.12 | 否 | 否 | slycot 未收录 | CPU |

官方文档： [PyTorch](https://pytorch.org/docs/stable/) · [TensorFlow](https://www.tensorflow.org/) · [Transformers](https://huggingface.co/docs/transformers) · [ONNX Runtime](https://onnxruntime.ai/docs/) · [Gymnasium](https://gymnasium.farama.org/)

---

## 5. 中文处理与检索

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| jieba | 中文分词 | 词频、检索预处理 | 15 | 3.10 / 3.12 | 否 | 自定义词典自备 | **仅 sdist** `jieba-0.42.1.tar.gz`，无 wheel | 否 |
| langdetect | 语言检测 | 语种过滤 | 15 | 3.10 / 3.12 | 否 | 否 | **仅 sdist** | 否 |
| nltk | 英文 NLP 工具箱 | 分词/词性 | 15 | 3.10 / 3.12（3.10.4） | **nltk.download 要网** | **语料未下载** | 否 | 否 |
| spacy | NLP 流水线 | 需语言模型 | 15 | 3.10 / 3.12（3.8.18） | 装模型要网 | **模型未下载** | 否 | 否 |
| tiktoken | BPE 计 token | 与 OpenAI 兼容分词 | 15 | 3.10 / 3.12（0.14.0） | 否 | 编码表多随包 | 否 | 否 |
| faiss-cpu | 向量近邻 | 本地检索 | 15 | 3.10 / 3.12（1.15.1） | 否 | 向量要自备 | 否 | CPU |
| chromadb / lancedb | 向量库客户端 | RAG 存储 | 15 | 3.10 / 3.12 | 远程服务才要网 | 否 | 否 | 否 |
| langchain / llama-index-core | RAG 编排 | 组装检索链 | 15 | 3.10 / 3.12 | 调 LLM API 要网 | 否 | 否 | 否 |

官方文档： [jieba](https://github.com/fxsjy/jieba) · [NLTK](https://www.nltk.org/) · [spaCy](https://spacy.io/usage) · [FAISS](https://github.com/facebookresearch/faiss/wiki) · [LangChain](https://python.langchain.com/)

---

## 6. PDF、Office 与文档转换

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pypdf | PDF 拆合、文本 | 轻量 PDF | 20 | 3.10 / 3.12（6.21.4） | 否 | 否 | 否 | 否 |
| pymupdf | PDF 渲染/提取 | 复杂版面 | 20 | 3.10（1.28.2）/ 3.12（2.0） | 否 | 否 | 否 | 否 |
| pdfplumber / pdfminer.six | 表格与文本提取 | 扫描件效果差 | 20 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| python-docx | Word | 生成/读取 docx | 20 | 3.10 / 3.12（1.2.0） | 否 | 否 | 否 | 否 |
| python-pptx | PowerPoint | 生成 pptx | 20 | 3.10 / 3.12（1.0.2） | 否 | 否 | 否 | 否 |
| openpyxl / xlsxwriter | Excel | 表格文件 | 12、20 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| reportlab | 程序化 PDF | 票据/报告 | 20 | 3.10 / 3.12（5.1.0） | 否 | 否 | 否 | 否 |
| weasyprint | HTML→PDF | 排版 | 20 | 3.10 / 3.12（70.0） | 否 | 否 | **Cairo/Pango** | 否 |
| pypandoc | 调 Pandoc | 格式互转 | 20 | 3.10 / 3.12（1.17） | 否 | 否 | **Pandoc 可执行文件未齐备** | 否 |
| markitdown | 文件转 Markdown | 预处理 | 20 | 3.10 / 3.12（0.1.9） | 部分 extras 要云服务 | 否 | 视输入格式 | 否 |

官方文档： [pypdf](https://pypdf.readthedocs.io/) · [PyMuPDF](https://pymupdf.readthedocs.io/) · [python-docx](https://python-docx.readthedocs.io/) · [python-pptx](https://python-pptx.readthedocs.io/) · [WeasyPrint](https://weasyprint.readthedocs.io/)

---

## 7. 图像、音视频

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pillow | 位图读写 | 缩放、格式转换 | 01、03、16、20 | 3.10 / 3.12（版本因组而异） | 否 | 否 | 否 | 否 |
| opencv-python-headless | 图像/视频数组 | 无 GUI 的 CV | 03、16 | 3.10 / 3.12（5.0.0.93） | 否 | 否 | 部分解码仍可能要 FFmpeg | 摄像头才要硬件 |
| scikit-image | 图像算法 | 滤波、分割 | 03、16 | 3.10 / 3.12 | 否 | 否 | 否 | CPU |
| librosa / soundfile | 音频分析/读写 | 波形、特征 | 03 | 3.10 / 3.12 | 否 | 否 | **libsndfile / FFmpeg 可能需要** | 否 |
| av / imageio / imageio-ffmpeg / moviepy / pydub | 容器编解码、剪辑 | 音视频处理 | 16 | 3.10 / 3.12 | 否 | 否 | **FFmpeg 强烈建议** | 否 |
| mne / wfdb | 脑电/心电 | 生理信号 | 03 | 3.10 / 3.12 | 公开库下载要网 | 否 | 否 | 否 |

官方文档： [Pillow](https://pillow.readthedocs.io/) · [OpenCV](https://docs.opencv.org/) · [librosa](https://librosa.org/doc/latest/index.html) · [PyAV](https://pyav.basswood-io.com/) · [MoviePy](https://zulko.github.io/moviepy/)

---

## 8. OCR

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pytesseract | 调 Tesseract | 印刷体 OCR | 16 | 3.10 / 3.12（0.3.13） | 否 | 语言包在 deb 中，**未安装验证** | **tesseract-ocr** | 否 |
| rapidocr-onnxruntime | ONNX OCR 封装 | 中英文检测识别 | 16 | 3.10 / 3.12（1.4.4，声明 &lt;3.13） | 首次是否再下模型**未验证** | wheel 内可能含 ONNX | 依赖 OpenCV | CPU |
| pdf2image | PDF 栅格化 | OCR 前处理 | 16 | 3.10 / 3.12 | 否 | 否 | **poppler** | 否 |
| pypdfium2 | PDF 渲染 | 同上 | 16 | 3.10 / 3.12 | 否 | 否 | 否（wheel 带库） | 否 |

未收录 PaddleOCR / EasyOCR 权重。官方文档： [pytesseract](https://pypi.org/project/pytesseract/) · [RapidOCR](https://rapidai.github.io/RapidOCRDocs/) · [Tesseract](https://tesseract-ocr.github.io/)

---

## 9. Web、浏览器自动化与爬虫

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fastapi / uvicorn | HTTP API | 本地服务 | 10、17 | 3.10 / 3.12 | 对外服务才要网 | 否 | 否 | 否 |
| flask / django | Web 框架 | 站点/后台 | 17 | 3.10 / 3.12（Flask 3.1.3，Django 5.2.18） | 同上 | 否 | 否 | 否 |
| httpx / requests | HTTP 客户端 | 调 API | 多组 | 3.10 / 3.12 | **访问远端要网** | 否 | 否 | 否 |
| scrapy | 爬虫框架 | 站点抓取 | 19 | 3.10 / 3.12（2.19.0） | **抓取要网** | 否 | 否 | 否 |
| beautifulsoup4 / lxml / parsel | HTML 解析 | 离线页面也可 | 19、20 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |
| playwright | 驱动 Chromium 等 | 浏览器自动化 | 19 | 3.10 / 3.12（1.64.1） | 装浏览器官方默认联网 | 否 | **浏览器内核未下载** | 否 |
| selenium | 驱动浏览器 | 同上 | 19 | 3.10 / 3.12（4.52.0） | webdriver-manager 会联网 | 否 | **浏览器+驱动未下载** | 否 |
| gradio / streamlit | 快速界面 | 演示模型 | 10 | 3.10 / 3.12 | 分享到 Hub 要网；本地可 | 否 | 浏览器打开 UI | 否 |

官方文档： [FastAPI](https://fastapi.tiangolo.com/) · [Flask](https://flask.palletsprojects.com/) · [Scrapy](https://docs.scrapy.org/) · [Playwright Python](https://playwright.dev/python/) · [Selenium](https://www.selenium.dev/documentation/)

---

## 10. 数据库客户端（不含服务器）

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sqlalchemy / alembic / sqlmodel | ORM 与迁移 | 应用数据层 | 18 | 3.10 / 3.12 | 连远程库要网 | 否 | 数据库服务器自备 | 否 |
| psycopg / asyncpg / pymysql / pymongo / redis | 驱动 | 对接已有库 | 18 | 3.10 / 3.12 | 连远程要网 | 否 | 对应服务器 | 否 |
| sqlite-utils / aiosqlite | SQLite | 本地文件库 | 18 | 3.10 / 3.12 | 否 | 否 | 否 | 否 |

官方文档： [SQLAlchemy](https://docs.sqlalchemy.org/) · [psycopg](https://www.psycopg.org/psycopg3/docs/)

---

## 11. 可视化界面与桌面

| 名称 | 作用 | 适用场景 | 环境组 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plotly / dash / panel / bokeh | 交互图与仪表板 | 内部看板 | 21、10 | 3.10 / 3.12 | 本地可 | 否 | 浏览器 | 否 |
| PySide6 | Qt 桌面 UI | 本地窗口程序 | 21b | 3.10 / 3.12（6.12.0） | 否 | 否 | 系统 xcb/OpenGL 库 | 显示器 |
| kaleido | Plotly 静态导出 | 出 PNG/PDF | 21 | 3.10 / 3.12 | 否 | 否 | 可能需额外浏览器组件，**未验证** | 否 |

官方文档： [Plotly](https://plotly.com/python/) · [Dash](https://dash.plotly.com/) · [PySide6](https://doc.qt.io/qtforpython-6/)

---

## 12. 串口、总线与开发板（主机 x86-64）

位于 [`embedded/host_linux_x86_64/python_host_comms_py310`](../embedded/host_linux_x86_64/python_host_comms_py310/) 与 `_py312`，**不要**装进科学计算 venv，也**不要**拷到 ARM 板。

| 名称 | 作用 | 适用场景 | Python | 联网 | 权重 | 外部程序 | 硬件 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pyserial 3.5 | UART | 调试串口 | 3.10 / 3.12 | 否 | 否 | 否 | **串口设备** |
| pyusb / hidapi / pyftdi | USB / HID / FTDI | 刷写、转串口 | 3.10 / 3.12 | 否 | 否 | udev 规则可能要 | USB 设备 |
| python-can / canopen | CAN | 车辆/工控 | 3.10 / 3.12 | 否 | 否 | SocketCAN 或适配器驱动 | CAN 接口 |
| paho-mqtt | MQTT 客户端 | 物联网消息 | 3.10 / 3.12 | **连 broker 要网或局域网** | 否 | broker 自备 | 否 |
| pymodbus / minimalmodbus | Modbus | 工业从站 | 3.10 / 3.12 | 网口或串口 | 否 | 否 | 总线设备 |
| pymavlink 2.4.50 | MAVLink | 无人机通信 | 3.10 / 3.12 | 视链路 | 否 | **不是飞控固件** | 飞控/数传 |
| mpremote / adafruit-ampy / circup | MicroPython 文件 | Pico/ESP REPL | 3.10 / 3.12 | 否 | 否 | 否 | 目标 MCU |
| esptool / rshell | ESP 烧录 / REPL | ESP32 | 仅 sdist | 否 | 否 | 可能需本机编译安装 sdist | ESP 芯片 |
| gpiozero 等 | 树莓派 GPIO | **仅板端** | Pi OS 3.11 | 否 | 否 | 系统 pigpio/lgpio | **树莓派** |

板端 ARM wheel 在 [`embedded/boards/raspberry_pi/`](../embedded/boards/raspberry_pi/)。MCU 固件在 [`embedded/firmware/`](../embedded/firmware/)。

官方文档： [pyserial](https://pyserial.readthedocs.io/) · [python-can](https://python-can.readthedocs.io/) · [Paho MQTT](https://eclipse.dev/paho/files/paho.mqtt.python/html/) · [pymavlink](https://mavlink.io/en/mavgen_python/) · [gpiozero](https://gpiozero.readthedocs.io/)

---

## 13. 用户会调用的外部程序（非 Python 包）

| 名称 | 作用 | 所在位置 | 说明 |
| --- | --- | --- | --- |
| python-build-standalone | 可解压 CPython | [`runtimes/python_build_standalone/`](../runtimes/python_build_standalone/) | 第三方构建；解压后才是解释器 |
| CPython 官方源码 | 自行编译 | [`runtimes/cpython_official_source/`](../runtimes/cpython_official_source/) | 不能直接运行 |
| pip.pyz | 主机 pip 引导 | [`scripts/pip.pyz`](../scripts/pip.pyz) | 准备脚本用，不是目标机必装 |
| FFmpeg | 音视频 | `system_dependencies/*/…debs` | 未 apt 安装 |
| Tesseract | OCR 引擎 | expansion_debs | 含 chi-sim 语言包文件，未安装验证 |
| Poppler | PDF 转图 | expansion_debs | pdf2image 依赖 |
| Cairo/Pango | WeasyPrint | expansion_debs | 未安装验证 |
| Pandoc | 文档转换 | [`external_runtimes/pandoc/`](../external_runtimes/pandoc/) 目前主要是索引 | **不要当成已有 pandoc 二进制** |
| Arduino CLI / 工具链 | MCU 编译烧录 | [`embedded/host_linux_x86_64/`](../embedded/host_linux_x86_64/) | 与 CPython 环境分开 |
| Playwright 浏览器 | 页面自动化 | **缺失** | 见 19 组说明 |

---

## 14. 传递依赖（只列原则）

`setuptools`、`wheel`、`certifi`、`urllib3`、`idna`、`six`、`packaging`、`typing-extensions`、`numpy` 作为依赖出现在许多 lock 中。  
不要单独为它们写教程。需要审计时打开该环境的 `requirements_lock_en.txt` 与 `wheel_inventory_cn.csv`。
