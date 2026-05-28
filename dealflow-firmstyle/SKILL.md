---
name: dealflow-firmstyle
description: Capture your firm's voice, templates, term preferences, and visual identity from sample materials so every other dealflow skill produces output that matches how your firm works. Run this after /dealflow-setup, once per firm or fund.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Firm Style Onboarding

Build a firm-style profile from the firm's existing IC memos, models, term sheets, and marketing materials. The profile is read by every memo-producing, document-producing, and Excel-producing skill in dealflow — it's what makes outputs feel like *your* firm's work instead of generic AI output.

## Invocation

```
/dealflow-firmstyle <path-to-folder-with-sample-materials>
/dealflow-firmstyle ~/firm-samples
```

If no path is given, ask the user to provide one.

## Prerequisites

### 1. Confirm Python dependencies

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
python3 -c "import pymupdf" 2>/dev/null || pip install pymupdf --quiet
python3 -c "import docx" 2>/dev/null || pip install python-docx --quiet
```

If Python is missing, tell the user to install from python.org and stop.

### 2. Ensure config exists

Check `~/.claude/dealflow/diligence-config.yaml`. If missing, tell the user: *"Run /dealflow-setup first — firmstyle builds on top of your base diligence config."*

### 3. Confirm the samples folder exists and has files

```
Glob <samples-path>/**/*
```

If empty: *"This folder appears to be empty. Point me at a folder containing sample IC memos, models, term sheets, and marketing materials."*

## Workflow

### Phase 1 — Inventory and classify samples

Scan the folder. Classify each file by type using filename heuristics + content inspection:

- **IC memos** — `.md`, `.docx`, `.pdf` with words like "memo", "ic", "investment", "recommendation"
- **Prescreen memos** — `.md`, `.docx`, `.pdf` with words like "prescreen", "screening", "snapshot", and shorter than full IC memos
- **Financial models** — `.xlsx` with multiple tabs and formulas
- **Term sheets** — `.docx`, `.pdf` with words like "term sheet", "summary of terms", "preferred stock"
- **Marketing materials** — `.pdf`, `.pptx` with words like "fund overview", "deck", "tearsheet"
- **Logos / brand assets** — image files

Present the inventory and ask the user to confirm or correct classifications.

### Phase 2 — Extract voice

Read 2+ IC memos. Use a subagent for this (it produces a lot of intermediate content). The subagent should report back:

- **Tone descriptors** — formal/casual, assertive/hedged, dense/breezy
- **Sentence length** — average and variance
- **Hedging frequency** — how often "we believe", "appears", "indicates" show up vs. assertive statements
- **Common opening phrases** by section ("Our diligence confirmed", "The team's track record suggests", etc.)
- **Words and phrases the firm uses** — at least 10 examples
- **Words and phrases the firm avoids** — try to infer (e.g., absence of "no-brainer", "slam dunk")
- **Perspective** — first person plural (we/our), third person, mixed
- **Reading level / audience** — IC partners, board, LPs, mixed

### Phase 3 — Extract structure

Read IC memo and prescreen samples. Identify:

- Section headings used in each memo type
- Which sections appear in every memo (required) vs. some (optional)
- Length norms per section
- Standard exhibits expected in every memo (football field, returns waterfall, sensitivity table, comparable transactions, etc.)
- Where the firm puts the recommendation (front, back, both)

For sample financial models, identify:
- Tab order
- Tab naming convention (PascalCase, snake_case, Title Case)
- Standard structure (3-statement, KPI dashboard, scenarios, etc.)

### Phase 4 — Extract visual identity and formatting

For PDF/DOCX samples:

- **Colors** — dominant palette from cover pages and section headers. Try `pymupdf` to extract page-level colors; otherwise ask the user.
- **Fonts** — extract from PDF metadata where possible; ask the user otherwise
- **Page layout** — page size (Letter/A4), margins, header/footer style, page numbering

For sample Excel models:

- Header fill colors
- Input vs. formula vs. output cell color conventions
- Number formats (currency, percent, decimals)
- Whether negatives are red, parens, etc.

If extraction is ambiguous or partial, ask the user. Never silently invent visual conventions.

### Phase 5 — Extract term preferences

Read sample term sheets. For each economic and governance term, capture the firm's standard position:

- Liquidation preference (1x non-participating? 1x participating capped? 2x?)
- Anti-dilution (broad-based weighted average? full ratchet?)
- Board composition
- Pro-rata rights (yes/no)
- Protective provisions (standard NVCA set? expanded?)
- Drag-along / tag-along thresholds
- ROFR / co-sale
- Vesting defaults
- Option pool target
- Any non-standard terms the firm consistently includes

If multiple term sheets show variation, capture the modal/typical position and flag deals where the firm took a different stance.

### Phase 6 — Generate template descriptions

For each template (IC memo, prescreen, term sheet, model layout), generate a plain-English description of how it should "feel" — the kind of note a partner would write to an analyst. Example:

> "Cover page with deal name, logo, confidentiality marking. Executive summary on page 2, single-page. Body sections use serif headings on sans-serif body. Pull quotes from management calls set in italic with a left bar in navy. Every numerical claim references a model tab or data room file in a footnote."

These descriptions guide skills when the exact template can't cover every case.

### Phase 7 — Present for confirmation

Present every extracted dimension to the user using AskUserQuestion. Walk through:

1. Voice — show the extracted tone, sample phrases, things to use, things to avoid
2. Structure — show memo sections, exhibits expected
3. Visual — show extracted colors, fonts, layout choices
4. Term preferences — show each term and the inferred default
5. Template descriptions — show the plain-English notes

For each section, give the user options to accept, edit, or skip. Never save without confirmation.

### Phase 8 — Save profile

Write the profile to `~/.claude/dealflow/firm-style.yaml`. Follow the schema below.

Also copy/save extracted template files to `~/.claude/dealflow/templates/`:
- `ic-memo.md` — memo skeleton with section headings + plain-English descriptions of what each section should contain
- `prescreen.md` — prescreen skeleton
- `termsheet.md` — term sheet skeleton with the firm's standard terms
- `model-layout.md` — text description of the expected model tab order

### Phase 9 — Confirm and explain

After save, tell the user:

> "Firm-style profile saved to ~/.claude/dealflow/firm-style.yaml. Templates saved to ~/.claude/dealflow/templates/. The following skills now produce output tailored to your firm's style: /dealflow-prescreen, /dealflow-vp-review, /dealflow-pre-ic, /dealflow-termsheet, /dealflow-superanalyst, /dealflow-process, /dealflow-deskresearch. Re-run /dealflow-firmstyle anytime your firm's conventions change."

## Profile Schema

The full schema is documented in `design-spec-v2.md`. Required top-level keys:

```yaml
version: 1
firm_name: "..."
voice:
  tone, hedging, length_preference, perspective, reading_level,
  common_phrases[], avoid_phrases[], hedging_words{use[], avoid[]}
templates:
  ic_memo, prescreen, termsheet, model_layout
brand:
  logo, primary_color, secondary_color, accent_color, ...,
  font_family_headings, font_family_body, font_family_monospace, ...
formatting:
  page_size, margins_in, header, footer, cover_page,
  confidentiality_marking, table_style, callout_style,
  chart_style, excel_formatting
template_descriptions:
  ic_memo, prescreen, termsheet
term_preferences:
  liquidation_preference, anti_dilution, board_composition,
  pro_rata_rights, protective_provisions, drag_along, rofr,
  vesting_default, option_pool_target
prescreen_config:
  sections[], length_target, model_complexity, required_exhibits[]
reference_materials:
  ic_memos[], models[], termsheets[], marketing[]
```

Use `yaml.safe_dump` with `sort_keys=False` to preserve a logical order.

## Privacy

All sample materials are read locally and analyzed via the Anthropic API call. They are not stored anywhere except your firm-style profile file. Sample file paths are stored as references (`reference_materials`) but not their contents. Recommend the user add `~/.claude/dealflow/` to backup but not version control.

## Error handling

| Scenario | Response |
|---|---|
| Folder missing or empty | "Point me at a folder containing sample IC memos, models, term sheets, and marketing materials." |
| Only one IC memo | "I'd suggest 2+ memos for reliable voice extraction. Want me to proceed with one, or add more samples first?" |
| Password-protected file | "Skipping [file] — password-protected. Remove the password and re-run if you want it included." |
| No term sheets | "No term sheets found. Skipping term preferences — you can fill these in later by editing ~/.claude/dealflow/firm-style.yaml directly." |
| Logo file not found | "No logo detected. Skipping logo placement — you can add `brand.logo` to the profile later." |

## Interactive mode

After save, stay in interactive mode for refinement:
- "Add an extra avoid phrase: 'massive opportunity'"
- "Change the primary color to #1f4d7a"
- "Show me what the IC memo template will look like"
