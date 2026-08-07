# test_formatter.py
from formatter import format_timestamp, format_transcript


def test_format_timestamp():
    assert format_timestamp(0) == "[00:00]"
    assert format_timestamp(5) == "[00:05]"
    assert format_timestamp(65) == "[01:05]"
    assert format_timestamp(3605) == "[60:05]"


def test_format_transcript():
    segments = [
        {"start": 0.0, "text": "大家好"},
        {"start": 5.2, "text": "欢迎来到我的频道"},
    ]
    assert format_transcript(segments) == (
        "[00:00] 大家好\n"
        "[00:05] 欢迎来到我的频道"
    )
