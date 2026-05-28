---
name: dealflow-checklist
description: Lightweight snapshot of the current state of a deal — what's done, what's open, what's blocked. Reads deal state and index. Designed for daily standups and quick status checks. Cheap to run.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

# Deal Checklist

Quick state-of-the-deal snapshot. Pulls from `.dealflow/deal-state.yaml` and `.dealflow/index.jsonl`. Runs in seconds. Designed to run often.

## Invocation

```
/dealflow-checklist <path-to-deal-folder>
```

## Prerequisites

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
```

State and index should already exist (created by earlier skills). If not, this skill reports the deal as not initialized.

## Phase 1 — Read state and index

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" read "<deal-folder>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" query "<deal-folder>" --limit 1000
```

If state doesn't exist: *"No deal state found. Run /dealflow-prescreen, /dealflow-dataroom, or /dealflow-process first to initialize this deal."*

## Phase 2 — Generate snapshot

Build a markdown snapshot covering:

### Header

```markdown
# <deal-name> — Snapshot — <date>
**Stage:** <stage>
**Opened:** <opened-date> (<days> days ago)
**Last updated:** <last-updated>
```

### Skills run

Table of every skill run with date and report path. Pull from `state.skills_run`.

```markdown
## Skills run

| Skill | Date | Report |
|---|---|---|
| dealflow-prescreen | 2026-05-15 | reports/prescreen-2026-05-15.md |
| dealflow-dataroom | 2026-05-22 | reports/dataroom-assessment-2026-05-22.md |
| ...
```

### Workstreams

If `state.workstreams` is populated (by `/dealflow-process`):

```markdown
## Workstreams

| Workstream | Owner | Status | Target |
|---|---|---|---|
| QoE | Internal | In progress | 2026-06-28 |
| Legal DD | External counsel | Not started | 2026-07-05 |
| ...
```

Group by status (complete / in progress / blocked / not started).

### Materials in deal

From the index, count records by category:

```markdown
## Materials

- Financials: 12 docs
- Legal: 8 docs
- Customer: 4 docs
- Memos: 2 (latest: prescreen 2026-05-15)
- Models: 1
- Analyses: 3
- Reviews: 1 (vp-review 2026-05-24)
- Research: 1
```

### Key decisions

```markdown
## Key decisions

- 2026-05-15: Pursue — passes buy box
- 2026-05-20: LOI issued at $40M pre
```

### Open items

If `state.workstreams` has any in "blocked" or "in progress" with a past target date, list them.

### Stale index records

```bash
# For each indexed file, check is-stale; list any that have changed since indexing
```

If any are stale: *"3 indexed files have changed on disk since their last index pass. Consider re-running /dealflow-dataroom --reindex."*

### Outstanding to-dos

If there are open questions in any memo or review, surface them.

## Phase 3 — Output

Write to `<deal-folder>/reports/checklist-YYYY-MM-DD.md`.

For console: print a tight version to stdout so the user gets a quick read without opening the file.

## Phase 4 — Quick analysis

In one paragraph, tell the user:

- Where the deal is in its lifecycle
- What's overdue
- What should happen next given the stage
- Token-cheap suggestion of next skill to run

Example:
> "Acme Corp is in diligence, 14 days in. QoE and legal DD are in progress; commercial DD hasn't started. 3 data room files have updated since last index. Suggest: /dealflow-dataroom --reindex to refresh, then /dealflow-vp-review to scrub the working memo. Target close in 4 weeks looks achievable."

## Notes

- This skill is read-only on state/index. It does not call `add-skill-run`. The point is to be cheap to run repeatedly without polluting state with checklist runs.
- For users who want a written record, the markdown checklist is saved with a date stamp — they can run multiple times per day.

## Error handling

| Scenario | Response |
|---|---|
| No state | "Initialize the deal first with /dealflow-prescreen, /dealflow-dataroom, or /dealflow-process." |
| Stale index | Surface in output but don't abort. |
