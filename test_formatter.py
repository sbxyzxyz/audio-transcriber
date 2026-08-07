# test_formatter.py
from formatter import format_ms, format_transcript, merge_by_pause, _join_text


def test_format_ms():
    assert format_ms(0) == "00:00.000"
    assert format_ms(0.125) == "00:00.125"
    assert format_ms(5.5) == "00:05.500"
    assert format_ms(65.025) == "01:05.025"
    assert format_ms(3605.999) == "60:05.999"


def test_join_text_chinese_no_space():
    assert _join_text("大家好", "今天好") == "大家好今天好"


def test_join_text_english_space():
    assert _join_text("Hello", "world") == "Hello world"


def test_merge_by_pause_joins_short_gap():
    """段间停顿短（同句话被拆）应合并。"""
    segments = [
        {"start": 0.0, "end": 3.0, "text": "今天给大家讲讲"},
        {"start": 3.0, "end": 6.0, "text": "工地上那些事"},
    ]
    merged = merge_by_pause(segments, pause=0.5)
    assert len(merged) == 1
    assert merged[0]["text"] == "今天给大家讲讲工地上那些事"
    assert merged[0]["start"] == 0.0
    assert merged[0]["end"] == 6.0


def test_merge_by_pause_keeps_long_gap():
    """段间停顿长（句子边界）不应合并。"""
    segments = [
        {"start": 0.0, "end": 3.0, "text": "大家好。"},
        {"start": 4.0, "end": 6.0, "text": "今天好。"},
    ]
    merged = merge_by_pause(segments, pause=0.5)
    assert len(merged) == 2


def test_merge_by_pause_empty():
    assert merge_by_pause([]) == []


def test_merge_by_pause_single():
    segs = [{"start": 0.0, "end": 2.0, "text": "大家好"}]
    assert merge_by_pause(segs) == segs


def test_format_transcript():
    data = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "大家"},
            {"start": 1.0, "end": 2.0, "text": "好"},
            {"start": 3.0, "end": 4.0, "text": "欢迎"},
        ],
        "words": [],
    }
    assert format_transcript(data) == (
        "[00:00.000 - 00:02.000] 大家好\n"
        "[00:03.000 - 00:04.000] 欢迎"
    )


def test_format_transcript_raw():
    """mode='raw' 应保留引擎原始分段，不合并。"""
    data = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "大家好"},
            {"start": 1.0, "end": 2.0, "text": "今天好"},
        ],
        "words": [],
    }
    # 段间停顿 0s，默认会合并成一条
    assert len(format_transcript(data, mode="raw").split("\n")) == 2
