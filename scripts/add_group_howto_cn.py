#!/usr/bin/env python3
"""Insert 本组能做什么 sections into environment READMEs. Does not touch wheelhouses."""
from __future__ import annotations

from pathlib import Path

ROOT = Path("/root/linux_python_offline_resources")
ENV = ROOT / "environments"
GUIDE = "../../guides"

DOCS = {
    "01_scientific_notebook": {
        "can": "做数组运算、表格清洗、本地绘图和 JupyterLab Notebook。适合日常数据分析入门。不含深度学习框架。",
        "pkgs": [
            ("numpy", "https://numpy.org/doc/stable/", "N 维数组", "否"),
            ("pandas", "https://pandas.pydata.org/docs/", "表格式数据", "读 URL 才要网"),
            ("scipy", "https://docs.scipy.org/doc/scipy/", "科学算法", "否"),
            ("matplotlib", "https://matplotlib.org/stable/", "静态图", "否"),
            ("jupyterlab", "https://jupyterlab.readthedocs.io/", "Notebook UI", "浏览器；装扩展可能要网"),
            ("openpyxl", "https://openpyxl.readthedocs.io/", "Excel", "否"),
            ("pyarrow", "https://arrow.apache.org/docs/python/", "Parquet/Arrow", "否"),
        ],
    },
    "02_ml_stats_timeseries_em": {
        "can": "做 sklearn 流水线、XGBoost/LightGBM/CatBoost 树模型、statsmodels 统计和 HMM。CPU 表格机器学习。不含 PyTorch/TensorFlow。",
        "pkgs": [
            ("scikit-learn", "https://scikit-learn.org/stable/", "经典 ML API", "否"),
            ("xgboost", "https://xgboost.readthedocs.io/", "提升树", "CPU 包，非 GPU"),
            ("lightgbm", "https://lightgbm.readthedocs.io/", "提升树", "CPU"),
            ("catboost", "https://catboost.ai/docs/", "提升树", "CPU"),
            ("statsmodels", "https://www.statsmodels.org/stable/", "统计模型", "否"),
            ("hmmlearn", "https://hmmlearn.readthedocs.io/", "HMM", "否"),
        ],
    },
    "03_signal_audio_image": {
        "can": "做图像数组处理、小波、音频特征和部分生理信号读写。默认 OpenCV headless。完整音频解码仍可能要系统 FFmpeg。",
        "pkgs": [
            ("opencv-python-headless", "https://docs.opencv.org/", "图像/视频数组", "FFmpeg 可能仍需要"),
            ("scikit-image", "https://scikit-image.org/docs/stable/", "图像算法", "否"),
            ("Pillow", "https://pillow.readthedocs.io/", "位图 IO", "否"),
            ("librosa", "https://librosa.org/doc/latest/index.html", "音频特征", "可能要 FFmpeg/sndfile"),
            ("soundfile", "https://python-soundfile.readthedocs.io/", "音频读写", "libsndfile"),
            ("mne", "https://mne.tools/stable/", "脑电", "公开数据集要网"),
            ("PyWavelets", "https://pywavelets.readthedocs.io/", "小波", "否"),
        ],
    },
    "04_pytorch_cpu": {
        "can": "在 CPU 上编写 PyTorch 训练/推理代码。wheel 来自官方 CPU 索引。不含 CUDA，不含模型权重。",
        "pkgs": [
            ("torch", "https://pytorch.org/docs/stable/", "张量与自动微分", "from_pretrained/下权重要网"),
            ("torchvision", "https://pytorch.org/vision/stable/", "视觉工具", "示例数据集要网或自备"),
            ("torchaudio", "https://pytorch.org/audio/stable/", "音频工具", "解码可能要 FFmpeg"),
        ],
    },
    "05_gpr_bayesopt": {
        "can": "用 GPyTorch/BoTorch 做高斯过程与贝叶斯优化（PyTorch CPU）。不要和 GPflow/TensorFlow 组混装。",
        "pkgs": [
            ("gpytorch", "https://docs.gpytorch.ai/", "GPR", "否"),
            ("botorch", "https://botorch.org/docs/introduction", "贝叶斯优化", "否"),
            ("torch", "https://pytorch.org/docs/stable/", "后端", "CPU only"),
        ],
    },
    "06_bayesian_mcmc": {
        "can": "用 PyMC、ArviZ、emcee 做贝叶斯推断与诊断。cmdstanpy 只是 Python 包，CmdStan 编译器未下载。",
        "pkgs": [
            ("pymc", "https://www.pymc.io/", "概率编程", "否"),
            ("arviz", "https://python.arviz.org/", "后验诊断", "否"),
            ("emcee", "https://emcee.readthedocs.io/", "MCMC", "否"),
            ("cmdstanpy", "https://mc-stan.org/cmdstanpy/", "Stan 前端", "需要未收录的 CmdStan"),
        ],
    },
    "07_tensorflow_cpu": {
        "can": "在 CPU 上使用 TensorFlow 2.21 与 Keras。不要与 07b（TF 2.18 + numpy<2）合并。不含 GPU/CUDA，不含权重。",
        "pkgs": [
            ("tensorflow-cpu", "https://www.tensorflow.org/", "TF CPU", "下权重/数据集要网"),
            ("keras", "https://keras.io/", "高层 API", "同上"),
        ],
    },
    "07b_gpflow_tf218": {
        "can": "运行官方对齐的 GPflow 2.11.2 + TensorFlow 2.18 + TFP 0.25（numpy<2）。仅此组。",
        "pkgs": [
            ("gpflow", "https://gpflow.github.io/GPflow/", "GPR（TF）", "否"),
            ("tensorflow-cpu", "https://www.tensorflow.org/", "TF 2.18.0", "不要换成 2.21"),
            ("tensorflow-probability", "https://www.tensorflow.org/probability", "TFP 0.25", "否"),
        ],
    },
    "08_rl_basics": {
        "can": "用 Gymnasium 与 Stable-Baselines3 写小型强化学习实验。不含 Atari ROM、MuJoCo 或大型仿真器。",
        "pkgs": [
            ("gymnasium", "https://gymnasium.farama.org/", "RL 环境 API", "第三方 ROM 未收录"),
            ("stable-baselines3", "https://stable-baselines3.readthedocs.io/", "RL 算法", "依赖 PyTorch CPU"),
            ("torch", "https://pytorch.org/docs/stable/", "后端", "CPU"),
        ],
    },
    "09_huggingface_llm": {
        "can": "调用 transformers/tokenizers/datasets/peft 的 Python API。这是库，不是模型仓库。from_pretrained 默认访问 Hub。",
        "pkgs": [
            ("transformers", "https://huggingface.co/docs/transformers", "模型 API", "权重需自备或联网"),
            ("datasets", "https://huggingface.co/docs/datasets", "数据集 API", "下载数据要网"),
            ("tokenizers", "https://huggingface.co/docs/tokenizers", "分词", "否"),
            ("accelerate", "https://huggingface.co/docs/accelerate", "训练辅助", "否"),
            ("peft", "https://huggingface.co/docs/peft", "参数高效微调", "基座权重自备"),
            ("huggingface_hub", "https://huggingface.co/docs/huggingface_hub", "Hub 客户端", "联网"),
        ],
    },
    "10_onnx_api_ui": {
        "can": "用 ONNX Runtime CPU 做推理骨架，并用 FastAPI/Gradio/Streamlit 做本地界面。onnxruntime-gpu 不在本环境。",
        "pkgs": [
            ("onnxruntime", "https://onnxruntime.ai/docs/", "ONNX CPU 推理", "需要 .onnx 文件"),
            ("onnx", "https://onnx.ai/", "模型格式", "否"),
            ("fastapi", "https://fastapi.tiangolo.com/", "HTTP API", "对外才要网"),
            ("gradio", "https://www.gradio.app/docs/", "演示 UI", "分享 Hub 要网"),
            ("streamlit", "https://docs.streamlit.io/", "数据应用 UI", "本地浏览器"),
        ],
    },
    "11_optimization_control": {
        "can": "用 CVXPY、OSQP、Clarabel、CasADi 和 python-control 做凸优化与控制计算。slycot 未收录。",
        "pkgs": [
            ("cvxpy", "https://www.cvxpy.org/", "凸优化建模", "否"),
            ("casadi", "https://web.casadi.org/docs/", "最优控制/符号", "否"),
            ("osqp", "https://osqp.org/docs/", "QP 求解器", "否"),
            ("control", "https://python-control.readthedocs.io/", "控制工具箱", "部分功能要 slycot（未收录）"),
        ],
    },
    "12_data_storage": {
        "can": "处理较大表格、Parquet/HDF5/Zarr/Delta、DuckDB SQL 和 Dask 调度。不含 GPU。对象存储 SDK 连云才要网。",
        "pkgs": [
            ("polars", "https://docs.pola.rs/", "高性能 DataFrame", "否"),
            ("duckdb", "https://duckdb.org/docs/", "嵌入式 SQL", "否"),
            ("pyarrow", "https://arrow.apache.org/docs/python/", "列存", "否"),
            ("dask", "https://docs.dask.org/", "延迟计算", "多机才要网"),
            ("zarr", "https://zarr.readthedocs.io/", "分块数组", "否"),
            ("h5py", "https://docs.h5py.org/", "HDF5", "否"),
            ("deltalake", "https://delta-io.github.io/delta-rs/python/", "Delta 表", "远端存储要网"),
        ],
    },
    "13_stats_timeseries": {
        "can": "做计量、波动率、变点、时序预测和基于本地收益率的绩效指标。quantstats 拉基准行情会走 yfinance 网络。Prophet 缺 CmdStan。",
        "pkgs": [
            ("statsmodels", "https://www.statsmodels.org/stable/", "计量", "否"),
            ("arch", "https://arch.readthedocs.io/", "GARCH", "否"),
            ("quantstats", "https://github.com/ranaroussi/quantstats", "绩效指标", "yfinance 要网；请喂本地序列"),
            ("backtesting", "https://kernc.github.io/backtesting.py/", "OHLC 回测", "数据自备"),
            ("statsforecast", "https://nixtlaverse.nixtla.io/statsforecast", "预测", "否"),
            ("sktime", "https://www.sktime.net/", "时序 ML", "否"),
            ("prophet", "https://facebook.github.io/prophet/", "加法模型", "需要未下载的 CmdStan"),
        ],
    },
    "14_ml_tooling": {
        "can": "做特征工程、不平衡学习、SHAP/LIME 解释、Optuna 调参和 MLflow 跟踪。不含训练框架本体。",
        "pkgs": [
            ("shap", "https://shap.readthedocs.io/", "特征贡献", "否"),
            ("optuna", "https://optuna.readthedocs.io/", "超参搜索", "远程存储才要网"),
            ("mlflow", "https://mlflow.org/docs/latest/index.html", "实验跟踪", "跟踪服务器才要网"),
            ("imbalanced-learn", "https://imbalanced-learn.org/", "类别不平衡", "否"),
            ("feature-engine", "https://feature-engine.readthedocs.io/", "特征变换", "否"),
            ("scikit-learn", "https://scikit-learn.org/stable/", "基线模型", "否"),
        ],
    },
    "15_nlp_retrieval": {
        "can": "调用分词、稀疏/向量检索和 RAG 编排库。jieba/langdetect 仅有 sdist。不含 spaCy/NLTK 语料，不含嵌入模型权重。",
        "pkgs": [
            ("jieba", "https://github.com/fxsjy/jieba", "中文分词", "仅 sdist，默认安装脚本不装"),
            ("nltk", "https://www.nltk.org/", "英文 NLP", "nltk.download 要网；语料未下载"),
            ("spacy", "https://spacy.io/usage", "NLP 流水线", "模型未下载"),
            ("faiss-cpu", "https://github.com/facebookresearch/faiss/wiki", "向量检索", "向量自备"),
            ("chromadb", "https://docs.trychroma.com/", "向量库", "远程才要网"),
            ("langchain", "https://python.langchain.com/", "RAG 编排", "调 LLM API 要网"),
            ("tiktoken", "https://github.com/openai/tiktoken", "token 计数", "否"),
        ],
    },
    "16_media_ocr": {
        "can": "做图像/音视频读写接口和 OCR 调用。pytesseract 需要 Tesseract；pdf2image 需要 Poppler；编解码建议 FFmpeg。不含 PaddleOCR 权重。",
        "pkgs": [
            ("opencv-python-headless", "https://docs.opencv.org/", "图像数组", "否"),
            ("av", "https://pyav.basswood-io.com/", "容器解码", "FFmpeg 建议具备"),
            ("moviepy", "https://zulko.github.io/moviepy/", "剪辑", "FFmpeg"),
            ("pytesseract", "https://pypi.org/project/pytesseract/", "Tesseract 包装", "必须有 tesseract 可执行文件"),
            ("rapidocr-onnxruntime", "https://rapidai.github.io/RapidOCRDocs/", "ONNX OCR", "是否另下模型未验证"),
            ("pdf2image", "https://github.com/Belval/pdf2image", "PDF 转图", "需要 poppler"),
            ("soundfile", "https://python-soundfile.readthedocs.io/", "音频", "libsndfile"),
        ],
    },
    "17_web_services": {
        "can": "搭建 FastAPI/Flask/Django 服务、ASGI/WSGI 服务器和 Redis 任务队列客户端。不含 Nginx、数据库服务器或 Redis 服务端。",
        "pkgs": [
            ("fastapi", "https://fastapi.tiangolo.com/", "API 框架", "对外服务要网"),
            ("flask", "https://flask.palletsprojects.com/", "Web 框架", "同上"),
            ("django", "https://docs.djangoproject.com/", "全栈 Web", "同上"),
            ("uvicorn", "https://www.uvicorn.org/", "ASGI", "否"),
            ("gunicorn", "https://docs.gunicorn.org/", "WSGI", "否"),
            ("celery", "https://docs.celeryq.dev/", "任务队列客户端", "需要 broker"),
            ("redis", "https://redis.readthedocs.io/", "Redis 客户端", "需要 Redis 服务"),
        ],
    },
    "18_database": {
        "can": "用 SQLAlchemy/Alembic 和各数据库驱动访问 PostgreSQL/MySQL/SQLite/Redis/Mongo。本环境没有数据库服务器。",
        "pkgs": [
            ("sqlalchemy", "https://docs.sqlalchemy.org/", "ORM", "连远程要网"),
            ("alembic", "https://alembic.sqlalchemy.org/", "迁移", "否"),
            ("psycopg", "https://www.psycopg.org/psycopg3/docs/", "PostgreSQL", "需要服务器"),
            ("pymysql", "https://pymysql.readthedocs.io/", "MySQL", "需要服务器"),
            ("pymongo", "https://pymongo.readthedocs.io/", "MongoDB", "需要服务器"),
            ("redis", "https://redis.readthedocs.io/", "Redis", "需要服务器"),
            ("duckdb", "https://duckdb.org/docs/", "本地分析库", "否"),
        ],
    },
    "19_scraping_automation": {
        "can": "解析 HTML、写 Scrapy 爬虫、调用 Playwright/Selenium API。浏览器内核和驱动未下载。Playwright/Selenium 当前不能当开箱即用。",
        "pkgs": [
            ("beautifulsoup4", "https://www.crummy.com/software/BeautifulSoup/bs4/doc/", "HTML 解析", "本地文件否"),
            ("lxml", "https://lxml.de/", "XML/HTML", "否"),
            ("scrapy", "https://docs.scrapy.org/", "爬虫框架", "抓远程要网"),
            ("playwright", "https://playwright.dev/python/", "浏览器自动化", "内核未下载；官方 install 要网"),
            ("selenium", "https://www.selenium.dev/documentation/", "浏览器自动化", "驱动/浏览器未下载"),
            ("httpx", "https://www.python-httpx.org/", "HTTP 客户端", "访问远端要网"),
        ],
    },
    "20_documents": {
        "can": "读写 PDF/Word/PPT/Excel，以及部分 HTML/Markdown 转换。WeasyPrint 要 Cairo；pypandoc 要 Pandoc 二进制（本库未齐备）。",
        "pkgs": [
            ("pypdf", "https://pypdf.readthedocs.io/", "轻量 PDF", "否"),
            ("pymupdf", "https://pymupdf.readthedocs.io/", "PDF 渲染/提取", "否"),
            ("python-docx", "https://python-docx.readthedocs.io/", "Word", "否"),
            ("python-pptx", "https://python-pptx.readthedocs.io/", "PPT", "否"),
            ("openpyxl", "https://openpyxl.readthedocs.io/", "Excel", "否"),
            ("reportlab", "https://www.reportlab.com/docs/reportlab-userguide.pdf", "生成 PDF", "否"),
            ("weasyprint", "https://weasyprint.readthedocs.io/", "HTML→PDF", "Cairo/Pango"),
            ("pypandoc", "https://github.com/JessicaTegner/pypandoc", "调 Pandoc", "Pandoc 未齐备"),
        ],
    },
    "21_viz_dashboard": {
        "can": "做 Plotly/Bokeh/Altair 交互图和 Dash/Panel/Voila 仪表板。桌面 Qt 见 21b。Streamlit 在 10 组。",
        "pkgs": [
            ("plotly", "https://plotly.com/python/", "交互图", "浏览器"),
            ("dash", "https://dash.plotly.com/", "仪表板", "本地 HTTP"),
            ("panel", "https://panel.holoviz.org/", "仪表板", "本地 HTTP"),
            ("bokeh", "https://docs.bokeh.org/", "交互图", "浏览器"),
            ("altair", "https://altair-viz.github.io/", "声明式统计图", "否"),
            ("kaleido", "https://github.com/plotly/Kaleido", "静态导出", "是否还需组件未验证"),
        ],
    },
    "21b_desktop_pyside6": {
        "can": "写 PySide6 桌面窗口程序。不要和 PyQt6 混装。目标机可能还要 xcb/OpenGL 系统库。需要显示器。",
        "pkgs": [
            ("PySide6", "https://doc.qt.io/qtforpython-6/", "Qt 绑定", "系统 GUI 库；需要显示器"),
            ("qtpy", "https://qtpy.readthedocs.io/", "Qt 抽象层", "否"),
            ("pyqtgraph", "https://www.pyqtgraph.org/", "科学绘图控件", "否"),
        ],
    },
}


def pins(env_dir: Path) -> dict[str, str]:
    inv = env_dir / "wheel_inventory_cn.csv"
    out: dict[str, str] = {}
    if not inv.exists():
        return out
    for line in inv.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split(",")
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    lock = env_dir / "requirements_lock_en.txt"
    if lock.exists():
        for line in lock.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "==" in line and not line.startswith("#"):
                n, v = line.split("==", 1)
                n = n.split("[")[0].strip()
                out.setdefault(n, v)
                out.setdefault(n.replace("_", "-"), v)
    return out


def ver_of(p: dict[str, str], name: str) -> str:
    keys = [name, name.replace("-", "_"), name.replace("_", "-")]
    if name.lower() == "pillow":
        keys += ["Pillow", "pillow"]
    if name.lower() == "scikit-learn":
        keys += ["sklearn", "scikit_learn"]
    if name.lower() == "opencv-python-headless":
        keys += ["opencv_python_headless"]
    if name.lower() == "beautifulsoup4":
        keys += ["bs4"]
    if name.lower() == "stable-baselines3":
        keys += ["stable_baselines3"]
    if name.lower() == "huggingface_hub":
        keys += ["huggingface-hub"]
    if name.lower() == "tensorflow-cpu":
        keys += ["tensorflow_cpu"]
    if name.lower() == "pywavelets":
        keys += ["PyWavelets", "pywt"]
    for k in keys:
        if k in p:
            return p[k]
        for existing, ver in p.items():
            if existing.lower() == k.lower():
                return ver
    if name == "jieba":
        return "0.42.1（sdist）"
    if name == "langdetect":
        return "1.0.9（sdist）"
    return "见 lock"


def section(stem: str, env_dir: Path, py: str) -> str:
    spec = DOCS[stem]
    p = pins(env_dir)
    rows = []
    for name, url, role, extra in spec["pkgs"]:
        rows.append(
            f"| `{name}` | {ver_of(p, name)} | {role} | {extra} | [{name} 文档]({url}) |"
        )
    table = "\n".join(
        [
            "| 包 | 本环境版本 | 作用 | 额外依赖 | 官方文档 |",
            "| --- | --- | --- | --- | --- |",
            *rows,
        ]
    )
    return (
        f"## 本组能做什么\n\n"
        f"{spec['can']}\n\n"
        f"目标解释器：**CPython {py}**（Linux x86-64 glibc）。"
        f"本轮未在目标机安装或运行，不能写成开箱即用。\n\n"
        f"详细对照见 [`{GUIDE}/常用工具与包用途索引_cn.md`]({GUIDE}/常用工具与包用途索引_cn.md)；"
        f"安装步骤见 [`{GUIDE}/离线安装与使用_cn.md`]({GUIDE}/离线安装与使用_cn.md)；"
        f"最小示例见 [`{GUIDE}/常见任务快速入门_cn.md`]({GUIDE}/常见任务快速入门_cn.md)。\n\n"
        f"## 常用包说明\n\n"
        f"{table}\n\n"
        f"传递依赖只列在 `requirements_lock_en.txt` / `wheel_inventory_cn.csv`，不逐个写教程。\n\n"
    )


def patch_readme(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if "## 本组能做什么" in text:
        return False
    marker = "## 离线安装"
    if marker not in text:
        raise SystemExit(f"no install heading in {path}")
    path.write_text(text.replace(marker, block + marker, 1), encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for d in sorted(ENV.iterdir()):
        if not d.is_dir() or not (d / "README_cn.md").exists():
            continue
        name = d.name
        if name.endswith("_py310"):
            stem, py = name[: -len("_py310")], "3.10"
        elif name.endswith("_py312"):
            stem, py = name[: -len("_py312")], "3.12"
        else:
            continue
        if stem not in DOCS:
            continue
        if patch_readme(d / "README_cn.md", section(stem, d, py)):
            n += 1
            print("patched", name)
    print("patched_count", n)


if __name__ == "__main__":
    main()
