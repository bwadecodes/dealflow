"""Deal state management.

Reads and writes {deal_dir}/.dealflow/deal-state.yaml. Tracks deal stage,
skills run, and key decisions. Lazily initialized by any skill on first call.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as _exc:
    raise ImportError(
        "PyYAML is required for state management. Install with: pip install pyyaml"
    ) from _exc


STAGES = ("prescreen", "diligence", "ic", "termsheet", "closed", "dead")
_STATE_VERSION = 1


def _state_path(deal_dir: Path) -> Path:
    return Path(deal_dir) / ".dealflow" / "deal-state.yaml"


def _ensure_dirs(deal_dir: Path) -> None:
    (Path(deal_dir) / ".dealflow" / "notes").mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def init_state(deal_dir: Path, deal_name: str | None = None) -> dict[str, Any]:
    """Create .dealflow/deal-state.yaml if missing. Returns the state dict."""
    _ensure_dirs(deal_dir)
    path = _state_path(deal_dir)
    if path.exists():
        return read_state(deal_dir)
    state: dict[str, Any] = {
        "version": _STATE_VERSION,
        "deal_name": deal_name or Path(deal_dir).name,
        "stage": "prescreen",
        "opened": _now_iso(),
        "last_updated": _now_iso(),
        "skills_run": [],
        "key_decisions": [],
        "workstreams": [],
    }
    _write(path, state)
    return state


def read_state(deal_dir: Path) -> dict[str, Any]:
    path = _state_path(deal_dir)
    if not path.exists():
        return init_state(deal_dir)
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _write(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = _now_iso()
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(state, fh, sort_keys=False, default_flow_style=False)


def update_state(deal_dir: Path, updates: dict[str, Any]) -> dict[str, Any]:
    state = read_state(deal_dir)
    state.update(updates)
    _write(_state_path(deal_dir), state)
    return state


def add_skill_run(deal_dir: Path, skill: str, report: str | None = None) -> None:
    state = read_state(deal_dir)
    entry = {"skill": skill, "timestamp": _now_iso()}
    if report:
        entry["report"] = report
    state.setdefault("skills_run", []).append(entry)
    _write(_state_path(deal_dir), state)


def get_stage(deal_dir: Path) -> str:
    return read_state(deal_dir).get("stage", "prescreen")


def set_stage(deal_dir: Path, stage: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage '{stage}'. Valid: {', '.join(STAGES)}")
    update_state(deal_dir, {"stage": stage})


def add_decision(deal_dir: Path, decision: str, date: str | None = None) -> None:
    state = read_state(deal_dir)
    state.setdefault("key_decisions", []).append(
        {"date": date or _dt.date.today().isoformat(), "decision": decision}
    )
    _write(_state_path(deal_dir), state)
