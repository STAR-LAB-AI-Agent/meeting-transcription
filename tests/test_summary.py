from src import summarize


def test_summary_structure(transcript):
    result = summarize.summarize(transcript)
    for key in ("topic", "summary", "key_points", "decisions", "action_items"):
        assert key in result
    assert result["method"] == "extractive_fallback"


def test_summary_extracts_decisions(transcript):
    result = summarize.summarize(transcript)
    assert any("决定" in d for d in result["decisions"])


def test_summary_extracts_actions(transcript):
    result = summarize.summarize(transcript)
    assert any("待办" in a for a in result["action_items"])


def test_summary_empty_transcript():
    result = summarize.summarize({"segments": []})
    assert set(
        ("topic", "summary", "key_points", "decisions", "action_items")
    ).issubset(result)
    assert result["key_points"] == []
    assert result["decisions"] == []
    assert result["action_items"] == []
