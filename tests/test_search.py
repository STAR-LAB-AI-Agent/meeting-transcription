from src import search


def test_search_normal(segments):
    hits = search.search_keyword(segments, "预算")
    assert len(hits) > 0
    assert all("预算" in h["sentence"] for h in hits)
    assert all("start_ms" in h and "end_ms" in h for h in hits)


def test_search_multiple_hits(segments):
    hits = search.search_keyword(segments, "预算")
    assert len(hits) >= 3


def test_search_not_found(segments):
    hits = search.search_keyword(segments, "不存在的词xyz")
    assert hits == []


def test_search_chinese_keyword(segments):
    hits = search.search_keyword(segments, "深度学习")
    assert len(hits) >= 3
    assert all("深度学习" in h["sentence"] for h in hits)


def test_search_english_keyword(segments):
    hits = search.search_keyword(segments, "ASR")
    assert len(hits) >= 1
    assert "语音识别" in hits[0]["sentence"]


def test_search_empty_transcript():
    assert search.search_keyword([], "预算") == []


def test_token_optimization(segments):
    full = "\n".join(s.get("text", "") for s in segments)
    hits = search.search_keyword(segments, "预算")
    compact = search.compress_hits(hits)
    stats = search.compression_stats(full, compact)
    assert stats["estimated_token_before"] > stats["estimated_token_after"]
    assert 0 < stats["reduction_percent"] < 100
    assert "compression_ratio" in stats
