---
name: dd-model
description: Review a financial model (.xlsx) — understand the business model, map key drivers, test assumptions, and surface the data points that matter most for your investment decision.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Agent
  - AskUserQuestion
---

# Financial Model Review

Read a financial model and produce a business-intelligence-focused review — understanding the business, testing assumptions, and surfacing the most interesting data points.

## Invocation

```
/dd-model <path-to-excel-file>
/dd-model <path-to-excel-file> "<deal context>"
```

The optional context string helps frame the analysis — e.g., "B2B SaaS, Series A at $40M pre, net revenue retention 120%."

## Prerequisites

### 1. Load the config

Same resolution order as `/dd-dataroom`:
1. If a `--config` path was passed in the invocation, use that file
2. `~/.claude/dealflow/diligence-config.yaml` (default location)
3. If neither exists: prompt user to run `/dd-setup` or offer to use the default template
4. Locate defaults: `Glob **/dealflow/config/defaults/pe-lower-middle-market.yaml`

### 2. Check Python + openpyxl

```bash
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
```

If Python is not installed: *"Python is required for reading Excel files. Install it from python.org and try again."*

### 3. Validate the file

Confirm the file exists and is `.xlsx`:
```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('<filepath>', data_only=True)
print(f'Workbook loaded: {len(wb.sheetnames)} sheets')
for s in wb.sheetnames:
    print(f'  - {s}')
"
```

If the file is password-protected: *"This file is password-protected. Remove the password in Excel and try again."*

If the file is not `.xlsx`: *"This skill works with .xlsx files. If your model is in Google Sheets, download it as .xlsx first."*

## Phase 1: Model Comprehension

Open the workbook **twice** — this is critical:

**Read 1 — Formulas (model structure):**
```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('<filepath>', data_only=False)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f'\n=== {sheet} ({ws.max_row} rows x {ws.max_column} cols) ===')
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 50), values_only=False):
        vals = []
        for cell in row:
            if cell.value is not None:
                v = str(cell.value)
                vals.append(v[:80])
        if any(v for v in vals):
            print('\t'.join(vals))
"
```

**Read 2 — Cached values (computed numbers):**
```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('<filepath>', data_only=True)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f'\n=== {sheet} ===')
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 50), values_only=True):
        vals = [str(c) if c is not None else '' for c in row]
        if any(v for v in vals):
            print('\t'.join(vals))
"
```

**Important:** `data_only=True` returns values from the last time the file was saved in Excel. If values are mostly `None`, warn the user: *"This file's cached values are empty — it may have been exported from Google Sheets without opening in Excel first. The numbers shown may be incomplete, but I can still analyze the model structure from formulas."*

From the two reads, determine:

1. **Tab inventory** — what each sheet does (assumptions, revenue build, P&L, balance sheet, cash flow, scenarios, cap table, etc.)
2. **Business model identification** — SaaS? Marketplace? DTC? Subscription? Services? What are the revenue lines?
3. **Driver map** — the key inputs that drive the outputs. Trace formulas to find:
   - What feeds into revenue (units × price? Growth %? Bottoms-up by segment?)
   - What drives costs (% of revenue? Headcount-based? Fixed?)
   - How deep are the assumptions (SKU-level detail vs. top-line growth rate?)

Output a plain-English summary:

> *"This is a [X]-year [business type] model built on [revenue driver description]. Revenue is driven by [key inputs]. The model has [X] tabs covering [list]. The assumption depth is [shallow/moderate/deep] — [explain what that means]."*

Note any named ranges, linked workbooks, or macros encountered.

## Phase 2: Assumption Analysis

For each key driver identified in Phase 1:

- **What's assumed** — the actual numbers and growth rates
- **Depth assessment** — is this a single growth % or built from unit economics, conversion funnels, cohort data?
- **Reasonableness flags:**
  - 🟢 Conservative or in-line with historicals
  - 🟡 Moderate — plausible but untested
  - 🔴 Aggressive — significantly above historical trends or industry benchmarks
- **Sensitivity** — which assumptions move the needle most? Identify the 3-5 inputs where a small change creates a large output swing.

Compare projections to historicals where both exist in the model. Flag step-changes that aren't explained.

## Phase 3: Key Data Points & Insights

The business intelligence layer — this is where the review earns its value:

- **Inflection points** — step-changes in the model (e.g., "Gross margin jumps from 62% to 78% in Year 3 as the company shifts from professional services to software")
- **Operating leverage** — where do margins expand as revenue scales? Which cost lines shrink as a % of revenue?
- **Cash dynamics** — burn rate, runway, when does the business turn cash-flow positive? What is the cash conversion of earnings?
- **Key assumptions to test in diligence** — the 5-10 assumptions that matter most and need validation from the company or third parties
- **Hidden risks** — assumptions that are internally inconsistent, unusually optimistic, or not supported by the historicals

## Phase 4: Report Output

Create the output directory:
```bash
mkdir -p "<deal-folder>/dd-reports"
```

Determine the deal folder — use the parent directory of the model file's location. Save using `Write` to:
```
<deal-folder>/dd-reports/model-review-YYYY-MM-DD.md
```

### Report structure

```markdown
# Financial Model Review: [Deal Name / File Name]

**Date:** YYYY-MM-DD
**Model file:** [filename]
**Sheets:** [count]
**Config template:** [PE / VC / Growth Equity / Custom]

---

## Business Model Summary

[Plain-English description of what the model says the business is and how it makes money. Written for an investor, not an accountant. 2-3 paragraphs.]

---

## Driver Map

| Driver | Input | Depth | Source Tab |
|--------|-------|-------|------------|
| Revenue | [description] | [shallow/moderate/deep] | [tab name] |
| COGS | [description] | [shallow/moderate/deep] | [tab name] |
| ... | ... | ... | ... |

[Commentary on overall model quality and depth]

---

## Assumption Analysis

### [Driver Name]

**What's assumed:** [specific numbers and rates]
**Depth:** [how detailed the build is]
**Reasonableness:** [🟢/🟡/🔴] — [explanation]
**Sensitivity:** [how much output moves when this changes]

[Repeat for each key driver]

---

## Key Findings

### Inflection Points
- [Finding with specific numbers and tab references]

### Operating Leverage
- [Finding]

### Cash Dynamics
- [Finding]

### Hidden Risks
- [Finding]

---

## Assumptions to Test

Prioritized list of what needs validation in diligence:

1. **[Critical]** [Assumption] — [why it matters, what to ask]
2. **[Critical]** [Assumption] — [why it matters, what to ask]
3. **[Important]** [Assumption] — [why it matters, what to ask]
...
```

## Interactive Mode

After saving:

> **Report saved to `<path>/dd-reports/model-review-YYYY-MM-DD.md`.**
>
> You can ask me to dig deeper into any part of the model — specific tabs, assumptions, scenarios, or comparisons. Or move on to `/dd-questions` to build your diligence question list.

For follow-ups, re-read specific tabs as needed. Reference exact cell ranges and formulas when answering questions.

## Error Handling

| Scenario | Response |
|----------|----------|
| File not found | *"Can't find that file. Check the path and try again."* |
| Not .xlsx | *"This skill works with .xlsx files. If your model is in Google Sheets, download it as .xlsx first."* |
| Password-protected | *"This file is password-protected. Remove the password in Excel and try again."* |
| Cached values are None | Warn user (see Phase 1), proceed with formula analysis only |
| Very large model (50+ tabs) | Focus on the most important tabs first (P&L, revenue, assumptions). Summarize secondary tabs. |
| Named ranges / linked workbooks | Note them in the report. Flag any that couldn't be resolved. |
| Python not installed | *"Python is required for reading Excel files. Install it from python.org and try again."* |