#!/usr/bin/env python3
"""CLI wrapper for dealflow_lib.pdf — render Markdown to PDF.

Usage:
    dealflow-pdf.py <input.md> <output.pdf> [--title "..."] [--profile <path>]
    dealflow-pdf.py --check        # report available renderer
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dealflow_lib import firmstyle, pdf  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?")
    p.add_argument("output", nargs="?")
    p.add_argument("--title", default=None)
    p.add_argument(
        "--profile",
        default=None,
        help="Path to firm-style profile (default: ~/.claude/dealflow/firm-style.yaml)",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Just report which PDF renderer is available",
    )
    args = p.parse_args()

    if args.check:
        r = pdf.renderer_available()
        if r:
            print(f"OK — renderer: {r}")
            return 0
        print(
            "ERROR — no renderer found. Install pandoc or weasyprint.",
            file=sys.stderr,
        )
        return 2

    if not args.input or not args.output:
        p.error("input and output are required unless --check is used")

    profile = (
        firmstyle.load_profile(Path(args.profile)) if args.profile else firmstyle.load_profile()
    )
    try:
        out = pdf.md_to_pdf(
            Path(args.input), Path(args.output), firm_style=profile, title=args.title
        )
    except pdf.PdfRendererNotAvailable as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
