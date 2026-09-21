"""Natural-language entry point for the AI Meeting ASR Agent.

Usage:
    python cli/meeting_cli.py "搜索预算"
    python cli/meeting_cli.py "01:30 附近说了什么"
    python cli/meeting_cli.py "生成这次会议摘要"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import agent_router, logger, search, security, summarize, transcribe

DEFAULT_TRANSCRIPT = PROJECT_ROOT / "examples" / "demo_transcript.json"
DEFAULT_AUDIO = PROJECT_ROOT / "data" / "input" / "demo.wav"


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _load_transcript(path: str) -> dict:
    p = security.validate_path(path, write=False, must_exist=True)
    return json.loads(p.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="自然语言会议助手")
    parser.add_argument("query", help="自然语言指令")
    parser.add_argument(
        "--transcript", default=str(DEFAULT_TRANSCRIPT), help="转写 JSON 路径"
    )
    parser.add_argument("--audio", default=str(DEFAULT_AUDIO), help="音频路径")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    route = agent_router.route(args.query)
    intent = route["intent"]
    try:
        if intent == "transcribe":
            result = transcribe.transcribe(args.audio, overwrite=args.overwrite)
            _print_json(result)
            return 0

        if intent == "search":
            data = _load_transcript(args.transcript)
            hits = search.search_keyword(
                data.get("segments", []), route["keyword"], context=1
            )
            _print_json(
                {"intent": intent, "keyword": route["keyword"],
                 "hit_count": len(hits), "hits": hits}
            )
            return 0

        if intent == "locate":
            data = _load_transcript(args.transcript)
            rng = agent_router.extract_range_minutes(args.query)
            if rng:
                result = search.locate_range(
                    data.get("segments", []), rng[0], rng[1]
                )
            else:
                time_str = agent_router.extract_time(args.query)
                if not time_str:
                    raise ValueError("未能从指令中解析出时间。")
                result = search.locate_time(
                    data.get("segments", []), time_str, context=1
                )
            result["intent"] = intent
            _print_json(result)
            return 0

        if intent == "summarize":
            data = _load_transcript(args.transcript)
            result = summarize.summarize(data)
            result["intent"] = intent
            _print_json(result)
            return 0

        _print_json(
            {
                "intent": "unknown",
                "error": "无法识别的指令，支持：转写 / 搜索 / 时间定位 / 摘要。",
                "query": args.query,
            }
        )
        return 1
    except (
        security.SecurityError,
        FileNotFoundError,
        FileExistsError,
        ValueError,
        RuntimeError,
    ) as exc:
        logger.log(intent, status="error", error_type=type(exc).__name__)
        _print_json(
            {"intent": intent, "ok": False, "error": str(exc),
             "error_type": type(exc).__name__}
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
