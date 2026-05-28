"""Dealflow shared library.

Modules:
- state: read/write {deal}/.dealflow/deal-state.yaml
- index: read/write/query {deal}/.dealflow/index.jsonl
- firmstyle: load ~/.claude/dealflow/firm-style.yaml
- excel: build auditable Excel workbooks with firm-style formatting
- pdf: render Markdown to PDF with firm-style branding

Skills invoke these either as Python imports (with scripts/ on PYTHONPATH)
or via the thin CLI wrappers in scripts/ (e.g., scripts/dealflow-index.py).
"""

__version__ = "2.0.0"
