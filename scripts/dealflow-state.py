#!/usr/bin/env python3
"""CLI wrapper for dealflow_lib.state — used by skills.

Usage:
    dealflow-state.py init <deal_dir> [--name <deal_name>]
    dealflow-state.py read <deal_dir>
    dealflow-state.py add-skill-run <deal_dir> --skill <name> [--report <path>]
    dealflow-state.py set-stage <deal_dir> --stage <stage>
    dealflow-state.py add-decision <deal_dir> --decision <text> [--date <YYYY-MM-DD>]

All commands print JSON to stdout on success.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dealflow_lib import state  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("deal_dir")
    p_init.add_argument("--name", default=None)

    p_read = sub.add_parser("read")
    p_read.add_argument("deal_dir")

    p_add = sub.add_parser("add-skill-run")
    p_add.add_argument("deal_dir")
    p_add.add_argument("--skill", required=True)
    p_add.add_argument("--report", default=None)

    p_stage = sub.add_parser("set-stage")
    p_stage.add_argument("deal_dir")
    p_stage.add_argument("--stage", required=True)

    p_dec = sub.add_parser("add-decision")
    p_dec.add_argument("deal_dir")
    p_dec.add_argument("--decision", required=True)
    p_dec.add_argument("--date", default=None)

    args = p.parse_args()
    deal = Path(args.deal_dir)

    if args.cmd == "init":
        s = state.init_state(deal, deal_name=args.name)
    elif args.cmd == "read":
        s = state.read_state(deal)
    elif args.cmd == "add-skill-run":
        state.add_skill_run(deal, skill=args.skill, report=args.report)
        s = state.read_state(deal)
    elif args.cmd == "set-stage":
        state.set_stage(deal, args.stage)
        s = state.read_state(deal)
    elif args.cmd == "add-decision":
        state.add_decision(deal, args.decision, date=args.date)
        s = state.read_state(deal)
    else:
        return 1
    print(json.dumps(s, default=str, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
