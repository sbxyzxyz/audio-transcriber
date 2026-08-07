# formatter.py
def format_ms(seconds: float) -> str:
    """把秒数格式化成 mm:ss.mmm，毫秒三位，分钟可超过 60（长视频）。"""
    ms = int(round(seconds * 1000))
    minutes, ms_remainder = divmod(ms, 60000)
    secs, millis = divmod(ms_remainder, 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def format_transcript(segments: list) -> str:
    """把带 start/end/text 的句子列表拼成带时间戳文字稿。

    每行格式：[mm:ss.mmm - mm:ss.mmm] 文本
    """
    lines = []
    for seg in segments:
        start = format_ms(seg["start"])
        end = format_ms(seg["end"])
        lines.append(f"[{start} - {end}] {seg['text'].strip()}")
    return "\n".join(lines)
