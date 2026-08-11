# test_transcriber.py
# 验证 Transcriber 的模型加载分支逻辑。
# 注意：不实际下载/加载模型，只验证"本地已有 vs 需要下载"的参数选择，
# 保证 CI 无需下载几 GB 模型也能跑。

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transcriber import LANGUAGES, MODEL_SIZES, Transcriber  # noqa: E402


def test_model_sizes_map_to_names():
    """模型档位应映射到模型名，而不是本地路径。"""
    assert MODEL_SIZES["极速"] == "small"
    assert MODEL_SIZES["标准"] == "medium"
    assert MODEL_SIZES["高精度"] == "large-v3"


def test_languages():
    assert LANGUAGES["中文"] == "zh"
    assert LANGUAGES["自动识别"] is None


def test_missing_model_dir_uses_download_root(tmp_path, monkeypatch):
    """本地无模型目录时，应传模型名 + download_root 让引擎自动下载。"""
    import transcriber

    # 把 MODELS_DIR 指到临时目录，保证里面没有模型
    monkeypatch.setattr(transcriber, "MODELS_DIR", str(tmp_path))

    fake_models = []

    class FakeWhisperModel:
        def __init__(self, arg, device=None, compute_type=None, **kwargs):
            fake_models.append({"arg": arg, "device": device, **kwargs})

    monkeypatch.setattr(transcriber, "WhisperModel", FakeWhisperModel)

    t = Transcriber("极速", "中文")
    # 应传模型名 small + download_root=临时目录
    assert fake_models, "应实例化模型"
    assert fake_models[0]["arg"] == "small"
    assert fake_models[0]["download_root"] == str(tmp_path)


def test_existing_model_dir_uses_local_path(tmp_path, monkeypatch):
    """本地已有模型目录时，应直接加载本地路径（不触发下载）。"""
    import transcriber

    # 建一个 models/small/model.bin 模拟已就绪模型
    local_dir = tmp_path / "small"
    local_dir.mkdir(parents=True)
    (local_dir / "model.bin").write_bytes(b"fake")
    monkeypatch.setattr(transcriber, "MODELS_DIR", str(tmp_path))

    fake_models = []

    class FakeWhisperModel:
        def __init__(self, arg, device=None, compute_type=None, **kwargs):
            fake_models.append({"arg": arg, "device": device, **kwargs})

    monkeypatch.setattr(transcriber, "WhisperModel", FakeWhisperModel)

    t = Transcriber("极速", "中文")
    assert fake_models, "应实例化模型"
    assert fake_models[0]["arg"] == str(local_dir)
    assert "download_root" not in fake_models[0]


def test_gpu_failure_falls_back_to_cpu(tmp_path, monkeypatch):
    """GPU 初始化失败时，应回退 CPU 并复用同一模型参数。"""
    import transcriber

    monkeypatch.setattr(transcriber, "MODELS_DIR", str(tmp_path))

    calls = []

    class FlakyWhisperModel:
        def __init__(self, arg, device=None, compute_type=None, **kwargs):
            calls.append(device)
            if device == "cuda":
                raise RuntimeError("CUDA unavailable")

    monkeypatch.setattr(transcriber, "WhisperModel", FlakyWhisperModel)

    t = Transcriber("极速", "中文")
    assert calls == ["cuda", "cpu"], "应尝试 GPU 后回退 CPU"
