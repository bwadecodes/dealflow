---
name: dealflow-vp-review
description: Detailed scrub of memos, models, and analyses for correctness and completeness before they go to a senior person. Catches math errors, broken citations, inconsistent claims, missing sections, and unreasonable model assumptions. Not a judgement call on the deal.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# VP Review

The job a careful VP would do before passing materials up: line-by-line correctness check, completeness check, and a reasonableness scrub on the model. Focuses on what's wrong or missing — not whether the deal is good.

## Invocation

```
/dealflow-vp-review <path-to-deal-folder>
/dealflow-vp-review <path-to-deal-folder> --memo <path>
/dealflow-vp-review <path-to-deal-folder> --model <path>
```

By default, auto-discovers the latest memo, model, and analysis files in the deal folder. Use `--memo` and `--model` to point at specific files.

## Prerequisites

### Python deps + utilities

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
python3 -c "import pymupdf" 2>/dev/null || pip install pymupdf --quiet
python3 -c "import docx" 2>/dev/null || pip install python-docx --quiet
```

Lazy-init state and index:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" init "<deal-folder>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" init "<deal-folder>"
```

## Phase 1 — Discover materials

If `--memo` and `--model` aren't given:

1. Look in `<deal-folder>/reports/` for the latest memo (.md or .docx with words like "memo", "ic", "prescreen")
2. Look in `<deal-folder>/` for the latest model (.xlsx)
3. Look in `<deal-folder>/reports/` for the latest analysis files

Confirm with the user: *"Reviewing: [memo path], [model path], [analyses]. Right files?"*

## Phase 2 — Read materials with index awareness

For each material, check the index first:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" is-stale "<deal-folder>" --path "<path>"
```

If indexed and not stale, read the index summary + key facts to save tokens. Read the source file only for sections you need to verify directly.

For the model, use the dual-open pattern:
```bash
python3 -c "
import openpyxl
wb_formulas = openpyxl.load_workbook('<model>', data_only=False)
wb_values = openpyxl.load_workbook('<model>', data_only=True)
# inspect both
"
```

## Phase 3 — Correctness checks

### Math and formula audit (model)

For each tab:
- List all formulas. Spot-check 5–10 random formulas — do they reference the right cells?
- Check for broken references (`#REF!`, `#NAME?`, `#VALUE!`)
- Check for hardcoded numbers in formula cells (a sign of overrides)
- Verify that totals tie (sum of column = total row)
- Verify that P&L → cash flow → balance sheet tie out if all three tabs exist
- Check unit consistency (mixing $M and $K is a common bug)

### Internal consistency between memo and model

For every numerical claim in the memo, check that the model supports it:
- "ARR is $8M" → does the model show $8M ARR?
- "We're targeting 30% IRR" → does the model's returns tab show 30% IRR at base case?
- "Gross margin is 65%" → check the model

Flag claims that don't tie to the model with the file + section reference and what the model actually shows.

### Citation completeness

Every factual claim in the memo should be backed by either:
- A document in the data room (cross-reference the index)
- A line item in the model
- A web source (footnote URL)

Flag uncited claims.

### Standard sections

Load the firmstyle IC memo template if configured. Check each required section is present. Flag missing sections.

### Formatting and copy

- Typos and grammar
- Inconsistent date formats
- Inconsistent capitalization of company name
- Mixed units ($M, $MM, $K)
- Unfilled placeholders (TK, TBD, XXX)
- Numbers without context (a single percent without saying compared to what)

### Missing exhibits

If firmstyle defines `standard_exhibits` (e.g., football field, returns waterfall, sensitivity), check each is present in the memo. Flag missing.

## Phase 4 — Reasonableness scrub on model

Read the model assumptions and cases. For each material driver:

### Individual assumption reasonableness

- Compare to historicals in the model (if visible)
- Compare to public comps (the index may have desk research; check)
- Compare to industry norms (use general knowledge; flag where confidence is low)

Mark each driver: **aggressive / in-line / conservative / unable to assess**.

### Base case vs. management case test

**Is the "base case" actually a base case, or is it the management case in disguise?**

- Compare base case revenue growth to what the deck or CIM forecasts. If they match within ~5%, the base case may be the management case.
- Compare base case margins to historicals. If margins jump in Y1 of the model with no operational change, the base case is optimistic.
- Compare base case S&M efficiency and headcount growth to historicals.

Flag with: *"Base case Y2 revenue ($X) equals management forecast within X%. Consider whether this should be discounted by 10–20% for a true base case."*

### Downside case test

**Does the downside case properly reflect a real downside?**

A real downside in different business types:
- **SaaS**: logo churn acceleration + expansion compression + sales productivity drop + extended sales cycles
- **Consumer / DTC**: AOV compression + CAC inflation + cohort retention drop
- **Services**: utilization drop + bill rate compression + delayed payment

Check that the model's downside actually moves these drivers, not just a flat haircut on revenue.

Flag with severity:
- **High**: "Downside shows 90% of base revenue but everything else stays bull case. Not coherent."
- **Medium**: "Downside revenue moves but customer churn assumption doesn't change. For SaaS, real downside should include churn acceleration."

### Bull case sanity

- Are the bull case assumptions individually plausible? (e.g., 60% growth Y4 of a $100M business is rare — flag for justification)
- Cross-case consistency: if revenue is up 50% bull vs. 0% downside, do S&M and headcount move with it?

## Phase 5 — Compile report

Write the report to `<deal-folder>/reports/vp-review-YYYY-MM-DD.md`.

Structure:

```markdown
# VP Review — <deal-name>

**Reviewer:** dealflow-vp-review
**Materials reviewed:** [memo path], [model path], [analyses]
**Date:** YYYY-MM-DD

## Summary

- Issues found: [N]
- High severity: [N]
- Medium: [N]
- Low: [N]

## Correctness Issues

### Math / formula errors (model)
1. **[High]** [Tab!Cell] [description] [suggested fix]
...

### Memo–model consistency
...

### Citation gaps
...

### Formatting and copy
...

## Completeness Issues

### Missing sections
...

### Missing exhibits
...

## Model Reasonableness

### Assumption-level flags
| Driver | Y1 | Y2 | Y3 | Reasonableness | Note |
|---|---|---|---|---|---|
| Revenue growth | 50% | 40% | 30% | aggressive | Compared to comps avg 30%/25%/20% |
...

### Base case vs. management case
[Findings with specifics]

### Downside coherence
[Findings with specifics]

### Cross-case consistency
[Findings with specifics]

## What's NOT in scope for this review

This review does not pass judgement on whether the deal is good — that's
for /dealflow-pre-ic and the IC itself. Issues flagged here are
correctness and completeness, not investment opinion.
```

## Phase 6 — PDF and index update

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-pdf.py" \
  "<deal-folder>/reports/vp-review-<DATE>.md" \
  "<deal-folder>/reports/vp-review-<DATE>.pdf"

python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-vp-review --report "reports/vp-review-<DATE>.md"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/vp-review-<DATE>.md" --category review --type md \
  --indexed-by dealflow-vp-review \
  --summary "VP review — N issues found (H/M/L counts)" \
  --tags "review,vp-review"
```

## Phase 7 — Hand off

Tell the user the headline counts and the highest-severity findings. Offer:
- "Want me to walk you through the top issues?"
- "Want me to draft fixes for the math errors?"
- "Ready for /dealflow-pre-ic once these are addressed?"

## Error handling

| Scenario | Response |
|---|---|
| No memo found | "I couldn't find a memo. Point me at one with --memo, or run /dealflow-prescreen first." |
| No model found | "No model in the deal folder. Skip the model checks?" |
| Model has linked workbooks | "Model has external links to [path]. I'll review what's in the workbook but can't follow the links. Note: some formulas may not resolve." |
| Model has macros | "Model contains macros. I won't execute them — reviewing the static structure only." |
