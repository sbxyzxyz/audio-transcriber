# formatter.py
# 合并依据：相邻 segment 之间停顿 < 该秒数 视为同一句话（合并）。
# 0.5s 是合理平衡：小于它是同句话被拆（并回），大于它是真句子边界（分开）。
MERGE_PAUSE = 0.5
# 超长保护：合并后单条超过该秒数则强制在词边界切（防止一条太长）
MAX_SEGMENT_SECONDS = 12.0


def format_ms(seconds: float) -> str:
    """把秒数格式化成 mm:ss.mmm，毫秒三位，分钟可超过 60（长视频）。"""
    ms = int(round(seconds * 1000))
    minutes, ms_remainder = divmod(ms, 60000)
    secs, millis = divmod(ms_remainder, 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def _join_text(a: str, b: str) -> str:
    """合并两段文本：中英文拼接处补空格，避免粘连。"""
    a, b = a.strip(), b.strip()
    if not a:
        return b
    if a[-1].isascii() and b[:1].isascii():
        return a + " " + b
    return a + b


def merge_by_pause(segments: list, pause: float = MERGE_PAUSE) -> list:
    """按停顿间隔合并：相邻段之间停顿很短 → 同一句话，合并。

    引擎 segment 是模型语义分句；这里用"段间停顿"判断哪些是同句话
    被拆的，把它们拼回完整句。停顿长的段间不合并（句子边界）。
    """
    if not segments:
        return []
    merged = []
    cur = segments[0]
    for nxt in segments[1:]:
        gap = nxt["start"] - cur["end"]
        if gap < pause:
            cur = {"start": cur["start"], "end": nxt["end"],
                   "text": _join_text(cur["text"], nxt["text"])}
        else:
            merged.append(cur)
            cur = nxt
    merged.append(cur)
    return merged


def format_transcript(data: dict, mode: str = "sentence") -> str:
    """把转写结果拼成带时间戳文字稿。

    data 结构：{"segments": [{start,end,text}], "words": [{start,end,word}]}
    两种模式：
      - "sentence"（默认）：按停顿合并，保持完整句
      - "raw"：不合并，引擎原始分段（最细）
    每行格式：[mm:ss.mmm - mm:ss.mmm] 文本
    """
    if mode == "sentence":
        segments = merge_by_pause(data["segments"], MERGE_PAUSE)
    else:
        segments = data["segments"]
    lines = []
    for seg in segments:
        start = format_ms(seg["start"])
        end = format_ms(seg["end"])
        lines.append(f"[{start} - {end}] {seg['text'].strip()}")
    return "\n".join(lines)
