---
name: dealflow-returns
description: Standalone returns model — entry, debt, hold, exit, IRR/MOIC, full sensitivities. Separate from the operating model so deal structures can be swapped without disturbing the ops build.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Returns Model

Build a standalone returns model with full sensitivity tables. Decoupled from the operating model so you can iterate on deal structure (entry multiple, debt, equity check, hold period, exit) without touching how the business is modeled.

## Invocation

```
/dealflow-returns <path-to-deal-folder>
/dealflow-returns <path-to-deal-folder> --ops-model <path-to-ops-model.xlsx>
```

If `--ops-model` is provided, pull projected EBITDA / revenue from it. Otherwise, ask the user for projections.

## Prerequisites

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
```

Init state and index if needed.

## Phase 0 — Context (do this FIRST, before gathering inputs)

A returns model without context produces a generic IRR/MOIC + sensitivity grid that may completely miss the point of the actual structure. This skill is the most likely to encounter structured deals, where single-case returns are the wrong test. Before gathering inputs, do TWO things:

### 0a. Ask the user three quick context questions

Use a single `AskUserQuestion`:

1. **What's this returns model for?** — Live deal pricing decision, case study / interview / sourcing exercise, internal practice, sensitivity analysis on an existing structure.
2. **Who's the audience and what does success look like?** — Deal team, partner, IC, external case-study reviewer. The audience changes which sensitivities to surface.
3. **What's already been deliberately decided so the build doesn't re-litigate?** — Structure choices (equity-only vs LBO vs tranched growth equity vs structured pref), entry valuation framework, debt structure if known, exit multiple methodology, scenario definitions (e.g., "downside = revenue flat, base = 25% CAGR, upside = mgmt"). These are the things the user is treating as inputs, not questions.

Keep answers brief. If skipped, default to "live deal, internal audience, plain equity check, no structure specified" and note in the report header.

### 0b. Read sibling AI work and analysis BEFORE building

Inside the deal folder, look for and read these BEFORE Phase 1:
- `AI Work/*.md` — prior AI-generated artifacts. **Especially `Deal Structure*`, `Returns*`, or any document explaining the structure rationale.** The "why is this deal tranched / capped / participating" answer often lives here.
- `Analysis/*.md` — the user's framing notes
- Any `*Notes*` or `*Questions*` files
- `reports/` — prior reviews

Cite these in the report — if the user has already written down "the Step 2 tranche exists to protect downside while preserving upside conversion," your returns model should reflect and quantify that thesis, not ignore it.

### 0c. Structured deals — special rule (CRITICAL for this skill)

If the deal is structured (tranched, preferred with cap/floor, contingent funding, participation rights), single-case MOIC/IRR is **the wrong primary output**. The structure exists precisely BECAUSE of asymmetric payoffs:

- **Downside protection** via liquidation preference, accruing coupon, walk-away rights on later tranches
- **Upside participation** via conversion features
- **Dilution control** for founders, which is the negotiation lever that gets the structure accepted

For any structured deal, build the model with:

- **Multi-scenario returns:** downside / base / upside exit valuations
- **Structured vs vanilla counterfactual** at EACH scenario (not just base)
- **Probability-weighted MOIC and IRR** if the user has a view
- **Sensitivity to the optionality moments:** what happens if Step 2 isn't funded, what happens if conversion triggers, what the cap protects

If the user provides only single-case inputs, push back once: *"This looks like a structured deal. Single-case returns will understate the structure's value. Want me to model downside / base / upside scenarios with the structured-vs-vanilla delta at each?"* If they decline, proceed with single-case but note the limitation prominently.

### 0d. Default assumption: intentional until proven otherwise

If existing returns work has unusual definitions or apparent inconsistencies (e.g., a "Variance L2 vs Vanilla" row that doesn't match the headline MOIC delta), the FIRST hypothesis is intentional — often these rows show **founder dilution variance** rather than investor variance. Read carefully before flagging.

## Phase 1 — Gather inputs

Ask the user (or pull from ops model + config):

### Deal structure
- Deal type: equity only / LBO / minority growth equity / secondary
- Entry valuation (EV or equity?)
- Entry multiple (used or implied?)
- Equity check size
- Debt at entry (if LBO): total, structure (term loan, mezz, seller note), rates, amortization

### Hold and exit
- Hold period (years)
- Exit multiple assumption (revenue or EBITDA?)
- Exit timing (year)

### Cash flows during hold
- Annual EBITDA path (from ops model or user)
- Annual capex
- Annual debt service (if LBO)
- Dividend recap assumption (if applicable)

### Sensitivities
- Which variables to sensitize: entry multiple, exit multiple, EBITDA growth, leverage, hold period
- Range for each (e.g., entry multiple 8x–14x in 1x steps)

## Phase 2 — Build the model

Use ExcelAuthor. Tabs:

### 1. Assumptions
- All inputs as named ranges where possible
- Color-coded: yellow inputs, blue outputs
- Validation: warn if leverage > 6x EBITDA, exit < entry, etc.

### 2. Sources & Uses
- Equity check, debt tranches, fees, transaction costs
- Uses: purchase price, refinanced debt, transaction expenses, minimum cash

### 3. Operating cash flows
- EBITDA path (linked from ops model if provided, otherwise input)
- Less capex
- Less cash taxes (simple effective rate)
- Less change in NWC (simple % of revenue if revenue path given)
- = Unlevered free cash flow

### 4. Debt schedule (LBO mode)
- Opening balance, interest, mandatory amortization, sweep, ending balance
- Per tranche if multiple
- Total interest paid by year

### 5. Equity returns
- Initial equity check (negative)
- Annual cash sweep to equity (if any during hold)
- Exit equity value (exit EV − exit net debt)
- IRR (XIRR), MOIC, DPI/RVPI breakdown if hold has interim distributions

### 6. Sensitivities
Build matrices for the sensitivity dimensions. Standard set:
- Entry × Exit multiple → IRR
- Entry × Exit multiple → MOIC
- EBITDA CAGR × Exit multiple → IRR
- Leverage × Exit multiple → IRR (LBO)
- Hold period × Exit multiple → IRR

### 7. Scenarios
Bull / Base / Downside cases. Each is a column. Reuse the same model structure with different driver values.

### 8. Method tab
Explain methodology, assumptions, and any judgement calls. List anything not modeled (e.g., management option pool dilution, working capital seasonality).

### 9. Summary at the front
Headline:
- Base case IRR: X%
- Base case MOIC: Y.Yx
- Equity check: $A
- Hold: B years
- Sources/uses: $C uses, $D debt, $E equity
- Downside IRR: F%, Bull IRR: G%
- Key sensitivities (which variable moves IRR most)

## Phase 3 — Build with ExcelAuthor

```bash
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import excel, firmstyle

profile = firmstyle.load_profile()
author = excel.ExcelAuthor(firm_style=profile)
wb = author.new_workbook(title="Returns Model — <deal-name>")

# All tabs above, with formulas referencing Assumptions
# ...

author.add_method_tab(wb, """
Returns model assumptions:
- Tax rate: 25% effective (override on Assumptions tab)
- NWC: 5% of revenue
- Capex: as input by year
- LBO debt: <structure>
- Exit: <multiple type> × <year N EBITDA or revenue>
- IRR: XIRR on equity cash flows
- MOIC: cumulative equity returns / equity check

Not modeled:
- Management equity / option pool dilution
- Tax shield optimization
- Refinancing during hold (other than scheduled paydown)
- Interim distributions (unless toggled on Assumptions)
""")

author.add_summary_tab(wb, "Summary", title="Returns — <deal-name>", bullets=[...])

author.save(wb, Path("<deal-folder>/reports/returns-model-<DATE>.xlsx"))
PY
```

## Phase 4 — Markdown summary

Write `<deal-folder>/reports/returns-summary-YYYY-MM-DD.md`:
- Headline returns (base/bull/downside IRR, MOIC)
- Key drivers (which sensitivity matters most)
- Comparison to firm's hurdle (from config if available)
- Caveats and what's not modeled

Render PDF.

## Phase 5 — Update state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-returns --report "reports/returns-model-<DATE>.xlsx"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/returns-model-<DATE>.xlsx" --category model --type xlsx \
  --indexed-by dealflow-returns \
  --summary "Returns: base IRR X%, MOIC Y.Yx, leverage Z.Zx" \
  --tags "returns,model,irr,moic"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add-fact "<deal-folder>" \
  --path "reports/returns-model-<DATE>.xlsx" \
  --fact "Base case IRR: X%" --source-ref "Returns!B12" \
  --added-by dealflow-returns
# repeat for MOIC, leverage, downside IRR
```

## Phase 6 — Hand off

Tell the user the headline returns and what sensitivity matters most. Offer:
- "Want me to rerun with different exit multiple assumptions?"
- "Want to add a recession case?"
- "Should I draft the returns section of the IC memo from this?"

## Error handling

| Scenario | Response |
|---|---|
| Ops model path doesn't open | "Couldn't open the ops model. Falling back to user-provided EBITDA path." |
| EBITDA path is negative throughout | "EBITDA path is negative — typical returns math doesn't apply. Want me to build a runway/dilution model instead?" |
| Leverage > 8x EBITDA | "Leverage of [X]x is high — flagging but proceeding. Lenders typically max out around 6–7x for most strategies." |
