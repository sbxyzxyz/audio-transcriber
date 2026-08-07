# transcriber.py
from faster_whisper import WhisperModel


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
        self.model_size = MODEL_SIZES.get(model_size, "medium")
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
        return [{"start": seg.start, "text": seg.text}
                for seg in segments_iter]
