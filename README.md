# 视频转文字稿工具 (Audio Transcriber)

一个**本地免费**的视频/音频转文字稿工具：把视频或音频拖进窗口，点一下，就能生成带时间戳的文字稿。

所有识别都在你电脑本地完成，**音频不上传任何服务器**，私密安全，免费不限次数。

## 功能特性

- 🎬 **本地转写**：全程离线运行（首次需下载模型），音频不出本机
- ⏱ **毫秒格式时间戳**：每句带 `[开始 - 结束]` 时间，输出为毫秒格式
- 🧠 **智能分句**：以语音识别引擎的语义分句为基础，自动合并被拆断的句子，一句话一个时间戳
- 🎚 **三档识别精度**：极速 / 标准 / 高精度（默认高精度），适配不同质量需求
- 🚀 **GPU 加速**：支持 NVIDIA CUDA，优先用显卡跑，速度快
- 🗣 **中英双语**：中文 / 自动识别
- 📂 **支持多种格式**：mp4 / mov / mkv / avi / mp3 / wav / m4a / aac / flac / ogg
- 🖱 **拖拽即用**：把文件拖进窗口，选好选项，点开始

## 界面预览

```
┌─────────────────────────────────────────────┐
│         视频转文字稿工具                        │
│  ┌─────────────────────────────────────────┐ │
│  │   把视频/音频文件拖到这里                  │ │
│  │   或点击下方按钮选择文件                   │ │
│  └─────────────────────────────────────────┘ │
│  未选择文件                                    │
│  精度:[高精度▾] 语言:[中文▾] 分句:[按句子▾]     │
│              [ 开始转文字 ]                   │
│  ████████████████░░░░░░░░░░░░░░              │
│  就绪                                         │
└─────────────────────────────────────────────┘
```

转写完成后，在源文件同目录生成 `原文件名_文字稿.txt`：

```
[00:00.000 - 00:02.700] 大家好,欢迎来到我的频道
[00:03.980 - 00:11.300] 今天给大家讲讲工地上那些事我们首先看一下混凝土浇筑的注意事项
[00:12.520 - 00:16.580] 第一个问题,为什么混凝土要连续浇筑?
```

## 硬件要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11（64 位） |
| 内存 | 建议 8GB 以上 |
| 显卡 | 可选。有 NVIDIA 显卡（CUDA）则自动 GPU 加速；没有也能用 CPU 跑，只是慢一些 |
| 硬盘 | 模型约 3GB + 音频文件 |

## 安装步骤

### 方法一：有 Python 环境（推荐开发者）

需要 [Python 3.10+](https://www.python.org/downloads/) 和 [ffmpeg](https://ffmpeg.org/)。

```bash
git clone https://github.com/sbxyzxyz/audio-transcriber.git
cd audio-transcriber
python -m venv .venv

# Windows
.venv\Scripts\pip install -r requirements.txt

# macOS / Linux
.venv/bin/pip install -r requirements.txt

.venv\Scripts\python app.py   # Windows
.venv/bin/python app.py       # macOS / Linux
```

### 方法二：Windows 一键启动

Windows 用户可直接双击 `启动工具.bat`，首次运行会自动创建虚拟环境并安装依赖，之后每次双击即启动。

## 模型准备

首次运行时会自动下载 Whisper 识别模型（存到 `models/` 目录，之后离线可用）：

| 档位 | 模型 | 大小 | 特点 |
|------|------|------|------|
| 极速 | faster-whisper-small | ~460 MB | 快，适合语速内容，精度一般 |
| 标准 | faster-whisper-medium | ~1.5 GB | 均衡 |
| 高精度 | faster-whisper-large-v3 | ~2.9 GB | 最准，工程术语识别好，默认 |

国内网络下模型下载可能慢，可在命令行设置镜像：

```bash
# Windows PowerShell
$env:HF_ENDPOINT = "https://hf-mirror.com"
.venv\Scripts\python app.py
```

## 使用说明

1. 打开程序，把视频/音频文件拖进窗口（或点"选择文件"）
2. 选精度：极速 / 标准 / 高精度（默认高精度）
3. 选语言：中文 / 自动识别（默认中文）
4. 选分句：按句子（推荐，自动合并完整句）/ 按停顿（每处停顿单独一条，最细）
5. 点「开始转文字」，等进度条走完
6. 完成后弹出提示，在视频同目录找到 `*_文字稿.txt`

## 隐私说明

- ✅ **完全本地处理**：音频不上传、不联网（仅首次下载模型需联网）
- ✅ 转写后的文字稿只存在你自己的电脑上
- ✅ 无任何遥测、统计、广告

## 分句逻辑说明

语音识别引擎（faster-whisper）本身会按语义切分句子，但有时会把一句话拆成两段。工具用「停顿间隔」判断相邻两段是否为同一句话：

- 两段之间停顿 **< 0.5 秒** → 判定为同一句话被拆断，自动合并
- 停顿 ≥ 0.5 秒 → 判定为真实句子边界，保持分开

这个方案不依赖固定时长阈值，在多数场景下能减少句子被过度拆分，并尽量保证句子完整。

## 项目结构

```
app.py            # 图形界面（tkinter）
transcriber.py    # 转写核心（faster-whisper 封装）
formatter.py      # 时间戳格式化 + 智能分句
test_formatter.py # 单元测试
requirements.txt  # 依赖
启动工具.bat       # Windows 一键启动脚本
```

## 开发与测试

```bash
# 运行单元测试
.venv\Scripts\python -m pytest test_formatter.py -v
```

## 技术栈

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 语音识别引擎（CTranslate2 加速，支持 CUDA）
- [tkinter](https://docs.python.org/3/library/tkinter.html) — 图形界面（Python 标准库）
- [tkinterdnd2](https://github.com/ParthJadhav/TkinterDnD2) — 拖拽文件支持

## 许可证

[MIT](LICENSE) © 2026 sbxyzxyz
