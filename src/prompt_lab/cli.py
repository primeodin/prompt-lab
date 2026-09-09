"""CLI entry — run built-in A/B eval, print table or JSON."""

from __future__ import annotations

import argparse
import json
import sys

from prompt_lab.eval import format_table, report_to_dict, run_ab
from prompt_lab.model import LiveModel, MockModel


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prompt-lab",
        description="Tiny A/B prompt eval harness (mock-first).",
    )
    p.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic MockModel (default; no API key).",
    )
    p.add_argument(
        "--live",
        action="store_true",
        help="Call an OpenAI-compatible chat API (needs OPENAI_API_KEY).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print machine-readable results",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.live and args.mock:
        print("pick one of --mock or --live, not both", file=sys.stderr)
        return 2

    mock = not args.live
    if args.mock:
        mock = True

    try:
        if mock:
            model = MockModel()
        else:
            model = LiveModel()
        report = run_ab(model=model, mock=mock)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(report_to_dict(report), indent=2))
        return 0

    print(format_table(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
