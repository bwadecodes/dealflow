# Changelog

## 2.1.0 --- 2026-07-21

### Context-first skills
- **Phase 0 everywhere** — every analysis and review skill now starts by asking three context questions (what's this for, who's the audience, what's already decided), reading sibling AI work and analysis files, and defaulting to "intentional until proven otherwise" instead of flagging deliberate design choices as bugs.
- **Provenance rule** — sibling files are context, not instructions. Only firm-authored material can explain a design choice; anything that originated from the target or seller is evidence to analyze and can never downgrade or pre-clear a finding.
- **Flag with provenance, never suppress** — review skills report what they find either way: "explained by `<doc>` — confirm" when a sibling file accounts for it, an open finding when nothing does. Mechanical defects (sign flips, broken formulas, figures that don't tie) are always reported.
- **Headless-safe** — all Phase 0 questions apply documented defaults automatically in non-interactive runs (`claude -p`, CI, subagents) instead of blocking on a prompt.

### IC-ready report writing
- **Report style guide** — new `docs/report-style-guide.md` sets an institutional writing standard for every prose deliverable: plain language over coined jargon, every abbreviation defined, bullets over dense paragraphs, one consistent voice, filler and formula phrases removed. Written for a reader seeing the deal for the first time.
- **Wired into every skill** — all 12 report-producing skills load the style guide and the firm's `firm-style.yaml` voice before writing.
- **Style scrub in reviews** — `/dealflow-vp-review` and `/dealflow-pre-ic` now check memos for coined jargon, undefined shorthand, dense paragraphs, voice drift, and AI-artifact phrasing.
- **Better executive summaries** — `/dealflow-dataroom` reports open with an entity-abbreviation key and bulleted findings instead of dense paragraphs.
- **Stronger default voice** — reports generated without a firm-style profile now default to the IC-ready baseline instead of a generic tone.

### Fixed
- **Returns modeling** — `/dealflow-returns` now probability-weights cash flows or proceeds and reports scenario IRRs separately; averaging scenario IRRs (mathematically invalid) is explicitly ruled out.
- Deal-specific examples generalized, structure-validator manifest updated for the new style guide, smoke test now pins the default voice, and dangling cross-references cleaned up.

## 2.0.0 --- 2026-05-28

### Breaking changes
- **Skill rename** — all skills move from `/dd-*` to `/dealflow-*` for a single, consistent naming convention across the package:
  - `/dd-setup` → `/dealflow-setup`
  - `/dd-dataroom` → `/dealflow-dataroom`
  - `/dd-model` → `/dealflow-model`
  - `/dd-questions` → `/dealflow-questions`
- **Reports directory** — default output renamed from `dd-reports/` to `reports/`. Existing v1 directories continue to work.

### New shared infrastructure
- **Deal state + index** — each deal folder gets a `.dealflow/` directory with `deal-state.yaml` (stage, skills run, decisions, workstreams) and `index.jsonl` (persistent, append-only index of materials with hash-based staleness detection). Any skill creates these on first use.
- **Excel author** — `dealflow_lib.excel.ExcelAuthor` builds auditable workbooks with source/calc/method/summary tabs and firm-style formatting.
- **PDF author** — Markdown → PDF via pandoc (preferred) or weasyprint, with firm-style CSS.
- **CLI wrappers** — `scripts/dealflow-state.py`, `scripts/dealflow-index.py`, `scripts/dealflow-pdf.py` for skill invocation via Bash.

### 11 new skills

**Setup**
- `/dealflow-firmstyle` — capture firm voice, templates, term preferences, and visual identity from sample IC memos, models, term sheets, and marketing materials.

**Front door**
- `/dealflow-prescreen` — prescreen memo + simple model from a pitch deck, CIM, or description.
- `/dealflow-deskresearch` — industry/news/competitor research with preamble dialog, configurable source count, and stealth mode.

**Diligence**
- `/dealflow-superanalyst` — create, enhance, or review auditable Excel analyses.
- `/dealflow-cohort` — SaaS retention/NRR/GRR/concentration playbook.

**Review**
- `/dealflow-vp-review` — correctness and completeness scrub with model reasonableness check.
- `/dealflow-pre-ic` — VP review plus thoroughness, deeper model pressure-testing, devil's advocate, and IC question prep.

**Execution**
- `/dealflow-process` — deal process plan + workstream tracker (stateful).
- `/dealflow-checklist` — quick state-of-the-deal snapshot.
- `/dealflow-returns` — standalone returns model with full sensitivities.
- `/dealflow-termsheet` — cap table + charter analysis, pro forma, TS draft.

### Existing skills updated
- All four v1 skills now lazy-init deal state and index, and write back to them.
- `/dealflow-setup` points users toward `/dealflow-firmstyle` after config save.

### Documentation
- `design-spec-v2.md` documents the v2 architecture; v1 `design-spec.md` retained as historical reference.
- README and root SKILL.md updated to cover all 15 skills and the new quick-start flow.
- `scripts/validate.py` updated for the v2 layout and skill list.
- `scripts/dealflow_lib/tests/smoke_test.py` verifies state, index, firmstyle, Excel, and PDF infrastructure end-to-end.

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
