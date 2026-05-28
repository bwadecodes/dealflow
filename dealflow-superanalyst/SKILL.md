---
name: dealflow-superanalyst
description: Three modes — create (look at raw data, propose interesting analyses, execute as auditable Excel), enhance (extend existing analysis), and review (audit existing analysis for correctness and completeness). Output is always an auditable Excel workbook plus a markdown summary.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Agent
  - AskUserQuestion
---

# Super Analyst

The analyst you'd hire if you could — looks at data, proposes the analyses worth running, executes them as a clean, auditable Excel workbook. Also enhances existing analyses with what's missing, and reviews existing analyses for correctness.

## Invocation

```
/dealflow-superanalyst <data-or-analysis-path>          # auto-detect mode
/dealflow-superanalyst <data-path> --create
/dealflow-superanalyst <analysis-path> --enhance
/dealflow-superanalyst <analysis-path> --review
/dealflow-superanalyst <path> --deal-folder <deal-folder>
```

Auto-detect logic:
- If input is raw data (CSV, single-tab Excel with mostly numbers, no calculations) → create mode
- If input is a multi-tab Excel with formulas → ask: enhance or review?
- If input is a folder → ask the user what to point at

## Prerequisites

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
```

If a deal folder is provided, init state and index:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" init "<deal-folder>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" init "<deal-folder>"
```

## Phase 0 — Context (do this FIRST, before mode work)

Super-analyst output without context produces analyses that miss the user's actual question and treats deliberate design choices in existing analyses as bugs. Before any mode work, do TWO things:

### 0a. Ask the user three quick context questions

Use a single `AskUserQuestion`:

1. **What's this analysis for?** — Live deal diligence, case study / interview, internal practice, second-opinion on someone else's analysis.
2. **Who's the audience and what does success look like?** — Lead deal team, partner pre-read, IC, external case-study reviewer. Each wants different surfacing.
3. **What's already been deliberately decided so the analysis doesn't waste time questioning it?** — In create mode: thesis lens, scope cuts, what kind of analyses are NOT useful. In enhance/review mode: design choices in the existing analysis that the user owns (segmentation choices, time period definitions, cohort cut-offs, formula structures).

Keep answers brief and weave into mode work. If skipped, default to "live deal, internal audience, nothing pre-decided" and note in the summary.

### 0b. Read sibling AI work and analysis BEFORE starting

If a deal folder is provided, look for and read these BEFORE running:
- `AI Work/*.md` — prior AI-generated artifacts (analytical framings, prior super-analyst runs, design docs). These often contain the WHY behind the analytical approach.
- `Analysis/*.md` and `Analysis/*.docx` — the user's own framing notes
- Any `*Notes*`, `*Questions*`, or `Memo Feedback*` files at the project root
- `reports/` — any prior review reports

Cite these in the markdown summary when relevant — don't reinvent analyses the user has already worked through.

### 0c. Default assumption: intentional until proven otherwise

In enhance/review mode especially: when you see something unusual in the existing workbook (a non-standard segmentation, an off-cycle period definition, a hardcoded plug, a formula that looks fragile), the FIRST hypothesis is intentional design. Read the sibling docs, ask the user, THEN flag if still unexplained. Do not flag deliberate choices as bugs.

## Mode: CREATE

### Phase 1 — Profile the data

Open the source data. Report:
- Tables / sheets present
- Columns and inferred types
- Row count, time range if there's a date column
- Missing/null cell counts
- Min/max/distribution for numerical columns
- Unique value counts for categorical columns

Use the dual-open pattern for Excel; for CSV use pandas-style read.

### Phase 2 — Propose analyses

Based on the data shape, propose 5–10 analyses. Tailor to what you see:

- **Customer-level transactions** → cohort retention, NRR/GRR, AOV trends, customer concentration, basket analysis, segment analysis
- **Time-series financial data** → trend analysis, growth decomposition, seasonality, margin walk, working capital cycle
- **Product / SKU data** → SKU contribution, price elasticity hints, inventory turnover
- **Survey or NPS data** → segment cuts, driver analysis, distribution
- **Operational metrics** → ratio analysis, productivity trends, utilization

Present using AskUserQuestion (multi-select). Each option includes one-line rationale: *why* this analysis matters for this data.

Allow "all of the above", "skip — let me pick differently", or write-in.

### Phase 3 — Execute selected analyses

For each analysis, write one calc tab in the output Excel using the ExcelAuthor utility.

```bash
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import excel, firmstyle

profile = firmstyle.load_profile()
author = excel.ExcelAuthor(firm_style=profile)
wb = author.new_workbook(title="<analysis-name> — <deal-or-source>")

# Always start with the source data tab, preserved exactly
author.add_source_tab(wb, "Source", rows=[...])

# Then a calc tab per chosen analysis, formulas referencing Source
author.add_calc_tab(wb, "Cohorts", header=[...], rows=[...],
                    output_columns=[...])

# Method tab explaining each analysis
author.add_method_tab(wb, """
Cohort analysis: customers grouped by signup month, MRR tracked monthly.
Retention = end MRR / start MRR for each cohort-month pair.
Source: Source!A2:F500.
""")

# Summary tab at the front with key findings
author.add_summary_tab(wb, "Summary",
    title="<analysis-name>",
    bullets=["Finding 1", "Finding 2", ...])

author.save(wb, Path("<output-path>.xlsx"))
PY
```

### Standards every output must follow

- **Source tab preserved unmodified** — never edit values
- **Calculations reference source via formulas, not hardcoded values**
- **Method tab explains each calculation** — methodology, source ranges, any judgement calls
- **Input cells colored** (yellow per firmstyle) when there are tunable parameters
- **Output cells colored** (light blue) for headline numbers
- **Number formats** appropriate to the data type (currency, percent, integer)

### Phase 4 — Markdown summary

Write a brief narrative `analysis-summary-YYYY-MM-DD.md`:
- What was analyzed
- Top 3–5 findings
- What's worth looking at first
- What's *not* answered by this analysis (gaps)
- Pointer to the Excel for detail

## Mode: ENHANCE

### Phase 1 — Read existing analysis

Open the existing Excel. Map out:
- What tabs exist
- What's been calculated
- What source data sits behind it (referenced or external)

Use the dual-open pattern. Tell the user what you found.

### Phase 2 — Propose extensions

Based on what's there, propose what could be added. Extension types:
- Additional cuts (e.g., existing cohort analysis lacks geographic segmentation)
- Missing sensitivities (e.g., margin analysis with no scenario range)
- Cross-tabs not yet run (e.g., NRR exists, but no NRR-by-cohort-and-segment)
- Visualizations to add
- Supporting data to pull in (e.g., comp benchmarks the analysis doesn't compare against)
- Reasonableness checks (e.g., distribution checks, outlier flags)

Present using AskUserQuestion. Each extension proposal includes: *what would be added*, *why it strengthens the analysis*.

### Phase 3 — Execute extensions

Open the existing Excel, add new tabs labeled `Enhanced: <topic>`. Never overwrite existing tabs. Save as a new file with `-enhanced-YYYY-MM-DD.xlsx` suffix; original is preserved.

Add a `Method (Enhanced)` tab listing what was added and how.

## Mode: REVIEW

### Phase 1 — Read existing analysis

Same as enhance Phase 1.

### Phase 2 — Audit

Check:

- **Math / formula correctness** — spot-check 10+ formulas, look for `#REF!`/`#NAME?`, broken references
- **Methodology soundness** — is this the right analytical approach for the question?
  - e.g., for retention: is it ARR-weighted or logo? Is churn defined consistently?
  - For cohorts: are cohort boundaries clean? Truncated cohorts handled?
- **Data lineage** — do source pulls match what was used? Are filters and exclusions documented?
- **Completeness** — what's missing that a typical reader will ask?
- **Reasonableness of conclusions** — do the findings actually follow from the math?
- **Auditability** — can a reader trace every number back to source? If not, where does it break?

### Phase 3 — Review report

Write `<deal-folder>/reports/analysis-review-YYYY-MM-DD.md`:

```markdown
# Analysis Review — <analysis-name>

## Summary
- Issues: N total ([H], [M], [L])
- Methodology soundness: [strong / fair / weak]
- Auditability: [strong / fair / weak]

## Correctness Issues
1. **[H]** [Tab!Cell] [issue] [suggested fix]
...

## Methodology Issues
...

## Data Lineage Issues
...

## Completeness — Likely Reader Questions
1. ...
...

## Suggested Enhancements
[Pointers to /dealflow-superanalyst --enhance to apply]
```

Render to PDF; update state and index.

## Output locations

- `<deal-folder>/reports/analysis-<topic>-YYYY-MM-DD.xlsx` (create / enhance)
- `<deal-folder>/reports/analysis-summary-<topic>-YYYY-MM-DD.md` (create)
- `<deal-folder>/reports/analysis-review-<topic>-YYYY-MM-DD.md` + `.pdf` (review)

If no deal folder, write to the source file's directory.

## Update state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-superanalyst --report "<output-path>"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "<output-path>" --category analysis --type xlsx \
  --indexed-by dealflow-superanalyst \
  --summary "[mode] — [topic] — [headline finding]" \
  --tags "analysis,<mode>,<topic>"
```

For each key finding, add to the index as a fact:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add-fact "<deal-folder>" \
  --path "<output-path>" --fact "<finding>" --source-ref "<tab>!<cell>" \
  --added-by dealflow-superanalyst
```

This makes findings discoverable by other skills (vp-review, pre-ic).

## Error handling

| Scenario | Response |
|---|---|
| Data is too sparse to analyze | "The data has [X] rows / lots of nulls. Useful analyses are limited. Recommend pulling more data or pick a different angle." |
| Data is too messy (mixed types in columns) | "Column [X] mixes text and numbers. I can clean it (you'll review the cleaning rules) or you can clean it first." |
| Existing analysis has external linked workbooks | "Linked workbook [path] is referenced but not present. Reviewing what's in this file only." |
