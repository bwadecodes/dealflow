"""PDF author — Markdown → PDF with optional firm-style branding.

Tries pandoc first (lightest dep, best output). Falls back to weasyprint
if pandoc isn't available. Returns a clear error if neither is present.

Skills should always also save the Markdown source — the PDF complements
it, doesn't replace it.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import firmstyle


class PdfRendererNotAvailable(RuntimeError):
    """No supported PDF renderer (pandoc or weasyprint) is installed."""


def _have_pandoc() -> bool:
    return shutil.which("pandoc") is not None


def _have_weasyprint() -> bool:
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        return False
    return True


def _build_pandoc_css(brand: dict[str, Any], formatting: dict[str, Any]) -> str:
    """Minimal CSS reflecting the firm's brand. Pandoc HTML output respects
    --css; we generate inline to avoid file management."""
    margins = formatting.get("margins_in", {})
    return f"""
@page {{
  size: {formatting.get("page_size", "Letter")};
  margin: {margins.get("top", 1.0)}in {margins.get("right", 1.0)}in
          {margins.get("bottom", 1.0)}in {margins.get("left", 1.0)}in;
}}
body {{
  font-family: "{brand.get("font_family_body", "Inter")}", sans-serif;
  font-size: {brand.get("base_font_size_pt", 11)}pt;
  line-height: {brand.get("line_height", 1.4)};
  color: {brand.get("text_color", "#1c1c1c")};
  background: {brand.get("background_color", "#ffffff")};
}}
h1, h2, h3, h4, h5, h6 {{
  font-family: "{brand.get("font_family_headings", "Garamond")}", serif;
  font-weight: {brand.get("heading_weight", "semibold")};
  color: {brand.get("primary_color", "#1a3a5c")};
}}
a {{ color: {brand.get("link_color", "#1a3a5c")}; }}
code, pre {{ font-family: "{brand.get("font_family_monospace", "JetBrains Mono")}", monospace; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
th {{ background: {brand.get("primary_color", "#1a3a5c")}; color: #fff; }}
blockquote {{
  border-left: 4px solid {brand.get("primary_color", "#1a3a5c")};
  padding-left: 1em;
  font-style: italic;
  color: #555;
}}
""".strip()


def md_to_pdf(
    md_path: Path,
    pdf_path: Path,
    *,
    firm_style: dict[str, Any] | None = None,
    title: str | None = None,
) -> Path:
    """Render `md_path` to `pdf_path`. Returns the output path on success.
    Raises PdfRendererNotAvailable if no renderer is installed."""
    md_path = Path(md_path)
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    style = firm_style or firmstyle.load_profile()
    brand = firmstyle.get_brand(style)
    formatting = style.get("formatting") or {}

    if _have_pandoc():
        css = _build_pandoc_css(brand, formatting)
        css_path = pdf_path.with_suffix(".pdf.css")
        css_path.write_text(css, encoding="utf-8")
        cmd = [
            "pandoc",
            str(md_path),
            "-o",
            str(pdf_path),
            "--standalone",
            "--css",
            str(css_path),
        ]
        if title:
            cmd.extend(["--metadata", f"title={title}"])
        # Try HTML→PDF via wkhtmltopdf/weasyprint if available;
        # pandoc auto-detects. If pandoc lacks a PDF engine, fall through.
        result = subprocess.run(cmd, capture_output=True, text=True)
        css_path.unlink(missing_ok=True)
        if result.returncode == 0:
            return pdf_path
        # If pandoc failed for engine reasons, try weasyprint path below.

    if _have_weasyprint():
        try:
            import markdown as _md
            from weasyprint import HTML
        except ImportError as exc:
            raise PdfRendererNotAvailable(
                "weasyprint detected but markdown lib missing. Install: pip install markdown"
            ) from exc
        html_body = _md.markdown(
            md_path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"]
        )
        css = _build_pandoc_css(brand, formatting)
        full_html = (
            f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{title or md_path.stem}</title>"
            f"<style>{css}</style></head><body>{html_body}</body></html>"
        )
        HTML(string=full_html).write_pdf(str(pdf_path))
        return pdf_path

    raise PdfRendererNotAvailable(
        "No PDF renderer found. Install pandoc (preferred) or weasyprint:\n"
        "  - pandoc: https://pandoc.org/installing.html\n"
        "  - weasyprint: pip install weasyprint markdown"
    )


def renderer_available() -> str | None:
    """Returns name of available renderer ('pandoc' or 'weasyprint') or None."""
    if _have_pandoc():
        return "pandoc"
    if _have_weasyprint():
        return "weasyprint"
    return None
