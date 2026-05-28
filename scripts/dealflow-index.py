#!/usr/bin/env python3
"""CLI wrapper for dealflow_lib.index — used by skills.

Usage:
    dealflow-index.py init <deal_dir>
    dealflow-index.py add <deal_dir> --path <rel_path> --category <cat>
                          --type <ext> --indexed-by <skill>
                          [--summary <text>] [--tags tag1,tag2]
    dealflow-index.py add-fact <deal_dir> --path <rel> --fact <text>
                          --source-ref <ref> --added-by <skill>
    dealflow-index.py add-tags <deal_dir> --path <rel> --tags tag1,tag2
    dealflow-index.py query <deal_dir> [--category X] [--tags a,b]
                          [--substring text] [--limit N]
    dealflow-index.py get <deal_dir> --path <rel>
    dealflow-index.py is-stale <deal_dir> --path <rel>

Outputs JSON to stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dealflow_lib import index  # noqa: E402


def _split_tags(s: str | None) -> list[str]:
    return [t.strip() for t in s.split(",") if t.strip()] if s else []


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("deal_dir")

    p_add = sub.add_parser("add")
    p_add.add_argument("deal_dir")
    p_add.add_argument("--path", required=True, help="path relative to deal_dir")
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--type", dest="type_", required=True)
    p_add.add_argument("--indexed-by", required=True)
    p_add.add_argument("--summary", default="")
    p_add.add_argument("--tags", default="")

    p_fact = sub.add_parser("add-fact")
    p_fact.add_argument("deal_dir")
    p_fact.add_argument("--path", required=True)
    p_fact.add_argument("--fact", required=True)
    p_fact.add_argument("--source-ref", required=True)
    p_fact.add_argument("--added-by", required=True)

    p_tags = sub.add_parser("add-tags")
    p_tags.add_argument("deal_dir")
    p_tags.add_argument("--path", required=True)
    p_tags.add_argument("--tags", required=True)

    p_query = sub.add_parser("query")
    p_query.add_argument("deal_dir")
    p_query.add_argument("--category", default=None)
    p_query.add_argument("--tags", default=None)
    p_query.add_argument("--substring", default=None)
    p_query.add_argument("--limit", type=int, default=None)

    p_get = sub.add_parser("get")
    p_get.add_argument("deal_dir")
    p_get.add_argument("--path", required=True)

    p_stale = sub.add_parser("is-stale")
    p_stale.add_argument("deal_dir")
    p_stale.add_argument("--path", required=True)

    args = p.parse_args()
    deal = Path(args.deal_dir)

    if args.cmd == "init":
        index.init_index(deal)
        out = {"ok": True, "path": str(deal / ".dealflow" / "index.jsonl")}
    elif args.cmd == "add":
        file_path = deal / args.path
        size = file_path.stat().st_size if file_path.exists() else 0
        hash_ = index.hash_file(file_path) if file_path.exists() else ""
        out = index.add_or_update_record(
            deal,
            path=args.path,
            category=args.category,
            type_=args.type_,
            size_bytes=size,
            hash_=hash_,
            indexed_by=args.indexed_by,
            summary=args.summary,
            tags=_split_tags(args.tags),
        )
    elif args.cmd == "add-fact":
        index.add_fact(
            deal,
            path=args.path,
            fact=args.fact,
            source_ref=args.source_ref,
            added_by=args.added_by,
        )
        out = index.get_record(deal, args.path)
    elif args.cmd == "add-tags":
        index.add_tags(deal, path=args.path, tags=_split_tags(args.tags))
        out = index.get_record(deal, args.path)
    elif args.cmd == "query":
        out = index.query(
            deal,
            category=args.category,
            tags=_split_tags(args.tags) or None,
            substring=args.substring,
            limit=args.limit,
        )
    elif args.cmd == "get":
        out = index.get_record(deal, args.path) or {}
    elif args.cmd == "is-stale":
        out = {"path": args.path, "stale": index.is_stale(deal, args.path)}
    else:
        return 1

    print(json.dumps(out, default=str, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
