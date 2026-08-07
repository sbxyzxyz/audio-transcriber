# formatter.py
# 两词间隔超过该秒数视为句子边界（明显停顿）
PAUSE_SECONDS = 0.5


def format_ms(seconds: float) -> str:
    """把秒数格式化成 mm:ss.mmm，毫秒三位，分钟可超过 60（长视频）。"""
    ms = int(round(seconds * 1000))
    minutes, ms_remainder = divmod(ms, 60000)
    secs, millis = divmod(ms_remainder, 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def segment_words(words: list, pause_seconds: float = PAUSE_SECONDS) -> list[dict]:
    """把词流按停顿切分成句子。

    词与词之间间隔 >= pause_seconds 视为明显停顿，切开成新句；
    否则同属一句。返回 [{start, end, text}]。
    """
    if not words:
        return []
    sentences = []
    cur_words = [words[0]]
    for prev, cur in zip(words, words[1:]):
        gap = cur["start"] - prev["end"]
        if gap >= pause_seconds:
            # 明显停顿，当前句结束
            sentences.append(_make_sentence(cur_words))
            cur_words = [cur]
        else:
            cur_words.append(cur)
    if cur_words:
        sentences.append(_make_sentence(cur_words))
    return sentences


def _make_sentence(word_list: list) -> dict:
    text = ""
    for w in word_list:
        word = w["word"]
        # 中英文拼接处补空格：前后都是 ascii 字符时加空格，避免粘连
        if text and text[-1].isascii() and word and word[0].isascii():
            text += " "
        text += word
    return {"start": word_list[0]["start"], "end": word_list[-1]["end"], "text": text.strip()}


def format_transcript(data: dict, merge: bool = True) -> str:
    """把转写结果（含 segments/words）拼成带时间戳文字稿。

    data 结构：{"segments": [{start,end,text}], "words": [{start,end,word}]}
    merge=True 时用词流按停顿切句（一句一个小停顿不拆开）；
    merge=False 时用引擎原始分段（每处停顿都单独一条）。
    每行格式：[mm:ss.mmm - mm:ss.mmm] 文本
    """
    if merge:
        segments = segment_words(data["words"])
    else:
        segments = data["segments"]
    lines = []
    for seg in segments:
        start = format_ms(seg["start"])
        end = format_ms(seg["end"])
        lines.append(f"[{start} - {end}] {seg['text'].strip()}")
    return "\n".join(lines)
