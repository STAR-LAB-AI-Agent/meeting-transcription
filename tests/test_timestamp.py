import pytest

from src import search


def test_parse_mmss():
    assert search.parse_time_to_ms("01:30") == 90_000


def test_parse_hhmmss():
    assert search.parse_time_to_ms("01:02:03") == 3_723_000


def test_parse_seconds():
    assert search.parse_time_to_ms("90") == 90_000


def test_parse_invalid():
    with pytest.raises(ValueError):
        search.parse_time_to_ms("abc")


def test_locate_point(segments):
    result = search.locate_time(segments, "01:30")
    assert result["target_ms"] == 90_000
    assert not result["out_of_range"]
    assert len(result["segments"]) >= 1


def test_locate_out_of_range(segments):
    result = search.locate_time(segments, "02:00:00")
    assert result["out_of_range"] is True


def test_locate_range(segments):
    result = search.locate_range(segments, "05:00", "06:00")
    assert len(result["segments"]) >= 1
    for seg in result["segments"]:
        assert seg["start_ms"] <= 360_000
        assert seg["end_ms"] >= 300_000
