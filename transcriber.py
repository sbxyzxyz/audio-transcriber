# transcriber.py
import os

from faster_whisper import WhisperModel


# 本地模型目录（相对本文件位置，随工具整体搬迁不失效）
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

MODEL_SIZES = {
    "极速": os.path.join(MODELS_DIR, "small"),
    "标准": os.path.join(MODELS_DIR, "medium"),
    "高精度": os.path.join(MODELS_DIR, "large-v3"),
}

LANGUAGES = {
    "中文": "zh",
    "自动识别": None,
}


class Transcriber:
    def __init__(self, model_size: str, language: str | None):
        self.model_size = MODEL_SIZES.get(model_size, MODEL_SIZES["标准"])
        # 兼容传入显示名（如"中文"）或语言代码（如"zh"）
        self.language = LANGUAGES.get(language, language)
        # 优先 GPU，失败回退 CPU
        try:
            self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
        except Exception:
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str) -> list[dict]:
        segments_iter, _info = self.model.transcribe(
            audio_path, language=self.language, vad_filter=True
        )
        return [{"start": seg.start, "end": seg.end, "text": seg.text}
                for seg in segments_iter]
