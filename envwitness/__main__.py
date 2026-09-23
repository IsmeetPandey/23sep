from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import canonicalize, capture, compare, load


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envwitness", description="Capture and compare privacy-safe runtime receipts.")
    sub = parser.add_subparsers(dest="command", required=True)

    capture_parser = sub.add_parser("capture", help="capture a receipt from a project directory")
    capture_parser.add_argument("--root", type=Path, default=Path.cwd())
    capture_parser.add_argument("--output", type=Path, required=True)

    compare_parser = sub.add_parser("compare", help="compare two receipts")
    compare_parser.add_argument("left", type=Path)
    compare_parser.add_argument("right", type=Path)
    compare_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "capture":
            receipt = canonicalize(capture(args.root))
            args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"wrote {args.output}")
            return 0

        findings = compare(load(args.left), load(args.right))
        if args.as_json:
            print(json.dumps({"drift": findings}, indent=2, sort_keys=True))
        elif not findings:
            print("No meaningful environment drift found.")
        else:
            print(f"Found {len(findings)} difference(s):")
            for finding in findings:
                print(f"- [{finding['category']}] {finding['key']}: {finding['left']!r} != {finding['right']!r}")
        return 1 if findings else 0
    except (OSError, ValueError) as exc:
        print(f"envwitness: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
