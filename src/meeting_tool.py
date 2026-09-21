"""Unified script/CLI for the AI Meeting ASR Agent.

Every subcommand runs independently of the Agent layer and returns JSON.
Successful operations exit with code 0; failures exit non-zero with a clear
error message.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if __package__:
    from . import agent_router, logger, search, security, summarize, transcribe
else:
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
    from src import agent_router, logger, search, security, summarize, transcribe


def _load_transcript(path: str) -> tuple[dict, Path]:
    p = security.validate_path(path, write=False, must_exist=True)
    data = json.loads(p.read_text(encoding="utf-8"))
    return data, p


def _print_json(obj: dict | list) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_transcribe(args: argparse.Namespace) -> int:
    payload = transcribe.transcribe(args.audio, args.output, overwrite=args.overwrite)
    _print_json(payload)
    if args.markdown:
        md = transcribe.transcript_to_markdown(payload)
        print(md)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    data, _ = _load_transcript(args.transcript)
    segments = data.get("segments", [])
    hits = search.search_keyword(
        segments, args.keyword, context=args.context, max_results=args.max_results
    )
    result = {"keyword": args.keyword, "hit_count": len(hits), "hits": hits}
    if args.stats:
        full = "\n".join(s.get("text", "") for s in segments)
        compact = search.compress_hits(hits)
        result["token_optimization"] = search.compression_stats(full, compact)
    _print_json(result)
    return 0


def cmd_locate(args: argparse.Namespace) -> int:
    data, _ = _load_transcript(args.transcript)
    segments = data.get("segments", [])
    result = search.locate_time(segments, args.time, context=args.context)
    _print_json(result)
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    data, _ = _load_transcript(args.transcript)
    result = summarize.summarize(data, use_llm=args.llm)
    _print_json(result)
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    _print_json(agent_router.route(args.query))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meeting_tool", description="AI Meeting ASR Agent CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("transcribe", help="音频转写")
    p.add_argument("--audio", required=True, help="输入音频路径")
    p.add_argument("--output", default=None, help="输出 JSON 路径")
    p.add_argument("--overwrite", action="store_true", help="覆盖已有输出")
    p.add_argument("--markdown", action="store_true", help="同时打印 Markdown")
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("search", help="关键词检索")
    p.add_argument("--transcript", required=True, help="转写 JSON 路径")
    p.add_argument("--keyword", required=True, help="检索关键词")
    p.add_argument("--context", type=int, default=1, help="前后上下文句数")
    p.add_argument("--max-results", type=int, default=None)
    p.add_argument("--stats", action="store_true", help="输出 Token 压缩统计")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("locate", help="时间定位")
    p.add_argument("--transcript", required=True, help="转写 JSON 路径")
    p.add_argument("--time", required=True, help="时间点，如 01:30")
    p.add_argument("--context", type=int, default=1, help="前后上下文句数")
    p.set_defaults(func=cmd_locate)

    p = sub.add_parser("summarize", help="会议摘要")
    p.add_argument("--transcript", required=True, help="转写 JSON 路径")
    p.add_argument("--llm", action="store_true", help="使用外部 LLM（需配置环境变量）")
    p.set_defaults(func=cmd_summarize)

    p = sub.add_parser("route", help="自然语言意图识别")
    p.add_argument("query", help="自然语言指令")
    p.set_defaults(func=cmd_route)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    start = time.time()
    input_file = getattr(args, "audio", None) or getattr(args, "transcript", None)
    try:
        code = args.func(args)
    except (
        security.SecurityError,
        FileNotFoundError,
        FileExistsError,
        ValueError,
        RuntimeError,
    ) as exc:
        logger.log(
            args.command,
            input_file,
            status="error",
            error_type=type(exc).__name__,
        )
        _print_json(
            {"ok": False, "error": str(exc), "error_type": type(exc).__name__}
        )
        return 1
    logger.log(
        args.command,
        input_file,
        status="ok",
        duration_ms=int((time.time() - start) * 1000),
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
