---
name: dealflow-termsheet
description: Analyze a cap table and charter or LLC agreement, build a pro forma cap table, and draft a term sheet aligned with firm preferences. Outputs cap table analysis (MD/PDF), pro forma cap table (Excel), and term sheet draft (MD/DOCX). For drafting only — counsel must review before use.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Term Sheet

Analyze existing cap structure and draft a term sheet aligned with the firm's standard preferences. Output is a draft for counsel review, never legal advice.

## Invocation

```
/dealflow-termsheet <path-to-deal-folder>
/dealflow-termsheet <path-to-deal-folder> --cap-table <path> --charter <path>
```

By default, scan the deal folder for cap table (.xlsx with "cap" in name) and charter (.pdf/.docx with "charter", "llc", "agreement").

## Prerequisites

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
python3 -c "import pymupdf" 2>/dev/null || pip install pymupdf --quiet
python3 -c "import docx" 2>/dev/null || pip install python-docx --quiet
```

Firm-style strongly recommended:

```bash
python3 -c "from dealflow_lib import firmstyle; print(firmstyle.is_configured())"
```

If `False`, warn: *"No firm-style profile found. Term sheet draft will use generic NVCA defaults. Strongly recommend running /dealflow-firmstyle first so the draft matches your firm's standard terms."* Then continue.

Init state and index.

## Phase 0 — Context (do this FIRST, before reading the cap table)

A term sheet draft without context produces generic firm-style terms that may completely miss the deal-specific structural choices the user has already made. Before reading the cap table, do TWO things:

### 0a. Ask the user three quick context questions

Use a single `AskUserQuestion`:

1. **What's this term sheet for?** — Real signed-LOI deal heading to term sheet, case study / interview, internal practice, comparative analysis of structure choices.
2. **Who's the audience and what does success look like?** — Counsel review, partner sign-off, IC pre-read, external reviewer evaluating structure judgment.
3. **What's already been deliberately decided about the structure so the draft doesn't re-open it?** — Tranched vs single-close structure, liquidation preference type (non-participating / participating / capped), pro rata rights, anti-dilution flavor (broad-based weighted avg / full ratchet), board composition. If the user has already negotiated or pre-committed to specific terms, those are inputs to the draft, not questions to re-open.

Keep answers brief. If skipped, default to "real deal, counsel + partner audience, firm-style defaults, nothing pre-decided" and note in the analysis.

### 0b. Read sibling AI work and analysis BEFORE the cap table

Inside the deal folder, look for and read these BEFORE Phase 1:
- `AI Work/*.md` — prior AI-generated artifacts. **Especially `Deal Structure*` or any document explaining the structure rationale.** Term sheet terms should reflect the strategic logic of the structure, not just firm defaults.
- `Analysis/*.md` — the user's framing notes
- Any `*Notes*`, `*Questions*`, or `Memo Feedback*` files
- `reports/` — prior reviews (esp. returns analysis if it exists)

Cite these in the analysis when relevant. If the user has already written down "we want a 2-step close with a cap on Step 2 preference," your term sheet draft should reflect that thesis.

### 0c. Default assumption: intentional until proven otherwise

If the existing cap table or charter has unusual terms (non-standard preferences, unusual pay-to-play, custom anti-dilution), the FIRST hypothesis is that prior investors negotiated those on purpose. Note them; don't reflexively normalize to firm-style defaults in the draft. Ask the user before stripping non-standard inherited terms.

### 0d. Structured deals — special note

If this is a structured deal (tranched, capped preference, contingent funding), the term sheet's value lives in the structural terms (Step 2 trigger conditions, walk-away rights, conversion mechanics, anti-dilution scope). Spend disproportionate effort on those vs. the boilerplate. If a returns model exists in `AI Work/` or `reports/`, the term sheet should align with the structure that model assumes.

## Phase 1 — Read cap table

Open with the dual-pattern. Identify:
- Founders and their share counts / %
- Investor classes (common, preferred series, SAFEs, notes)
- Per-series preferences (if listed in the cap table; usually only counts and prices)
- Option pool (allocated, granted, outstanding, unvested)
- Total fully diluted shares

If the cap table is missing or messy, walk the user through what's needed.

## Phase 2 — Read charter / LLC agreement

Extract key existing terms:

### Economic terms
- Liquidation preference per series (1x non-participating? 1x participating capped? cap?)
- Anti-dilution (broad-based weighted average / narrow-based / full ratchet)
- Dividend rights (cumulative? non-cumulative? rate?)
- Conversion price / ratio per series
- Pay-to-play provisions

### Governance terms
- Board composition (count, who appoints which seat)
- Protective provisions (what requires preferred consent)
- Voting thresholds
- Drag-along, tag-along, ROFR, co-sale
- Information rights
- Pre-emptive rights / pro-rata

### Other
- Vesting schedules (especially founder vesting)
- Repurchase rights
- Special provisions

Use pymupdf for text extraction; for visual/scanned docs, use `Read` directly so Claude can OCR.

## Phase 3 — New round inputs

Ask the user via AskUserQuestion:

- Round size (total $)
- Pre-money valuation
- Our check size (% of round)
- Round type (Series A/B/C, bridge, extension)
- New option pool increase (% post-money) — pre-money or post-money pool top-up?
- Lead investor or co-lead?
- Any specific terms to negotiate beyond the firm's standard set?

## Phase 4 — Build pro forma cap table

Open the existing cap table. Add columns for the new round:

- New shares issued (round size / new price per share)
- Pre-money pool top-up (option pool increase before the round)
- Pro forma ownership %

Build a waterfall: at exit value X, who gets what under the new structure? Show 3 exit scenarios (low, base, high) — useful for management to see how their economics change.

Use ExcelAuthor:

```bash
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import excel, firmstyle

profile = firmstyle.load_profile()
author = excel.ExcelAuthor(firm_style=profile)
wb = author.new_workbook(title="Pro Forma Cap Table — <deal-name>")

# Existing cap table tab — preserved
author.add_source_tab(wb, "Existing Cap", rows=[...])

# New round inputs tab
author.add_calc_tab(wb, "New Round Inputs",
    header=["Item", "Value"],
    rows=[
        ["Round size ($)", 20000000],
        ["Pre-money ($)", 80000000],
        ["Post-money ($)", "=B2+B3"],
        ["Option pool top-up %", 0.05],
        ...
    ],
    input_columns=[2])

# Pro forma — formulas everywhere
author.add_calc_tab(wb, "Pro Forma", header=[...], rows=[...])

# Waterfall at exit scenarios
author.add_calc_tab(wb, "Waterfall", header=[...], rows=[...])

author.add_method_tab(wb, """
Pro forma assumes:
- Option pool top-up sized to bring total pool to target % post-money,
  taken from existing shareholders (pre-money treatment).
- New series ranks senior to existing series for liquidation preference.
- Waterfall shows preferred preference, then conversion threshold,
  then participating economics (if applicable).
""")

author.add_summary_tab(wb, "Summary", title="Pro Forma Cap Table", bullets=[
    "New round dilution: founders X%, existing investors Y%",
    "Our ownership: Z% post-money",
    "Exit at <base case>: our return $A on $B check",
])

author.save(wb, Path("<deal-folder>/reports/pro-forma-cap-table-<DATE>.xlsx"))
PY
```

## Phase 5 — Cap table analysis report

`<deal-folder>/reports/cap-table-analysis-YYYY-MM-DD.md`:

```markdown
# Cap Table Analysis — <deal-name>

## Existing Structure

### Ownership snapshot
- Founders: A%
- Employees / pool: B%
- Existing investors: C% (Series Seed X%, Series A Y%)

### Existing preferences
| Series | Preference | Anti-dilution | Conversion |
|---|---|---|---|
| Seed | 1x non-part | BBWA | 1:1 |
| A | 1x non-part | BBWA | ... |

### Governance
- Board: <composition>
- Protective provisions: <summary>
- Other: <vesting, ROFR, drag/tag>

## Proposed New Round

### Economics
- Size: $X, pre-money: $Y, post-money: $Z
- Pool top-up: A% (pre-money treatment)
- Our check: $B (C% of round)

### Pro Forma Ownership
[table]

### Returns Snapshot
[exit scenarios]

## Flags

- [Any unusual existing terms]
- [Cap table cleanup needed]
- [Founder dilution concerns]
- [Existing investor consent requirements]
```

Render PDF.

## Phase 6 — Term sheet draft

Load firm-style `term_preferences` and `templates.termsheet`. If both exist, use them. Otherwise, use NVCA-aligned defaults.

Draft `<deal-folder>/reports/term-sheet-draft-YYYY-MM-DD.md`:

```markdown
# SUMMARY OF PROPOSED TERMS — <deal-name>

**DRAFT FOR COUNSEL REVIEW — NOT LEGAL ADVICE**

## Issuer / Securities
- Company: <Company Inc.>
- Security: Series <X> Preferred Stock

## Investment
- Round size: $X
- Pre-money: $Y
- Post-money: $Z
- Investor check: $A (B%)
- Lead investor: <firm name>

## Economics
- **Liquidation Preference**: [from firm-style term_preferences.liquidation_preference]
- **Dividends**: [standard or as specified]
- **Conversion**: [1:1 standard]
- **Anti-Dilution**: [from firm-style]
- **Pay-to-Play**: [if firm standard]

## Governance
- **Board**: [from firm-style board_composition]
- **Protective Provisions**: [from firm-style]
- **Information Rights**: [standard for round size]

## Investor Rights
- **Pro Rata Rights**: [from firm-style pro_rata_rights]
- **ROFR / Co-Sale**: [from firm-style]
- **Drag-Along**: [from firm-style drag_along]
- **Registration Rights**: [standard]

## Founder / Employee
- **Vesting**: [from firm-style vesting_default; e.g., 4 years 1 year cliff]
- **Option Pool**: [from firm-style option_pool_target]

## Conditions
- Satisfactory completion of legal, financial, commercial diligence
- Customary representations and warranties
- Signed employment agreements / IP assignment

## Confidentiality / Exclusivity
- [standard 30 days exclusivity if applicable]

## Expenses
- [standard — counsel fees reimbursed up to cap]

---

**Disclaimer**: This term sheet draft was generated by dealflow-termsheet as a starting point for negotiation. It is not legal advice. All terms must be reviewed and refined by qualified counsel before use. The firm-style profile drove the substantive choices; refer to <firm-style.yaml> for the underlying preferences.
```

Render to PDF and DOCX. For DOCX, use python-docx:

```bash
python3 - <<PY
import docx
from docx.shared import Pt
doc = docx.Document()
# build doc from markdown — simplified
with open("<md-path>") as f:
    for line in f:
        # convert headings, bullets, etc. (simplified — production version uses pandoc)
        doc.add_paragraph(line.rstrip())
doc.save("<docx-path>")
PY
```

Better: use pandoc if available for clean DOCX conversion.

## Phase 7 — Update state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-termsheet --report "reports/term-sheet-draft-<DATE>.md"

python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" set-stage "<deal-folder>" --stage termsheet

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/term-sheet-draft-<DATE>.md" --category termsheet --type md \
  --indexed-by dealflow-termsheet --summary "TS draft for <deal-name>" \
  --tags "termsheet,draft"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/cap-table-analysis-<DATE>.md" --category analysis --type md \
  --indexed-by dealflow-termsheet \
  --summary "Cap table analysis — existing structure and pro forma" \
  --tags "cap-table,analysis"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/pro-forma-cap-table-<DATE>.xlsx" --category model --type xlsx \
  --indexed-by dealflow-termsheet \
  --summary "Pro forma cap table with waterfall" \
  --tags "cap-table,pro-forma,waterfall"
```

## Phase 8 — Hand off

Tell the user:
- Headlines on cap table (existing structure summary)
- Pro forma our ownership %
- Key TS terms drawn from firm-style profile
- **Strong reminder: counsel must review before use**

Offer:
- "Want me to redraft any specific term?"
- "Compare against [specific past deal]?"
- "Walk through the waterfall at different exit values"

## Strong disclaimers — everywhere

Every output file (MD, PDF, DOCX) must contain the disclaimer:

> "Draft generated by dealflow-termsheet for counsel review. Not legal advice. All terms must be reviewed and refined by qualified counsel before negotiation or signing."

Print this in the SKILL hand-off message as well.

## Error handling

| Scenario | Response |
|---|---|
| No cap table | "Need a cap table (.xlsx) to build pro forma. Point me at one or skip pro forma." |
| No charter | "Charter not found — existing terms analysis will be limited. I'll mark inferred-only items." |
| Cap table doesn't tie | "Cap table fully diluted shares don't sum cleanly. Showing what I have, flagging the discrepancy. Resolve before relying on pro forma." |
| Existing structure has unusual provision | "Existing charter has [unusual term]. I've flagged this in the analysis — confirm with counsel before drafting the new TS around it." |
