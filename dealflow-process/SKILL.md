---
name: dealflow-process
description: Lay out a full deal process — phases from LOI through close, scope of third-party work, workstream tracker with owners and dates. Stateful — re-runs update status. Outputs a process plan (MD/PDF) and an Excel tracker.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Deal Process

Build and maintain the diligence process plan for a deal — workstreams, third-party providers, dates, owners, status. Stateful: re-running updates rather than overwriting.

## Invocation

```
/dealflow-process <path-to-deal-folder>
/dealflow-process <path-to-deal-folder> --update         # update existing tracker
/dealflow-process <path-to-deal-folder> --close-out      # mark all workstreams done
```

## Prerequisites

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet

python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" init "<deal-folder>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" init "<deal-folder>"
```

## Phase 1 — Read context

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" read "<deal-folder>"
```

From state, learn:
- Current deal stage
- What skills have been run
- Any existing workstreams (re-running)

Read config (`~/.claude/dealflow/diligence-config.yaml`) to determine deal type (VC, growth, PE LMM/MM/buyout).

## Phase 2 — Determine process shape

Different deal types have different process shapes. Use the config's investment approach to determine:

### VC / Growth equity process

Phases: Initial → LOI → Confirmatory DD → SPA → Close (typical 4–8 weeks)

Standard workstreams:
- Management diligence (deep dive sessions)
- Financial diligence (internal)
- Customer references
- Technical / product diligence (often internal, sometimes external)
- Legal DD (charter, cap table, IP, employment)
- Background checks on founders
- Documentation (term sheet, SPA, side letters)

Typical third-party work:
- Legal counsel
- Background check provider
- Optional: technical DD firm
- Optional: market study for thesis validation

### PE LMM / MM / Buyout process

Phases: IOI → Management Meeting → LOI → Confirmatory DD → SPA → Financing → Close (typical 8–16 weeks)

Standard workstreams:
- Quality of Earnings (QoE)
- Commercial / market study
- Legal DD
- IT / cybersecurity DD
- Insurance DD
- Tax structuring
- Environmental (if applicable)
- Operational DD (management interviews, site visits)
- Customer references (often via commercial DD provider)
- Financing (debt arrangement)
- Documentation

Typical third-party work:
- QoE provider (Big 4 or specialist)
- Commercial DD firm
- Legal counsel
- IT/cyber DD firm
- Insurance broker
- Tax advisor
- Environmental consultant (for industrial/real estate)
- Background checks

Present the standard process to the user with AskUserQuestion: "Here's the standard process for [deal type]. Want to keep as-is, add workstreams, remove any?"

## Phase 3 — Detail each workstream

For each workstream:

- **Owner**: who runs it (internal team member or external provider)
- **Provider**: if external, named provider (ask the user, or leave blank for them to fill in)
- **Start date**
- **End date / target**
- **Dependencies**: which other workstreams must complete first
- **Deliverable**: what the workstream produces
- **Status**: not started / in progress / blocked / complete

For the typical durations, use sensible defaults (e.g., QoE: 3–4 weeks, legal DD: 2–4 weeks). Let the user override.

## Phase 4 — Build the tracker

Excel workbook with these tabs:

- **Summary** — dashboard view: counts by status, key dates, critical path
- **Workstreams** — full list with all fields, sortable
- **Gantt** — rows are workstreams, columns are weeks, X marks active period
- **Third Parties** — list of external providers with contact placeholders
- **Decisions / Open Items** — running log

Use ExcelAuthor:

```bash
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import excel, firmstyle

profile = firmstyle.load_profile()
author = excel.ExcelAuthor(firm_style=profile)
wb = author.new_workbook(title="Deal Process — <deal-name>")

# Workstreams tab
author.add_calc_tab(wb, "Workstreams",
    header=["Workstream", "Owner", "Provider", "Start", "End", "Dependencies", "Deliverable", "Status"],
    rows=[
        ["QoE", "Internal lead", "TBD - Big 4 or specialist", "2026-06-01", "2026-06-28", "", "QoE report", "Not started"],
        ...
    ])

# Third Parties tab
author.add_calc_tab(wb, "Third Parties",
    header=["Workstream", "Provider", "Contact", "Estimated Fee", "Status"],
    rows=[...])

# Gantt tab — weeks across, workstreams down
# (build dynamically based on start/end dates)
author.add_calc_tab(wb, "Gantt", header=["Workstream", "W1", "W2", ...], rows=[...])

# Open Items tab
author.add_calc_tab(wb, "Open Items",
    header=["Date", "Item", "Owner", "Resolved?"], rows=[])

# Summary at front
author.add_summary_tab(wb, "Summary", title="Deal Process Dashboard", bullets=[
    "Total workstreams: N",
    "Not started: A | In progress: B | Blocked: C | Complete: D",
    "Critical path: [list]",
    "Target close: <date>",
])

author.save(wb, Path("<deal-folder>/reports/deal-tracker-<DATE>.xlsx"))
PY
```

## Phase 5 — Write the process plan

`<deal-folder>/reports/deal-process-plan-YYYY-MM-DD.md`:

```markdown
# Deal Process Plan — <deal-name>

## Overview
- Deal type: [VC / Growth / PE LMM / etc.]
- Current stage: [prescreen / DD / IC / etc.]
- Target close: <date>
- Total estimated weeks: N

## Phases

### Phase 1: [Name] (Week 1–2)
- Workstreams: [list]
- Decision gate: [milestone]

### Phase 2: ...

## Workstream Detail
[Per workstream: scope, owner/provider, dates, deliverable, dependencies]

## Third-Party Providers
[Per provider: workstream, role, estimated fee, status]

## Critical Path
[Which workstreams gate the close date]

## Decision Gates
[Where we stop and decide whether to proceed]

## Tracker
See `deal-tracker-YYYY-MM-DD.xlsx` for the active tracker.
```

Render PDF:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-pdf.py" \
  "<deal-folder>/reports/deal-process-plan-<DATE>.md" \
  "<deal-folder>/reports/deal-process-plan-<DATE>.pdf"
```

## Phase 6 — Persist workstreams to state

Save the workstreams to `deal-state.yaml` so other skills (checklist, vp-review) can read them:

```bash
# Read the state, append workstreams, write back
python3 - <<PY
import sys
sys.path.insert(0, "$DEALFLOW_ROOT/scripts")
from pathlib import Path
from dealflow_lib import state
state.update_state(Path("<deal-folder>"), {"workstreams": [
    {"name": "QoE", "owner": "...", "status": "Not started", ...},
    ...
]})
PY
```

## Phase 7 — Update mode

When called with `--update`:

1. Read existing workstreams from state
2. Present each to the user: "Status update for [workstream]?"
3. Update tracker Excel (re-write with new status, dates if changed)
4. Re-render PDF
5. Update state

## Update state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-process --report "reports/deal-process-plan-<DATE>.md"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/deal-process-plan-<DATE>.md" --category process --type md \
  --indexed-by dealflow-process --summary "Process plan — N workstreams" \
  --tags "process,plan"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/deal-tracker-<DATE>.xlsx" --category process --type xlsx \
  --indexed-by dealflow-process --summary "Workstream tracker" \
  --tags "process,tracker"
```

## Phase 8 — Hand off

Tell the user:
- Total workstreams
- Critical path
- Earliest decision gate
- Suggested next skill (`/dealflow-checklist` for ongoing tracking, `/dealflow-dataroom` once data room arrives)

## Error handling

| Scenario | Response |
|---|---|
| No config | "Run /dealflow-setup first — process plans differ by deal type." |
| Existing tracker found | "Found existing tracker. Use --update to refresh status, or confirm overwrite." |
| Conflicting dependencies | "Workstream [X] depends on [Y] which ends after [X] starts. Adjust dates?" |
