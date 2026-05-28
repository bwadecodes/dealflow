---
name: dealflow-prescreen
description: Produce a prescreen memo and simple model from minimal inputs — a pitch deck, CIM, or just a description. The natural front door to a new deal. Outputs Markdown + PDF memo and an Excel model.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - WebSearch
  - WebFetch
  - Agent
  - AskUserQuestion
---

# Prescreen

Generate a prescreen memo + simple model in the first 48 hours of looking at a deal. The output is what you'd want to send to a partner asking "is this worth a closer look?" — not a full IC memo.

## Invocation

```
/dealflow-prescreen <path-to-pitch-deck-or-folder>
/dealflow-prescreen "<verbal-description>" --no-files
/dealflow-prescreen <path> "<additional context>"
```

If no files exist, the user can provide a description and any links.

## Prerequisites

### 1. Confirm Python deps

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
python3 -c "import pymupdf" 2>/dev/null || pip install pymupdf --quiet
```

### 2. Config check

Check `~/.claude/dealflow/diligence-config.yaml`. If missing, tell the user: *"Run /dealflow-setup first — prescreen needs your buy box to assess fit."*

### 3. Firm-style check (optional but recommended)

```bash
python3 -c "from dealflow_lib import firmstyle; print(firmstyle.is_configured())" 2>/dev/null
```

If `False`, tell the user: *"No firm-style profile found. I'll produce a generic prescreen. Run /dealflow-firmstyle for output tailored to your firm's voice and templates."* Then continue.

### 4. Resolve deal name and folder

Derive the deal name from the input file/folder or ask the user.

Determine a deal folder. If the input is a folder, use that. If it's a file, use the parent. If it's a description-only invocation, ask: "Where should I save outputs? (default: ./<deal-name>/)"

Init state and index:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" init "<deal-folder>" --name "<deal-name>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" init "<deal-folder>"
```

## Phase 1 — Read inputs

Read whatever was provided:

- **Pitch deck (.pdf, .pptx)** — extract text via pymupdf; use Read tool on the PDF for visual content (charts, layouts)
- **CIM (.pdf, .docx)** — text + visual
- **Folder** — Glob for relevant files; read in priority order (deck → CIM → financials → other)
- **Description only** — work from what the user provided

Extract company snapshot:
- Name, sector, geography, stage, business model
- Current financials if available (revenue, growth, margins, burn)
- Round size, valuation ask, use of funds (if mentioned)
- Team (founders, key execs)

## Phase 2 — Quick desk research

Auto-invoke a 10-source desk research pass for market context. Don't dialog — just run a quick scan.

Spawn a subagent with task: "Pull 10 sources on <company> and <industry>. Focus on market size, top 3–5 direct competitors, and any recent funding news. Return a 1-page synthesis."

Skip this phase if the user invokes with `--no-research` flag.

## Phase 3 — Buy-box fit assessment

Read the user's config (`~/.claude/dealflow/diligence-config.yaml`). Map the company snapshot against the buy box:

- Revenue range fit
- Stage fit
- Ownership target feasibility
- Sector fit
- Any other buy_box criteria in the config

For each, mark green / yellow / red with a one-line rationale.

## Phase 4 — Thesis and anti-thesis

Generate **3 bullets each** for thesis and anti-thesis:

**Thesis** — strongest reasons this deal could work
**Anti-thesis** — strongest reasons this deal could fail or be the wrong fit

Each bullet should be specific to the company and what you learned, not generic.

## Phase 5 — Simple model

Build a 3–5 year simple P&L + returns model in Excel. Use the foundational ExcelAuthor utility.

```bash
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import excel, firmstyle

profile = firmstyle.load_profile()
author = excel.ExcelAuthor(firm_style=profile)
wb = author.new_workbook(title="Prescreen Model — <deal-name>")

# Assumptions tab — inputs the user can change
author.add_source_tab(wb, "Assumptions", rows=[
    ["Driver", "Y1", "Y2", "Y3", "Y4", "Y5"],
    ["Revenue growth %", 0.50, 0.40, 0.30, 0.25, 0.20],
    ["Gross margin %", 0.65, 0.68, 0.70, 0.72, 0.72],
    ["OpEx as % of revenue", 0.80, 0.70, 0.60, 0.55, 0.50],
    ["Starting revenue (\$M)", 10, "", "", "", ""],
])

# P&L tab — formulas referencing Assumptions
author.add_calc_tab(wb, "P&L", header=["Line item", "Y1", "Y2", "Y3", "Y4", "Y5"], rows=[
    ["Revenue", "=Assumptions!B5", "=B2*(1+Assumptions!C2)", "=C2*(1+Assumptions!D2)", "=D2*(1+Assumptions!E2)", "=E2*(1+Assumptions!F2)"],
    ["Gross profit", "=B2*Assumptions!B3", "=C2*Assumptions!C3", "=D2*Assumptions!D3", "=E2*Assumptions!E3", "=F2*Assumptions!F3"],
    ["OpEx", "=B2*Assumptions!B4", "=C2*Assumptions!C4", "=D2*Assumptions!D4", "=E2*Assumptions!E4", "=F2*Assumptions!F4"],
    ["EBITDA", "=B3-B4", "=C3-C4", "=D3-D4", "=E3-E4", "=F3-F4"],
], output_columns=[2,3,4,5,6])

# Returns tab — simple entry/exit IRR
author.add_calc_tab(wb, "Returns", header=["Item", "Value"], rows=[
    ["Entry valuation (\$M)", 50],
    ["Ownership %", 0.20],
    ["Exit multiple (x revenue)", 5],
    ["Exit revenue", "='P&L'!F2"],
    ["Exit valuation", "=B3*B4"],
    ["Exit value to investor", "=B5*B2"],
    ["Hold (years)", 5],
    ["MOIC", "=B6/(B1*B2)"],
    ["IRR", "=B8^(1/B7)-1"],
], input_columns=[2], output_columns=[2])

author.add_method_tab(wb, """
This is a simple prescreen model — drivers held as assumptions, P&L
derived by formula, returns calculated against entry valuation and
exit multiple.

Replace yellow input cells with deal-specific assumptions.
For a full IC-ready model, build separately or commission from the company.
""")

author.add_summary_tab(wb, "Summary", title="Prescreen Model — <deal-name>", bullets=[
    "Drivers on Assumptions tab — change to test sensitivities",
    "P&L derives from Assumptions",
    "Returns are simple — entry/exit, no debt, no fees",
    "Not a substitute for a full operating model",
])

author.save(wb, Path("<deal-folder>/reports/prescreen-model-<DATE>.xlsx"))
print("Model saved")
PY
```

Customize the numbers based on what you learned in Phase 1 (e.g., starting revenue from the deck, growth from comps in Phase 2). Use real numbers if you have them, sensible placeholders if not, but mark placeholders clearly.

## Phase 6 — Write the prescreen memo

Load the firmstyle prescreen template if available; otherwise use a default structure.

**Default sections** (override with `firm-style.yaml` → `prescreen_config.sections`):

1. **Snapshot** — company name, sector, stage, what they do, key metrics in a small table
2. **Buy-box fit** — green/yellow/red checklist
3. **Thesis** — 3 bullets
4. **Anti-thesis** — 3 bullets
5. **Initial valuation read** — rough sense from comps; reference the simple model's returns
6. **Recommendation** — one of: PASS / PURSUE / PURSUE WITH CONDITIONS / NEED MORE INFO. One paragraph rationale.
7. **Open questions for first management call** — 5–10 questions

Apply firmstyle voice: tone, hedging, common phrases, perspective (per `voice` in profile).

Save to `<deal-folder>/reports/prescreen-YYYY-MM-DD.md`.

## Phase 7 — Render PDF

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-pdf.py" \
  "<deal-folder>/reports/prescreen-<DATE>.md" \
  "<deal-folder>/reports/prescreen-<DATE>.pdf" \
  --title "Prescreen — <deal-name>"
```

If PDF renderer is missing, tell the user how to install and continue with Markdown only.

## Phase 8 — Update state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-prescreen --report "reports/prescreen-<DATE>.md"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/prescreen-<DATE>.md" --category memo --type md \
  --indexed-by dealflow-prescreen \
  --summary "Prescreen for <deal-name> — recommendation: <REC>" \
  --tags "prescreen,memo,<REC>"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/prescreen-model-<DATE>.xlsx" --category model --type xlsx \
  --indexed-by dealflow-prescreen \
  --summary "Simple prescreen model — 5yr P&L + returns" \
  --tags "prescreen,model"
```

Set deal stage:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" set-stage "<deal-folder>" --stage prescreen
```

## Phase 9 — Hand off

Tell the user:

> "Prescreen complete. Recommendation: <REC>.
>
> - Memo: `reports/prescreen-YYYY-MM-DD.md` (.pdf)
> - Model: `reports/prescreen-model-YYYY-MM-DD.xlsx`
>
> If you decide to pursue, run /dealflow-process next to lay out the full diligence plan, or /dealflow-dataroom once you have a data room."

Stay in interactive mode for refinement: "rewrite thesis to be more aggressive", "stress test the returns at 3x exit multiple", "draft an email to the founder asking the open questions", etc.

## Error handling

| Scenario | Response |
|---|---|
| No config | "Run /dealflow-setup first." |
| No input files and no description | "Give me a pitch deck, a CIM, a folder, or a description — I need something to start with." |
| Deck only has images, no text | "Reading the deck visually using Read on each page (slower but works)." |
| Folder has many files | "Lots of files. Prescreen reads the deck first, then CIM, then financials — running on top 5 files. Run /dealflow-dataroom for a full pass." |
| PDF renderer missing | "Markdown memo saved. Install pandoc or weasyprint for PDF output." |
