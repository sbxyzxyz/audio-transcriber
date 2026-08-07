# formatter.py
def format_timestamp(seconds: float) -> str:
    """把秒数格式化成 [mm:ss]，mm 可超过 60（长视频）。"""
    s = int(round(seconds))
    return f"[{s // 60:02d}:{s % 60:02d}]"


def format_transcript(segments: list) -> str:
    """把带 start 和 text 的句子列表拼成带时间戳文字稿。"""
    lines = [f"{format_timestamp(seg['start'])} {seg['text'].strip()}"
             for seg in segments]
    return "\n".join(lines)
