from src import agent_router


def test_route_transcribe():
    r = agent_router.route("帮我转写这个会议录音")
    assert r["intent"] == "transcribe"


def test_route_search():
    r = agent_router.route("搜索预算")
    assert r["intent"] == "search"
    assert r["keyword"] == "预算"


def test_route_search_extract_keyword():
    r = agent_router.route("会议里哪里提到了深度学习")
    assert r["intent"] == "search"
    assert r["keyword"] == "深度学习"


def test_route_locate():
    r = agent_router.route("01:30 附近说了什么")
    assert r["intent"] == "locate"


def test_route_summarize():
    r = agent_router.route("生成这次会议摘要")
    assert r["intent"] == "summarize"


def test_route_unknown():
    r = agent_router.route("今天天气怎么样")
    assert r["intent"] == "unknown"
