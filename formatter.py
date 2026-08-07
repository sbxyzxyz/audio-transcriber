# formatter.py
# 一句话超过该秒数即使无停顿也强制切分（防止长句合并）
MAX_SENTENCE_SECONDS = 15.0
# 自适应阈值上下限（秒）。
# 下限 0.3：人说话句内词间间隔几乎都 <0.3s，小于它的不可能是句边界，
#           防止句内呼吸声/辅音间隙被误切（分太细）。
# 上限 3.0：防止 Otsu 在异常数据下算出极端值。
MIN_PAUSE = 0.3
MAX_PAUSE = 3.0


def format_ms(seconds: float) -> str:
    """把秒数格式化成 mm:ss.mmm，毫秒三位，分钟可超过 60（长视频）。"""
    ms = int(round(seconds * 1000))
    minutes, ms_remainder = divmod(ms, 60000)
    secs, millis = divmod(ms_remainder, 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def _otsu_threshold(values: list, nbins: int = 64) -> float:
    """大津法：自动找把间隔分成"句内"和"句边界"两类的最优阈值。

    根据每段音频实际的停停顿分布自适应，说话快慢都能适配。
    """
    n = len(values)
    if n == 0:
        return MIN_PAUSE
    hi = max(values) + 1e-6
    hist, edges = _histogram(values, nbins, hi)
    centers = [(edges[i] + edges[i + 1]) / 2 for i in range(nbins)]
    best_t, best_var = 0.0, -1.0
    for t in range(1, nbins):
        w0 = sum(hist[:t])
        w1 = sum(hist[t:])
        if w0 == 0 or w1 == 0:
            continue
        m0 = sum(c * h for c, h in zip(centers[:t], hist[:t])) / w0
        m1 = sum(c * h for c, h in zip(centers[t:], hist[t:])) / w1
        var_between = w0 * w1 * (m0 - m1) ** 2
        if var_between > best_var:
            best_var = var_between
            best_t = edges[t]
    # 限制在合理范围，避免极端值
    return max(MIN_PAUSE, min(MAX_PAUSE, best_t))


def _histogram(values: list, nbins: int, hi: float) -> tuple:
    hist = [0] * nbins
    edges = [hi * i / nbins for i in range(nbins + 1)]
    for v in values:
        idx = int(v / hi * nbins)
        idx = min(idx, nbins - 1)
        hist[idx] += 1
    return hist, edges


def segment_words(words: list) -> list[dict]:
    """把词流按停顿切分成句子（自适应阈值）。

    1. 用 Otsu 自动判断"哪些停顿算句子边界"，适配不同说话节奏
    2. 一句话超过 MAX_SENTENCE_SECONDS 仍未切分时，在最长停顿处强制切
    返回 [{start, end, text}]。
    """
    if not words:
        return []
    gaps = []
    for prev, cur in zip(words, words[1:]):
        gaps.append(cur["start"] - prev["end"])
    threshold = _otsu_threshold(gaps)

    sentences = []
    cur_words = [words[0]]
    for i, word in enumerate(words[1:], start=1):
        gap = gaps[i - 1]  # 词 i-1 与词 i 之间的间隔
        sentence_len = word["end"] - cur_words[0]["start"]
        # 间隔是句边界，或当前句已超长：词 i 归属新句
        if gap >= threshold or sentence_len >= MAX_SENTENCE_SECONDS:
            sentences.append(_make_sentence(cur_words))
            cur_words = [word]
        else:
            cur_words.append(word)
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
    merge=True 时用词流按停顿切句（自适应阈值，一句一个小停顿不拆开）；
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
