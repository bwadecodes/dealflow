"""Deal index management.

Persistent index of materials at {deal_dir}/.dealflow/index.jsonl.
One JSON record per file or logical section. Skills query before
re-reading source files; skills append facts and tags as they
discover information.

Schema (per v2 design spec):
    path, hash, category, type, size_bytes, last_indexed, indexed_by,
    summary, key_facts[], sections[], cross_refs{}, tags[]
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def _index_path(deal_dir: Path) -> Path:
    return Path(deal_dir) / ".dealflow" / "index.jsonl"


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def hash_file(file_path: Path) -> str:
    """SHA-256 of the file's content. Used to detect post-index changes."""
    h = hashlib.sha256()
    with Path(file_path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def init_index(deal_dir: Path) -> Path:
    """Create .dealflow/index.jsonl if missing. Returns the index path."""
    path = _index_path(deal_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
    return path


def _read_all(deal_dir: Path) -> list[dict[str, Any]]:
    path = _index_path(deal_dir)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _write_all(deal_dir: Path, records: Iterable[dict[str, Any]]) -> None:
    path = _index_path(deal_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def _new_record(
    *,
    path: str,
    category: str,
    type_: str,
    size_bytes: int,
    hash_: str,
    indexed_by: str,
    summary: str = "",
    key_facts: list[dict[str, str]] | None = None,
    sections: list[dict[str, str]] | None = None,
    cross_refs: dict[str, list[str]] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "path": path,
        "hash": hash_,
        "category": category,
        "type": type_,
        "size_bytes": size_bytes,
        "last_indexed": _now_iso(),
        "indexed_by": indexed_by,
        "summary": summary,
        "key_facts": key_facts or [],
        "sections": sections or [],
        "cross_refs": cross_refs or {"mentions": [], "referenced_by": []},
        "tags": tags or [],
    }


def add_or_update_record(
    deal_dir: Path,
    *,
    path: str,
    category: str,
    type_: str,
    size_bytes: int,
    hash_: str,
    indexed_by: str,
    summary: str = "",
    sections: list[dict[str, str]] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Add a new record, or update the metadata of an existing one.

    Existing key_facts and cross_refs are preserved (additive operations
    only via add_fact/add_tag/add_cross_ref).
    """
    init_index(deal_dir)
    records = _read_all(deal_dir)
    existing_idx = next((i for i, r in enumerate(records) if r["path"] == path), None)
    if existing_idx is not None:
        rec = records[existing_idx]
        rec["hash"] = hash_
        rec["category"] = category
        rec["type"] = type_
        rec["size_bytes"] = size_bytes
        rec["last_indexed"] = _now_iso()
        rec["indexed_by"] = indexed_by
        if summary:
            rec["summary"] = summary
        if sections:
            rec["sections"] = sections
        if tags:
            existing = set(rec.get("tags", []))
            rec["tags"] = sorted(existing | set(tags))
        records[existing_idx] = rec
        _write_all(deal_dir, records)
        return rec
    rec = _new_record(
        path=path,
        category=category,
        type_=type_,
        size_bytes=size_bytes,
        hash_=hash_,
        indexed_by=indexed_by,
        summary=summary,
        sections=sections,
        tags=tags,
    )
    records.append(rec)
    _write_all(deal_dir, records)
    return rec


def get_record(deal_dir: Path, path: str) -> dict[str, Any] | None:
    for r in _read_all(deal_dir):
        if r["path"] == path:
            return r
    return None


def add_fact(
    deal_dir: Path,
    *,
    path: str,
    fact: str,
    source_ref: str,
    added_by: str,
) -> None:
    """Append a key fact to the record for `path`. No-op if record missing."""
    records = _read_all(deal_dir)
    for i, r in enumerate(records):
        if r["path"] == path:
            r.setdefault("key_facts", []).append(
                {"fact": fact, "source_ref": source_ref, "added_by": added_by}
            )
            records[i] = r
            _write_all(deal_dir, records)
            return


def add_tags(deal_dir: Path, *, path: str, tags: list[str]) -> None:
    records = _read_all(deal_dir)
    for i, r in enumerate(records):
        if r["path"] == path:
            existing = set(r.get("tags", []))
            r["tags"] = sorted(existing | set(tags))
            records[i] = r
            _write_all(deal_dir, records)
            return


def add_cross_ref(
    deal_dir: Path, *, path: str, direction: str, other_path: str
) -> None:
    """direction ∈ {'mentions', 'referenced_by'}."""
    if direction not in ("mentions", "referenced_by"):
        raise ValueError("direction must be 'mentions' or 'referenced_by'")
    records = _read_all(deal_dir)
    for i, r in enumerate(records):
        if r["path"] == path:
            refs = r.setdefault("cross_refs", {"mentions": [], "referenced_by": []})
            if other_path not in refs.setdefault(direction, []):
                refs[direction].append(other_path)
            records[i] = r
            _write_all(deal_dir, records)
            return


def query(
    deal_dir: Path,
    *,
    category: str | None = None,
    tags: list[str] | None = None,
    substring: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Filter records. `tags` matches any (OR). `substring` matches summary
    or any key_fact text, case-insensitive."""
    results: list[dict[str, Any]] = []
    sub_lc = substring.lower() if substring else None
    tag_set = set(tags) if tags else None
    for r in _read_all(deal_dir):
        if category and r.get("category") != category:
            continue
        if tag_set and not (tag_set & set(r.get("tags", []))):
            continue
        if sub_lc:
            haystack = (r.get("summary", "") or "").lower()
            facts = " ".join(f.get("fact", "") for f in r.get("key_facts", []))
            haystack += " " + facts.lower()
            if sub_lc not in haystack:
                continue
        results.append(r)
        if limit and len(results) >= limit:
            break
    return results


def is_stale(deal_dir: Path, path: str, file_path: Path | None = None) -> bool:
    """True if the indexed hash differs from the current file hash, or if
    the file is missing from the index."""
    rec = get_record(deal_dir, path)
    if rec is None:
        return True
    fp = Path(file_path) if file_path else Path(deal_dir) / path
    if not fp.exists():
        return True
    return rec.get("hash") != hash_file(fp)


def all_records(deal_dir: Path) -> list[dict[str, Any]]:
    return _read_all(deal_dir)
