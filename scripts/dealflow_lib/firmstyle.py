"""Firm-style profile loader.

The firm-style profile (~/.claude/dealflow/firm-style.yaml) is the package's
most influential config. It shapes voice, structure, visual identity, and
formatting across every output. Built by /dealflow-firmstyle; consumed by
every memo/document/Excel-producing skill.

This module only loads + validates. The /dealflow-firmstyle skill is
responsible for building the file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as _exc:
    raise ImportError(
        "PyYAML is required to load firm-style profiles. Install with: pip install pyyaml"
    ) from _exc


DEFAULT_PROFILE_PATH = Path.home() / ".claude" / "dealflow" / "firm-style.yaml"

# Sensible defaults used when no profile is configured. Skills should always
# fall back gracefully — generic output is better than no output.
_DEFAULTS: dict[str, Any] = {
    "version": 1,
    "firm_name": None,
    "voice": {
        "tone": "professional, direct, no jargon",
        "hedging": "moderate",
        "length_preference": "balanced",
        "perspective": "first_person_plural",
        "reading_level": "investor",
        "common_phrases": [],
        "avoid_phrases": [],
    },
    "templates": {},
    "brand": {
        "primary_color": "#1a3a5c",
        "secondary_color": "#c9a96e",
        "accent_color": "#7a8a99",
        "background_color": "#ffffff",
        "text_color": "#1c1c1c",
        "link_color": "#1a3a5c",
        "font_family_headings": "Garamond",
        "font_family_body": "Inter",
        "font_family_monospace": "JetBrains Mono",
        "heading_weight": "semibold",
        "base_font_size_pt": 11,
        "line_height": 1.4,
    },
    "formatting": {
        "page_size": "Letter",
        "margins_in": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        "header": {"enabled": False, "content": "", "show_on_first_page": False},
        "footer": {"enabled": True, "content": "Page {page} of {total}"},
        "cover_page": {"enabled": False, "elements": []},
        "confidentiality_marking": "",
        "table_style": "minimal-grid",
        "callout_style": "left-bar",
        "excel_formatting": {
            "header_fill": "#1a3a5c",
            "header_font_color": "#ffffff",
            "input_cell_color": "#fffacd",
            "formula_cell_color": "#ffffff",
            "output_cell_color": "#e6f0ff",
            "border_style": "thin",
            "number_format_currency": "$#,##0;($#,##0)",
            "number_format_percent": "0.0%",
            "decimal_places_default": 1,
        },
    },
    "term_preferences": {},
    "prescreen_config": {},
}


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Overlay wins; nested dicts merge, lists replace."""
    out = dict(base)
    for k, v in (overlay or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_profile(profile_path: Path | None = None) -> dict[str, Any]:
    """Load firm-style profile from disk, layered over sensible defaults.
    Returns the defaults if no profile is configured."""
    path = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH
    if not path.exists():
        return dict(_DEFAULTS)
    with path.open(encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh) or {}
    return _deep_merge(_DEFAULTS, loaded)


def is_configured(profile_path: Path | None = None) -> bool:
    """True if a firm-style profile file exists on disk."""
    path = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH
    return path.exists()


def get_template(profile: dict[str, Any], template_name: str) -> dict[str, Any] | None:
    return (profile.get("templates") or {}).get(template_name)


def get_voice(profile: dict[str, Any]) -> dict[str, Any]:
    return profile.get("voice") or _DEFAULTS["voice"]


def get_brand(profile: dict[str, Any]) -> dict[str, Any]:
    return profile.get("brand") or _DEFAULTS["brand"]


def get_excel_formatting(profile: dict[str, Any]) -> dict[str, Any]:
    return (profile.get("formatting") or {}).get(
        "excel_formatting"
    ) or _DEFAULTS["formatting"]["excel_formatting"]
