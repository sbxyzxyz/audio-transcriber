# test_formatter.py
from formatter import format_ms, format_transcript, segment_words


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


def test_format_transcript_no_merge_uses_segments():
    """merge=False 时应使用引擎原始分段。"""
    data = {
        "segments": [{"start": 0.0, "end": 1.0, "text": "大家好"}],
        "words": [{"start": 0.0, "end": 1.0, "word": "大家好"}],
    }
    assert format_transcript(data, merge=False) == "[00:00.000 - 00:01.000] 大家好"


def test_segment_words_joins_short_gap():
    """间隔小于阈值（小停顿）应同属一句。"""
    words = [
        {"start": 0.0, "end": 1.0, "word": "今天"},
        {"start": 1.1, "end": 2.0, "word": "给大家"},
        {"start": 2.1, "end": 3.0, "word": "讲讲"},
    ]
    segs = segment_words(words, pause_seconds=0.5)
    assert len(segs) == 1
    assert segs[0]["start"] == 0.0
    assert segs[0]["end"] == 3.0
    assert segs[0]["text"] == "今天给大家讲讲"


def test_segment_words_splits_long_gap():
    """间隔超过阈值（明显停顿）应切开成两句。"""
    words = [
        {"start": 0.0, "end": 1.0, "word": "大家好"},
        {"start": 3.0, "end": 4.0, "word": "今天"},
    ]
    segs = segment_words(words, pause_seconds=0.5)
    assert len(segs) == 2
    assert segs[0]["text"] == "大家好"
    assert segs[1]["text"] == "今天"


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
