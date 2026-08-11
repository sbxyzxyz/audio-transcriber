# transcriber.py
import os

from faster_whisper import WhisperModel


# 模型目录（相对本文件位置，随工具整体搬迁不失效）。
# 已手动放置的扁平模型（models/<名称>/model.bin）会被直接加载；
# 首次运行无模型时，会自动下载到此处，之后离线可用。
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

MODEL_SIZES = {
    "极速": "small",
    "标准": "medium",
    "高精度": "large-v3",
}

LANGUAGES = {
    "中文": "zh",
    "自动识别": None,
}


class Transcriber:
    def __init__(self, model_size: str, language: str | None):
        self.model_name = MODEL_SIZES.get(model_size, "medium")
        # 兼容传入显示名（如"中文"）或语言代码（如"zh"）
        self.language = LANGUAGES.get(language, language)
        # 模型加载参数：本地目录存在则直接加载本地（不复用、不重复下载）；
        # 否则传模型名让 faster-whisper 自动下载到 MODELS_DIR。
        local_dir = os.path.join(MODELS_DIR, self.model_name)
        if os.path.isdir(local_dir):
            self._model_arg, self._download_kwargs = local_dir, {}
        else:
            self._model_arg, self._download_kwargs = self.model_name, {"download_root": MODELS_DIR}
        # 优先 GPU，失败回退 CPU（此时模型已就绪，回退只是换设备）
        try:
            self.model = WhisperModel(
                self._model_arg, device="cuda", compute_type="float16",
                **self._download_kwargs,
            )
        except Exception:
            self.model = WhisperModel(
                self._model_arg, device="cpu", compute_type="int8",
                **self._download_kwargs,
            )

    def transcribe(self, audio_path: str) -> dict:
        segments_iter, _info = self.model.transcribe(
            audio_path, language=self.language, vad_filter=True,
            word_timestamps=True,
        )
        segments = []
        words = []
        for seg in segments_iter:
            segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
            for w in (seg.words or []):
                words.append({"start": w.start, "end": w.end, "word": w.word})
        return {"segments": segments, "words": words}
