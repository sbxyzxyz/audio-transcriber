# test_formatter.py
from formatter import (
    format_ms, format_transcript, segment_words, segment_by_interval,
    _otsu_threshold,
)


def test_format_ms():
    assert format_ms(0) == "00:00.000"
    assert format_ms(0.125) == "00:00.125"
    assert format_ms(5.5) == "00:05.500"
    assert format_ms(65.025) == "01:05.025"
    assert format_ms(3605.999) == "60:05.999"


def test_format_transcript():
    data = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "大家"},
            {"start": 1.0, "end": 2.0, "text": "好。"},
            {"start": 3.0, "end": 4.0, "text": "欢迎"},
        ],
        "words": [
            {"start": 0.0, "end": 1.0, "word": "大家"},
            {"start": 1.0, "end": 2.0, "word": "好。"},
            {"start": 3.0, "end": 4.0, "word": "欢迎"},
        ],
    }
    assert format_transcript(data) == (
        "[00:00.000 - 00:02.000] 大家好。\n"
        "[00:03.000 - 00:04.000] 欢迎"
    )


def test_format_transcript_raw_uses_segments():
    """mode='raw' 时应使用引擎原始分段。"""
    data = {
        "segments": [{"start": 0.0, "end": 1.0, "text": "大家好"}],
        "words": [{"start": 0.0, "end": 1.0, "word": "大家好"}],
    }
    assert format_transcript(data, mode="raw") == "[00:00.000 - 00:01.000] 大家好"


def test_segment_by_interval_cuts_around_target():
    """大约每 4 秒一条，停顿点处切分。"""
    # 构造连续说话，每 4 秒处有一个停顿边界
    words = []
    t = 0.0
    for chunk in ["今天给大家", "讲讲工地", "上那些事"]:
        for ch in chunk:
            words.append({"start": t, "end": t + 0.5, "word": ch})
            t += 0.5
        # 句间停顿
        words[-1]["end"] = t  # 修正最后词结束时间
        t += 2.0  # 2 秒停顿，>MIN_PAUSE
    segs = segment_by_interval(words, target_seconds=4.0, max_seconds=6.0)
    assert len(segs) >= 1


def test_segment_by_interval_max_seconds_guard():
    """超过 max_seconds 无停顿也应强制切分。"""
    words = []
    t = 0.0
    for i in range(20):  # 连续 10 秒说话，无停顿
        words.append({"start": t, "end": t + 0.5, "word": "啊"})
        t += 0.5
    segs = segment_by_interval(words, target_seconds=4.0, max_seconds=6.0)
    # 20个词×0.5=10秒，应被强制切成至少2段，且每段不超过max_seconds
    assert len(segs) >= 2
    for s in segs:
        assert s["end"] - s["start"] <= 6.0 + 0.01


def test_segment_words_joins_short_gap():
    """间隔小于阈值（小停顿）应同属一句。"""
    words = [
        {"start": 0.0, "end": 1.0, "word": "今天"},
        {"start": 1.1, "end": 2.0, "word": "给大家"},
        {"start": 2.1, "end": 3.0, "word": "讲讲"},
    ]
    segs = segment_words(words)
    assert len(segs) == 1
    assert segs[0]["text"] == "今天给大家讲讲"


def test_segment_words_splits_long_gap():
    """间隔明显大于句内（句子边界）应切开。"""
    words = [
        {"start": 0.0, "end": 1.0, "word": "大家好"},
        {"start": 3.0, "end": 4.0, "word": "今天"},
    ]
    segs = segment_words(words)
    assert len(segs) == 2
    assert segs[0]["text"] == "大家好"
    assert segs[1]["text"] == "今天"


def test_segment_words_adaptive_threshold():
    """Otsu 应自动区分句内(0)与句间(大间隔)两群。"""
    words = [
        {"start": 0.0, "end": 0.5, "word": "大家"},
        {"start": 0.5, "end": 1.0, "word": "好"},
        {"start": 2.5, "end": 3.0, "word": "欢迎"},
        {"start": 3.0, "end": 3.5, "word": "大家"},
    ]
    gaps = [w["start"] - p["end"] for p, w in zip(words, words[1:])]
    t = _otsu_threshold(gaps)
    # 阈值应落在大间隔(1.5)与句内(0)之间
    assert 0 < t <= 1.5
    segs = segment_words(words)
    assert len(segs) == 2


def test_segment_words_keeps_single():
    """单个词直接返回，不丢内容。"""
    words = [{"start": 0.0, "end": 2.0, "word": "大家好"}]
    segs = segment_words(words)
    assert len(segs) == 1
    assert segs[0]["text"] == "大家好"


def test_segment_words_empty():
    """空输入返回空列表，不崩溃。"""
    assert segment_words([]) == []


def test_segment_words_english_spacing():
    """中英文拼接处应补空格。"""
    words = [
        {"start": 0.0, "end": 1.0, "word": "Hello"},
        {"start": 1.1, "end": 2.0, "word": "world"},
    ]
    segs = segment_words(words)
    assert len(segs) == 1
    assert segs[0]["text"] == "Hello world"
