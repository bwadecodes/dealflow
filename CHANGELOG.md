# Changelog

## 2.0.0 --- 2026-05-28

### Breaking changes
- **Skill rename** — all skills move from `/dd-*` to `/dealflow-*` for a single, consistent naming convention across the package:
  - `/dd-setup` → `/dealflow-setup`
  - `/dd-dataroom` → `/dealflow-dataroom`
  - `/dd-model` → `/dealflow-model`
  - `/dd-questions` → `/dealflow-questions`
- **Reports directory** — default output renamed from `dd-reports/` to `reports/`. Existing v1 directories continue to work.

### Foundation for v2 expansion
- Adds `design-spec-v2.md` capturing the expanded v2 architecture: deal state + persistent index (`.dealflow/`), shared Excel/PDF authors, expansive firm-style profile, and 11 new skills (firmstyle, prescreen, deskresearch, superanalyst, cohort, vp-review, pre-ic, process, checklist, returns, termsheet).
- v1 `design-spec.md` retained as historical reference.

## 1.1.0 --- 2026-03-14

### Report improvements
- **Standardized headers** — all reports now start with `Company Name — Report Type — DateTime`
- **Configurable output directory** — reports respect `preferences.output_dir` from config (relative or absolute path)
- **HTML export** — new `report_format` preference (`"markdown"`, `"html"`, or `"both"`) with professional styled HTML template suitable for printing and sharing with senior stakeholders
- **Documents Flagged for Follow-Up** — `/dd-dataroom` now flags specific documents during review (Review, Incomplete, Verify, Question) with a dedicated report section
- **Deal identification** — all skills now explicitly resolve company/deal name before generating reports
- **HTML template** — added `config/report-template.html` with print-ready styling

### Config updates
- All default templates now default to `report_format: "both"`
- Updated `/dd-setup` preferences step to expose new format and output directory options

## 1.0.0 --- 2026-03-13

Initial release.

### Skills
- `/dd-setup` --- Configuration wizard with five starting templates (VC, Growth Equity, PE LMM, PE MM, PE Large Buyout)
- `/dd-dataroom` --- Data room assessment against your diligence rubric
- `/dd-model` --- Financial model review with driver mapping and assumption analysis
- `/dd-questions` --- Prioritized diligence question generation

### Config Templates
- Venture Capital
- Growth Equity
- PE Lower-Middle Market
- PE Middle Market
- PE Large Buyout

### Documentation
- CLI Quickstart for non-technical users
- IT & Compliance Guide with data flow explanation and approval template
- Rubric Customization Guide
