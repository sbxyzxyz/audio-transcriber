# test_formatter.py
from formatter import format_ms, format_transcript


def test_format_ms():
    assert format_ms(0) == "00:00.000"
    assert format_ms(0.125) == "00:00.125"
    assert format_ms(5.5) == "00:05.500"
    assert format_ms(65.025) == "01:05.025"
    assert format_ms(3605.999) == "60:05.999"


def test_format_transcript():
    segments = [
        {"start": 0.125, "end": 3.500, "text": "大家好"},
        {"start": 5.2, "end": 8.75, "text": "欢迎来到我的频道"},
    ]
    assert format_transcript(segments) == (
        "[00:00.125 - 00:03.500] 大家好\n"
        "[00:05.200 - 00:08.750] 欢迎来到我的频道"
    )
